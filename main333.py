import sys
import signal
import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from dotenv import load_dotenv
from src.core.database import Database
from src.services.text_analyzer import TextAnalyzer
from src.services.audio_processor import AudioProcessor

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
        load_dotenv()
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.analyzer = TextAnalyzer()
        self.audio_processor = AudioProcessor()
        self.app = Application.builder().token(self.token).build()
        self.db = None
        self._setup_handlers()
        Path("temp/audio").mkdir(parents=True, exist_ok=True)
        Path("temp/transcripts").mkdir(parents=True, exist_ok=True)

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            status_message = await update.message.reply_text(
                "🎵 Processing your voice message...\n"
                "0% - Downloading..."
            )
            voice_file = await context.bot.get_file(update.message.voice.file_id)
            file_path = f"temp/audio/{update.message.voice.file_id}.ogg"
            await voice_file.download_to_drive(file_path)

            await status_message.edit_text(
                "🎵 Processing your voice message...\n"
                "30% - Transcribing..."
            )
            result = await self.audio_processor.process_voice_message(file_path)

            if "error" in result:
                await status_message.edit_text(
                    f"❌ Sorry, I couldn't process your voice message: {result['error']}"
                )
                return

            await status_message.edit_text(
                "🎵 Processing your voice message...\n"
                "60% - Analyzing content..."
            )
            analysis = await self.analyzer.analyze_text(result["transcript"])

            if self.db:
                await self.db.conversations.insert_one({
                    "user_id": update.effective_user.id,
                    "audio_file_id": update.message.voice.file_id,
                    "transcript": result["transcript"],
                    "analysis": analysis,
                    "audio_metrics": {
                        "duration": result["duration_seconds"],
                        "sample_rate": result["frame_rate"],
                        "channels": result["channels"]
                    },
                    "timestamp": datetime.now()
                })

            response = (
                "🎤 *Voice Message Analysis*\n\n"
                f"*Duration*: {result['duration_seconds']:.1f} seconds\n\n"
                f"*Transcript*:\n{result['transcript']}\n\n"
                f"*Sentiment*: {analysis.get('sentiment', {}).get('label', 'N/A')}\n"
                f"*Confidence*: {analysis.get('sentiment', {}).get('score', 0):.2%}\n\n"
                "*Suggestions*:\n" +
                "\n".join([f"• {s}" for s in analysis.get('suggestions', ['No suggestions available.'])])
            )

            await status_message.edit_text(response, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error processing voice message: {str(e)}", exc_info=True)
            if 'status_message' in locals():
                await status_message.edit_text(
                    "❌ Sorry, I encountered an error while processing your voice message.\n"
                    "Please try again later."
                )
            else:
                await update.message.reply_text(
                    "❌ Sorry, I encountered an error while processing your voice message.\n"
                    "Please try again later."
                )
        finally:
            try:
                if 'file_path' in locals() and os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temporary file: {str(e)}")

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        if self.db:
            await self.db.users.update_one(
                {"telegram_id": user.id},
                {
                    "$set": {
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "last_active": datetime.now()
                    }
                },
                upsert=True
            )

        keyboard = [
            [
                InlineKeyboardButton("Start Analysis", callback_data='start_analysis'),
                InlineKeyboardButton("View Dashboard", callback_data='view_dashboard')
            ],
            [InlineKeyboardButton("Record Call", callback_data='record_call')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_html(
            f"Hi {user.mention_html()}! 👋\n\n"
            "Welcome to Dialmate - Your AI-Powered Call Co-pilot! 🤖\n\n"
            "I can help you:\n"
            "🎯 Analyze conversations\n"
            "🌍 Translate in real-time\n"
            "📊 Track relationship metrics\n"
            "🔍 Identify communication patterns\n\n"
            "Use /help to see available commands.",
            reply_markup=reply_markup
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
🤖 *Available Commands*:

/start - Begin using Dialmate
/help - Show this help message
/profile - View your profile
/record - Start recording
/analyze - Analyze conversation
/dashboard - View analytics
/settings - Configure preferences

*Features*:
• Voice message analysis
• Real-time translation
• Relationship metrics
• Communication patterns
• Interactive dashboard

Need help? Contact @support
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def profile(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if self.db:
            user_data = await self.db.users.find_one({"telegram_id": update.effective_user.id})
            if user_data:
                profile_text = (
                    "👤 *Your Profile*\n\n"
                    f"Name: {user_data.get('first_name', 'N/A')} {user_data.get('last_name', '')}\n"
                    f"Username: @{user_data.get('username', 'N/A')}\n"
                    f"Member Since: {user_data.get('last_active', 'N/A')}"
                )
                await update.message.reply_text(profile_text, parse_mode='Markdown')
            else:
                await update.message.reply_text("Profile not found. Please use /start to register.")

    async def record(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🎙 *Voice Recording*\n\n"
            "To analyze a conversation:\n"
            "1. Send a voice message\n"
            "2. Forward a voice message\n"
            "3. Share call recording\n\n"
            "I'll analyze it and provide insights!",
            parse_mode='Markdown'
        )

    async def analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📊 *Analysis*\n\n"
            "Send me text or voice messages to analyze.\n"
            "I'll provide insights about:\n"
            "• Communication patterns\n"
            "• Sentiment analysis\n"
            "• Relationship indicators",
            parse_mode='Markdown'
        )

    async def dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton("Communication Stats", callback_data='comm_stats'),
                InlineKeyboardButton("Relationship Metrics", callback_data='rel_metrics')
            ],
            [InlineKeyboardButton("View Full Dashboard", callback_data='full_dashboard')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "📊 *Your Analytics Dashboard*\n\n"
            "Choose what you'd like to view:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [
                InlineKeyboardButton("Language", callback_data='settings_language'),
                InlineKeyboardButton("Notifications", callback_data='settings_notifications')
            ],
            [
                InlineKeyboardButton("Privacy", callback_data='settings_privacy'),
                InlineKeyboardButton("Help", callback_data='settings_help')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "⚙️ *Settings*\n\n"
            "Configure your Dialmate experience:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            text = update.message.text
            analysis = await self.analyzer.analyze_text(text)

            if self.db:
                await self.db.conversations.insert_one({
                    "user_id": update.effective_user.id,
                    "text": text,
                    "analysis": analysis,
                    "timestamp": datetime.now()
                })

            response = self._format_analysis_results(analysis)
            await update.message.reply_text(response, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            await self.send_error_message(update)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        try:
            if query.data == 'start_analysis':
                await query.message.reply_text(
                    "Send me any text or voice message to analyze!"
                )
            elif query.data == 'view_dashboard':
                await self.dashboard(update, context)
            elif query.data == 'record_call':
                await self.record(update, context)
            else:
                await query.message.reply_text(
                    "This feature is coming soon!"
                )
        except Exception as e:
            logger.error(f"Error handling callback: {str(e)}")
            await self.send_error_message(update)

    def _setup_handlers(self):
        handlers = [
            CommandHandler("start", self.handle_error(self.start)),
            CommandHandler("help", self.handle_error(self.help)),
            CommandHandler("profile", self.handle_error(self.profile)),
            CommandHandler("record", self.handle_error(self.record)),
            CommandHandler("analyze", self.handle_error(self.analyze)),
            CommandHandler("dashboard", self.handle_error(self.dashboard)),
            CommandHandler("settings", self.handle_error(self.settings)),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_error(self.handle_message)),
            MessageHandler(filters.VOICE | filters.AUDIO, self.handle_error(self.handle_voice)),
            CallbackQueryHandler(self.handle_error(self.handle_callback))
        ]

        for handler in handlers:
            self.app.add_handler(handler)

        self.app.add_error_handler(self.error_handler)

    def handle_error(self, func):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                return await func(update, context)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                await self.send_error_message(update)
        return wrapper

    async def send_error_message(self, update: Update):
        error_message = (
            "😔 Sorry, I encountered an error while processing your request.\n"
            "Please try again later or contact support if the issue persists."
        )

        if update.callback_query:
            await update.callback_query.message.reply_text(error_message)
        else:
            await update.message.reply_text(error_message)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)
        await self.send_error_message(update)

    def _format_analysis_results(self, analysis: dict) -> str:
        return (
            "📊 *Analysis Results*\n\n"
            f"*Sentiment*: {analysis.get('sentiment', {}).get('label', 'N/A')}\n"
            f"*Confidence*: {analysis.get('sentiment', {}).get('score', 0):.2%}\n\n"
            "*Suggestions*:\n" +
            "\n".join([f"• {s}" for s in analysis.get('suggestions', ['No suggestions available.'])])
        )

    def _format_voice_analysis(self, transcript: str, analysis: Dict) -> str:
        return (
            "🎤 *Voice Message Analysis*\n\n"
            f"*Transcript*:\n{transcript}\n\n"
            f"*Sentiment*: {analysis.get('sentiment', {}).get('label', 'N/A')}\n"
            f"*Confidence*: {analysis.get('sentiment', {}).get('score', 0):.2%}\n\n"
            "*Communication Patterns*:\n" +
            "\n".join([f"• {k}: {v}" for k, v in analysis.get('communication_patterns', {}).items()]) +
            "\n\n*Suggestions*:\n" +
            "\n".join([f"• {s}" for s in analysis.get('suggestions', [])])
        )

    async def init_db(self):
        try:
            self.db = await Database.connect_db()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            self.db = None

    def run(self):
        async def start_bot():
            try:
                await self.init_db()
                logger.info("Starting bot polling...")
                await self.app.run_polling(allowed_updates=Update.ALL_TYPES)
            except Exception as e:
                logger.error(f"Error in start_bot: {str(e)}", exc_info=True)
                raise
            finally:
                logger.info("Stopping bot...")
                await self.app.stop()
                await self.app.shutdown()

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(start_bot())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.critical(f"Bot crashed: {str(e)}", exc_info=True)
            raise
        finally:
            try:
                loop.close()
            except Exception as e:
                logger.error(f"Error closing event loop: {str(e)}")

def main():
    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, lambda s, f: sys.exit(0))
        bot = DialmateBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Bot crashed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()