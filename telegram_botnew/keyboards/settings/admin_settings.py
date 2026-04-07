from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


ADMIN_MENU_MSG=(
    "PANNELLO ADMIN"
)

async def admin_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Genera Licenza", callback_data='generate_license')],
        [InlineKeyboardButton("Vedi Licenze", callback_data='license_0')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data='settings')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=ADMIN_MENU_MSG,
        parse_mode="HTML", 
        reply_markup=reply_markup
    )