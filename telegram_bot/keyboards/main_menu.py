from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram_bot.messages.messages_it import get_benvenuto

async def create_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user = update.effective_user
    user_link = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Cerca prodotto", callback_data='search_product')],
        [InlineKeyboardButton("🛒 Offerte Canale", callback_data='offerte_canale')],
        [InlineKeyboardButton("⚙️ Impostazioni", callback_data='settings')]
    ])

    if update.message:
        await update.message.reply_text(
            text=get_benvenuto(user_link),
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            text=get_benvenuto(user_link),
            parse_mode="HTML",
            reply_markup=reply_markup
        )