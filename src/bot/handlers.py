# src/bot/handlers.py
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from dialmateai.dialmate.src.models.user_profile import User
from datetime import datetime

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🤖 *Dialmate Bot Commands*

/start - Begin registration and assessment
/profile - View your profile and settings
/record - Start call recording
/analyze - Get analysis of recent calls
/dashboard - View your analytics
/help - Show this help message

Need assistance? Contact @thedigitalmindmeldpodcast
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await User.find_one({"telegram_id": update.effective_user.id})

    if user:
        welcome_back = f"""
Welcome back to Dialmate! 👋

Your profile is already set up. Use /help to see available commands.
"""
        await update.message.reply_text(welcome_back)
        return

    welcome_message = """
Welcome to Dialmate! 🎉

I'm your AI-powered call co-pilot for better relationships. Let's get started with a quick personality assessment to personalize your experience.

Are you ready to begin?
"""
    keyboard = [
        [InlineKeyboardButton("Yes, let's start! 🚀", callback_data="start_assessment")],
        [InlineKeyboardButton("Tell me more ℹ️", callback_data="more_info")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await User.find_one({"telegram_id": update.effective_user.id})

    if not user:
        await update.message.reply_text(
            "Please use /start to create your profile first!"
        )
        return

    profile_text = f"""
📊 *Your Dialmate Profile*

Username: @{user.username}
Member since: {user.created_at.strftime('%Y-%m-%d')}

*Personality Traits:*
"""
    if user.personality_traits:
        for trait, score in user.personality_traits.items():
            profile_text += f"\n• {trait.title()}: {'⭐' * int(score)}"
    else:
        profile_text += "\nPersonality assessment not completed. Use /start to take the assessment."

    keyboard = [
        [InlineKeyboardButton("Update Profile 🔄", callback_data="update_profile")],
        [InlineKeyboardButton("View Analytics 📈", callback_data="view_analytics")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(profile_text, reply_markup=reply_markup, parse_mode='Markdown')

async def record_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This is a placeholder - actual implementation will need device permissions
    recording_info = """
🎙️ *Call Recording*

To start recording calls:
1. Grant necessary permissions
2. Select call type to record
3. Start your conversation

*Note:* Please ensure you have consent from all parties before recording.
"""
    keyboard = [
        [InlineKeyboardButton("Grant Permissions 🔐", callback_data="grant_permissions")],
        [InlineKeyboardButton("Start Recording 🔴", callback_data="start_recording")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(recording_info, reply_markup=reply_markup, parse_mode='Markdown')
async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages"""
    try:
        # Inform user that analysis is starting
        processing_message = await update.message.reply_text(
            "🔄 Processing your message..."
        )

        # Perform text analysis
        analysis_result = await self.text_analyzer.analyze_text(update.message.text)

        # Format and send results
        response = self.format_analysis_results(analysis_result)
        await processing_message.edit_text(response, parse_mode='HTML')

        # Store conversation in database
        await self.store_conversation(update.effective_user.id,
                                   update.message.text,
                                   analysis_result)

    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        await self.send_error_message(update)

async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages"""
    try:
        # Inform user that processing is starting
        processing_message = await update.message.reply_text(
            "🎵 Processing your voice message..."
        )

        # Get voice file
        voice_file = await context.bot.get_file(update.message.voice.file_id)

        # Download and process voice file
        # This is a placeholder - implement actual audio processing
        transcribed_text = await self.process_voice_message(voice_file)

        # Analyze transcribed text
        analysis_result = await self.text_analyzer.analyze_text(transcribed_text)

        # Format and send results
        response = self.format_analysis_results(analysis_result)
        await processing_message.edit_text(response, parse_mode='HTML')

    except Exception as e:
        logging.error(f"Error processing voice message: {str(e)}")
        await self.send_error_message(update)
        
async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    analysis_info = """
🔍 *Call Analysis*

Select what you'd like to analyze:
"""
    keyboard = [
        [InlineKeyboardButton("Recent Calls 📞", callback_data="analyze_recent")],
        [InlineKeyboardButton("Specific Conversation 💭", callback_data="analyze_specific")],
        [InlineKeyboardButton("Overall Trends 📈", callback_data="analyze_trends")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(analysis_info, reply_markup=reply_markup, parse_mode='Markdown')


def format_analysis_results(self, analysis: Dict) -> str:
    """Format analysis results for Telegram message"""
    return (
        "📊 <b>Analysis Results</b>\n\n"
        f"Sentiment: {analysis['sentiment']['label']}\n"
        f"Score: {analysis['sentiment']['score']:.2f}\n\n"
        "<b>Communication Patterns:</b>\n"
        f"Questions: {analysis['communication_patterns']['questions_asked']}\n"
        f"Exclamations: {analysis['communication_patterns']['exclamations_used']}\n\n"
        "<b>Suggestions:</b>\n" +
        "\n".join(f"• {suggestion}" for suggestion in analysis['suggestions'])
    )

async def send_error_message(self, update: Update):
    """Send error message to user"""
    await update.message.reply_text(
        "Sorry, I encountered an error processing your request. Please try again later."
    )

async def get_or_create_user(self, tg_user) -> User:
    """Get or create user in database"""
    # Implement user database operations here
    pass

async def store_conversation(self, user_id: int, text: str, analysis: Dict):
    """Store conversation and analysis in database"""
    # Implement conversation storage here
    pass

async def dashboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dashboard_link = "https://your-dashboard-url.com"  # Replace with actual dashboard URL

    dashboard_info = """
📊 *Dialmate Dashboard*

Access your personal dashboard to view:
• Communication patterns
• Relationship insights
• Progress tracking
• Detailed analytics
"""
    keyboard = [
        [InlineKeyboardButton("Open Dashboard 🔗", url=dashboard_link)],
        [InlineKeyboardButton("Download Report 📥", callback_data="download_report")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(dashboard_info, reply_markup=reply_markup, parse_mode='Markdown')

# main.py
import asyncio
from telegram.ext import Application
from src.core.config import settings
from src.core.database import init_db

async def main():
    # Initialize database
    await init_db()

    # Initialize bot
    application = Application.builder().token("7779193710:AAGNCIaMyURhGwerx6wTc_dUUDMfzNDLjyk").build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("record", record_command))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(CommandHandler("dashboard", dashboard_command))

    # Start bot
    print("Bot started...")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())