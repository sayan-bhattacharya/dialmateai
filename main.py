import logging
import os
import signal
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from dotenv import load_dotenv

from src.services.text_analyzer import TextAnalyzer
from src.services.audio_processor import AudioProcessor
from src.core.database import Database

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DialmateBot:
    def __init__(self):
        """Initialize bot components"""
        load_dotenv()
        self.token = os.getenv('TELEGRAM_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_TOKEN not found in environment variables")

        # Initialize components
        self.analyzer = TextAnalyzer()
        self.audio_processor = AudioProcessor()
        self.db = None

        # Create directories
        Path("temp/audio").mkdir(parents=True, exist_ok=True)
        Path("temp/transcripts").mkdir(parents=True, exist_ok=True)

        # Create application
        self.app = Application.builder().token(self.token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up message and command handlers"""
        handlers = [
            CommandHandler("start", self.start),
            CommandHandler("help", self.help),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message),
            MessageHandler(filters.VOICE, self.handle_voice),
            CallbackQueryHandler(self.handle_callback)
        ]

        for handler in handlers:
            self.app.add_handler(handler)

        self.app.add_error_handler(self.error_handler)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        keyboard = [
            [
                InlineKeyboardButton("Start Analysis", callback_data='start_analysis'),
                InlineKeyboardButton("Help", callback_data='help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Welcome to Dialmate! I'm your AI-powered communication assistant.",
            reply_markup=reply_markup
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "Available commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "\nYou can also send me:\n"
            "• Text messages for analysis\n"
            "• Voice messages for transcription and analysis"
        )
        await update.message.reply_text(help_text)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with enhanced analysis"""
        try:
            text = update.message.text
            analysis = await self.analyzer.analyze_text(text)

            # Store in database if available
            if self.db:
                await self.db.conversations.insert_one({
                    "user_id": update.effective_user.id,
                    "text": text,
                    "analysis": analysis,
                    "timestamp": datetime.now()
                })

            # Enhanced response formatting
            sentiment = analysis.get('sentiment', {})
            sentiment_label = sentiment.get('label', 'N/A')
            confidence = sentiment.get('score', 0)

            # Create emoji based on sentiment
            emoji = "😊" if sentiment_label.lower() == 'positive' else "😔" if sentiment_label.lower() == 'negative' else "😐"

            response = (
                f"*Analysis Results* {emoji}\n\n"
                f"*Text*: `{text[:50]}...`\n"
                f"*Sentiment*: {sentiment_label}\n"
                f"*Confidence*: {confidence:.2%}\n\n"
                "Would you like to:\n"
                "1. Get detailed analysis\n"
                "2. Try another message\n"
                "3. Get help"
            )

            # Create inline keyboard
            keyboard = [
                [
                    InlineKeyboardButton("Detailed Analysis", callback_data='detailed_analysis'),
                    InlineKeyboardButton("New Message", callback_data='new_message')
                ],
                [InlineKeyboardButton("Help", callback_data='help')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                response,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await update.message.reply_text(
                "Sorry, I couldn't process your message. Please try again."
            )

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        try:
            await update.message.reply_text("Voice message received. Processing...")
        except Exception as e:
            logger.error(f"Error handling voice message: {str(e)}")
            await update.message.reply_text("Sorry, I couldn't process your voice message.")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries with enhanced options"""
        query = update.callback_query
        await query.answer()

        if query.data == 'start_analysis':
            await query.message.reply_text(
                "Send me any text message to analyze its sentiment!"
            )

        elif query.data == 'detailed_analysis':
            # Get the original message from context if available
            original_text = query.message.reply_to_message.text if query.message.reply_to_message else "No text available"
            analysis = await self.analyzer.analyze_text(original_text)

            detailed_response = (
                "*Detailed Analysis*\n\n"
                f"*Original Text*: `{original_text[:100]}`\n\n"
                f"*Primary Sentiment*: {analysis.get('sentiment', {}).get('label', 'N/A')}\n"
                f"*Confidence Score*: {analysis.get('sentiment', {}).get('score', 0):.2%}\n"
                f"*Text Length*: {len(original_text)} characters\n"
                "*Analysis Time*: Just now\n\n"
                "💡 *Tip*: Try sending different types of messages to see how the analysis varies!"
            )

            await query.message.reply_text(
                detailed_response,
                parse_mode='Markdown'
            )

        elif query.data == 'new_message':
            await query.message.reply_text(
                "I'm ready for a new message! Send me any text to analyze."
            )

        elif query.data == 'help':
            await self.help(update, context)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, something went wrong. Please try again later."
            )

    async def pre_run(self):
        """Initialize database before running"""
        try:
            self.db = await Database.connect_db()
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

def main():
    """Main entry point"""
    try:
        # Set up signal handlers
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda s, f: sys.exit(0))

        # Create bot instance
        bot = DialmateBot()

        # Run the application
        app = bot.app

        # Add pre-run hook
        app.pre_run = bot.pre_run

        # Run the application
        app.run_polling(allowed_updates=Update.ALL_TYPES)

    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()