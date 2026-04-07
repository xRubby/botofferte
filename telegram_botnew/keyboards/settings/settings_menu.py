from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

SETTINGS_MSG=(
        "<b>⚙️ Impostazioni</b>"
        "\n\n"
        "<b>IN LAVORAZIONE</b> 🏗️"
    )

async def settings_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        keyboard = []

        keyboard.append([InlineKeyboardButton("Pannello admin", callback_data='admin_settings')])

        keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data='back_to_main')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=SETTINGS_MSG, 
            parse_mode="HTML", 
            reply_markup=reply_markup,
        )