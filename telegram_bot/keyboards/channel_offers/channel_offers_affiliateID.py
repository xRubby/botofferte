from telegram import *
from telegram.ext import *

from database.DAO.CanaleDAO import get_affiliate_id

async def insert_affiliate_id(query, context, user_id, channel_id):
    message_id = query.message.id
    context.user_data[user_id] = {'awaiting_affiliate_id': True, 'message_id': message_id, 'channel_id': channel_id}
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Inserisci l'ID dell'affiliato di Amazon:\n\n"
             f"ID corrente: <b>{get_affiliate_id(channel_id)}</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )