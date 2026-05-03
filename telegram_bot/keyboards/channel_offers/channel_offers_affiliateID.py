from telegram import *
from telegram.ext import *

from database.DAO.GestisceDAO import GestisceDAO
from telegram_bot.keyboards.channel_offers.channels_offers_info import channel_info
from utils.channel_offers_utils import check_channel_id

ATTESA_ID_AFFILIATO = range(1)

async def insert_affiliate_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    user_id = update.effective_user.id

    id_affiliato = "Nessuno"

    with GestisceDAO() as gestisceDAO:
        gestisce_info = gestisceDAO.get(user_id, channel_id)

    if gestisce_info and gestisce_info.id_affiliato:
        id_affiliato = gestisce_info.id_affiliato

    text = f"Inserisci l'ID affiliato che verrà utilizzato al posto dell'ID memorizzato nel canale.\n\nID corrente: {id_affiliato}"

    keyboard = [
        [InlineKeyboardButton("Rimuovi ID Affiliato", callback_data=f'channel_removeaffiliateid_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_info_{channel_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )

    context.user_data["msg_id"] = msg.message_id
    context.user_data["channel_id"] = channel_id

    return ATTESA_ID_AFFILIATO

async def remove_affiliate_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    channel_id = check_channel_id(query, context)
    user_id = update.effective_user.id

    try:
        with GestisceDAO() as gestisce_dao:     
            gestisce_dao.update_idaffiliato(user_id, channel_id, "")
        
        text = "ID Affiliato rimosso con successo!"
    except Exception as e:
        text = f"Errore durante la rimozione dell'ID Affiliato..."

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_affiliateid_{channel_id}')]
    ])

    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard
    )

    return ConversationHandler.END

async def ricevi_affiliate_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    message_id = context.user_data.get("msg_id")
    channel_id = context.user_data.get('channel_id')
    affiliate_id = update.message.text
    user_id = update.effective_user.id

    await update.message.delete()
    try:
        with GestisceDAO() as gestisceDAO:
            gestisceDAO.update_idaffiliato(user_id, channel_id, affiliate_id)

        text = f"ID Affiliato aggiornato in: <b>{affiliate_id}</b>"
    except Exception as e:
        text = f"Errore durante l'aggiornamento dell'ID Affiliato..."

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_affiliateid_{channel_id}')]
    ])

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        text=text,
        message_id=message_id,
        parse_mode="HTML",
        reply_markup=keyboard
    )

    return ConversationHandler.END

async def annulla_insert_affiliateid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.pop("msg_id", None)
    context.user_data.pop("channel_id", None)

    await channel_info(update, context)
    return ConversationHandler.END

conv_insert_affiliateID = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(insert_affiliate_id, pattern=r'^channeloffers_affiliateid_.+$')
    ],
    states={
        ATTESA_ID_AFFILIATO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_affiliate_id),
            CallbackQueryHandler(remove_affiliate_id, pattern=r'^channel_removeaffiliateid_-?\d+$'),
            CallbackQueryHandler(annulla_insert_affiliateid, pattern=r'^channeloffers_info_-?\d+$'),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(annulla_insert_affiliateid, pattern=r'^channeloffers_info_-?\d+$')
    ],
    per_message=False,
    per_chat=True,
)