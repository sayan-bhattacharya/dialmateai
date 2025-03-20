# src/bot/handlers/assessment_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

class AssessmentHandler:
    def __init__(self, personality_assessment: PersonalityAssessment, iq_assessment: IQAssessment):
        self.personality_assessment = personality_assessment
        self.iq_assessment = iq_assessment

    async def start_assessment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the assessment process"""
        user_id = update.effective_user.id

        keyboard = [
            [
                InlineKeyboardButton("Personality Assessment", callback_data='start_personality'),
                InlineKeyboardButton("IQ Assessment", callback_data='start_iq')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Welcome to the assessment center! Choose what you'd like to start with:",
            reply_markup=reply_markup
        )

    async def handle_assessment_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle responses to assessment questions"""
        query = update.callback_query
        user_id = query.from_user.id

        # Process response and get next question or results
        if query.data.startswith('personality_'):
            response = int(query.data.split('_')[1])
            result = await self.personality_assessment.process_response(user_id, context.user_data['current_question'], response)

            if result.get("status") == "complete":
                await self._show_personality_results(update, context, result)
            else:
                await self._send_next_personality_question(update, context)