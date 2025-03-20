# main.py
import logging
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv

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

        self.active_conversations = {}
        self.user_data = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_message = (
            f"👋 Hello {user.first_name}!\n\n"
            "I'm Dialmate, your AI-powered conversation analyzer. "
            "I can help you understand communication patterns and relationships "
            "in your chats.\n\n"
            "Here's what I can do:\n"
            "• Analyze conversations in real-time\n"
            "• Track relationship dynamics\n"
            "• Generate cognitive profiles\n"
            "• Provide communication insights"
        )

        keyboard = [
            [
                InlineKeyboardButton("Start Analysis", callback_data='start_analysis'),
                InlineKeyboardButton("View Profile", callback_data='view_profile')
            ],
            [
                InlineKeyboardButton("Help", callback_data='help'),
                InlineKeyboardButton("Settings", callback_data='settings')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "*Available Commands*:\n\n"
            "📝 *Basic Commands*:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/analyze - Start conversation analysis\n"
            "/profile - View your profile\n"
            "/settings - Configure preferences\n\n"
            "💡 *Tips*:\n"
            "• Send messages to analyze communication\n"
            "• Use buttons for quick actions\n"
            "• Check your profile for insights"
        )

        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages"""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text
            chat_id = update.effective_chat.id

            # Basic message analysis
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'chat_id': chat_id,
                'message_length': len(message_text),
                'word_count': len(message_text.split())
            }

            # Store analysis
            if chat_id not in self.active_conversations:
                self.active_conversations[chat_id] = []
            self.active_conversations[chat_id].append(analysis)

            # Generate response
            response_text = (
                "📊 *Message Analysis*\n\n"
                f"Words: {analysis['word_count']}\n"
                f"Characters: {analysis['message_length']}\n\n"
                "Choose an option for more insights:"
            )

            keyboard = [
                [
                    InlineKeyboardButton("Detailed Analysis", callback_data='detailed_analysis'),
                    InlineKeyboardButton("View Stats", callback_data='view_stats')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                response_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error in handle_message: {str(e)}")
            await update.message.reply_text(
                "Sorry, I encountered an error while processing your message."
            )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()

        if query.data == 'start_analysis':
            await query.edit_message_text(
                "🔍 Analysis mode activated! Send messages to analyze them."
            )
        elif query.data == 'view_profile':
            await query.edit_message_text(
                "👤 *Your Profile*\n\n"
                "Analysis will be available after processing more messages.",
                parse_mode='Markdown'
            )
        elif query.data == 'help':
            await self.help(update, context)
        elif query.data == 'settings':
            await query.edit_message_text(
                "⚙️ *Settings*\n\n"
                "Configuration options will be available soon.",
                parse_mode='Markdown'
            )

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Error occurred: {context.error}")
        if update:
            await update.message.reply_text(
                "Sorry, an error occurred. Please try again later."
            )

    def run(self):
        """Run the bot"""
        # Create application
        application = Application.builder().token(self.token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_error_handler(self.error_handler)

        # Start the bot
        logger.info("Starting bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function"""
    try:
        # Create and run bot
        bot = DialmateBot()
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)

if __name__ == '__main__':
    main()