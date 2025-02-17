from telegram import *
from telegram.ext import *

from database.DAO.GestisceDAO import GestisceDAO

async def insert_affiliate_id(query, context, user_id, channel_id):

    await query.answer()

    with GestisceDAO() as gestisce_dao:
        gestisce_info = gestisce_dao.get(user_id, channel_id)

    message_id = query.message.id
    context.user_data[user_id] = {'awaiting_affiliate_id': True, 'message_id': message_id, 'channel_id': channel_id}
    

    id_affiliato = gestisce_info.id_affiliato if gestisce_info.id_affiliato else "Nessuno"

    text = f"Inserisci l'ID affiliato che verrà utilizzato al posto dell'ID memorizzato nel canale.\n\nID corrente: {id_affiliato}"

    keyboard = [
        [InlineKeyboardButton("Rimuovi ID Affiliato", callback_data=f'channel_removeaffiliateid_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )

async def remove_affiliate_id(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, channel_id: str, user_id: int):
    
    if context.user_data[user_id].get('awaiting_affiliate_id'):
        context.user_data[user_id]['awaiting_admin_affiliate_id'] = False

    with GestisceDAO() as gestisce_dao:     
        gestisce_dao.update_id_affiliato(user_id, channel_id, "")
    
    text = "ID Affiliato rimosso con successo!"

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )