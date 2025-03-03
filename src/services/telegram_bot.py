# src/services/telegram_bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import logging
from src.core.database import Database
from src.services.text_analyzer import TextAnalyzer
import asyncio
import json

class DialmateBot:
    def __init__(self, token: str):
        self.token = token
        self.analyzer = TextAnalyzer()
        self.app = Application.builder().token(self.token).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Set up message handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("analyze", self.analyze_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self.handle_voice))
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        db = Database.get_database()
        if db:
            # Store user info
            await db.users.update_one(
                {"telegram_id": update.effective_user.id},
                {
                    "$set": {
                        "username": update.effective_user.username,
                        "first_name": update.effective_user.first_name,
                        "last_name": update.effective_user.last_name,
                        "last_active": update.message.date
                    }
                },
                upsert=True
            )

        keyboard = [
            [InlineKeyboardButton("Start Analysis", callback_data='start_analysis')],
            [InlineKeyboardButton("View Dashboard", callback_data='view_dashboard')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        welcome_text = (
            "🤖 Welcome to Dialmate - Your AI-Powered Call Co-pilot!\n\n"
            "I can help you:\n"
            "📱 Analyze conversations\n"
            "🎯 Provide relationship insights\n"
            "🔍 Identify communication patterns\n"
            "📊 Show interactive analytics\n\n"
            "Send me any message to get started!"
        )

        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🔍 *Dialmate Commands*\n\n"
            "/start - Start the bot\n"
            "/analyze - Analyze recent conversations\n"
            "/help - Show this help message\n\n"
            "*Features*:\n"
            "• Send text messages for instant analysis\n"
            "• Send voice messages for transcription and analysis\n"
            "• View relationship insights and metrics\n"
            "• Access interactive dashboard\n"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def analyze_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analyze command"""
        db = Database.get_database()
        if db:
            # Fetch recent conversations
            recent_convos = await db.conversations.find(
                {"user_id": update.effective_user.id}
            ).sort("timestamp", -1).limit(5).to_list(length=5)

            if not recent_convos:
                await update.message.reply_text(
                    "No recent conversations found. Start chatting to get insights!"
                )
                return

            # Analyze conversations
            analysis_results = []
            for convo in recent_convos:
                analysis = await self.analyzer.analyze_text(convo['text'])
                analysis_results.append(analysis)

            # Format and send results
            summary = self._format_analysis_results(analysis_results)
            await update.message.reply_text(summary, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming text messages"""
        try:
            # Store message in DB
            db = Database.get_database()
            if db:
                await db.conversations.insert_one({
                    "user_id": update.effective_user.id,
                    "text": update.message.text,
                    "timestamp": update.message.date
                })

            # Analyze message
            analysis = await self.analyzer.analyze_text(update.message.text)

            # Format and send response
            response = self._format_single_analysis(analysis)
            await update.message.reply_text(response, parse_mode='Markdown')

        except Exception as e:
            logging.error(f"Error handling message: {e}")
            await update.message.reply_text(
                "Sorry, I encountered an error while processing your message."
            )

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        await update.message.reply_text(
            "🎵 Voice message received! Processing...\n"
            "This feature is coming soon!"
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()

        if query.data == 'start_analysis':
            await query.message.reply_text(
                "Send me a message to analyze, or use /analyze to see insights from recent conversations!"
            )
        elif query.data == 'view_dashboard':
            await query.message.reply_text(
                "🔗 Access your personal dashboard here: [Dashboard Link]\n"
                "(Dashboard integration coming soon!)"
            )

    def _format_single_analysis(self, analysis: dict) -> str:
        """Format single message analysis results"""
        return (
            "📊 *Analysis Results*\n\n"
            f"*Sentiment*: {analysis.get('sentiment', {}).get('label', 'N/A')}\n"
            f"*Confidence*: {analysis.get('sentiment', {}).get('score', 0):.2%}\n\n"
            "*Communication Patterns*:\n"
            f"• Questions: {analysis.get('communication_patterns', {}).get('questions_asked', 0)}\n"
            f"• Exclamations: {analysis.get('communication_patterns', {}).get('exclamations_used', 0)}\n\n"
            "*Relationship Indicators*:\n"
            f"• Positive Language: {analysis.get('relationship_indicators', {}).get('positive_language', 0)}\n"
            f"• Collaborative Terms: {analysis.get('relationship_indicators', {}).get('collaborative_terms', 0)}\n\n"
            "*Suggestions*:\n" +
            "\n".join([f"• {s}" for s in analysis.get('suggestions', [])] or ["No suggestions at this time."])
        )

    def run(self):
        """Run the bot"""
        self.app.run_polling()