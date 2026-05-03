from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database.DAO.GestisceDAO import GestisceDAO
from utils.channel_offers_utils import check_channel_id

async def channel_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    text = "Benvenuto nelle impostazioni di questo canale!"

    keyboard = [
        [InlineKeyboardButton("Esci dal canale", callback_data=f'channeloffers_exitchannel_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_info_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def exit_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    text = "Sei sicuro di voler uscire da questo canale?"

    keyboard = [
        [InlineKeyboardButton("✅ Conferma", callback_data=f'channeloffers_exitchannelconfirm_{channel_id}'), InlineKeyboardButton("❌ Annulla", callback_data=f'channeloffers_settings_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def exit_channel_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    user_id = update.effective_user.id

    keyboard = [
        [InlineKeyboardButton("🏠 Home", callback_data=f'back_to_main')]
    ]

    with GestisceDAO() as gestisceDAO:
        gestisce = gestisceDAO.get(user_id, channel_id)
        if gestisce and not gestisce.isCreator:
            gestisceDAO.delete(user_id, channel_id)
            text = "Sei stato rimosso dal canale!"
        elif gestisce.isCreator:
            text = "Non puoi essere rimosso dal canale in quanto sei il creatore!"
            keyboard = [
                [InlineKeyboardButton("Indietro", callback_data=f'channeloffers_settings_{channel_id}')]
            ]
        else:
            text = "Errore nella rimozione dal canale"

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
