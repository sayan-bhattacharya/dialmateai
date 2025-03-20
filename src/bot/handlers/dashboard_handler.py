# src/bot/handlers/dashboard_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import matplotlib.pyplot as plt
import io

class DashboardHandler:
    async def handle_dashboard_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        profile = await self.get_user_profile(user_id)

        # Create visualization
        fig = plt.figure(figsize=(12, 8))

        # Big Five Traits Plot
        plt.subplot(2, 2, 1)
        self._plot_big_five(profile.big_five_traits)

        # IQ Progress Plot
        plt.subplot(2, 2, 2)
        self._plot_iq_progress(profile.iq_history)

        # Conversation Analytics
        plt.subplot(2, 2, 3)
        self._plot_conversation_metrics(profile.conversation_history)

        # Save plot to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Send dashboard to user
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=buf,
            caption="Your Personal Analytics Dashboard"
        )