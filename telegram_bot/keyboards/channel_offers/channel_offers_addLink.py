from telegram import *
from telegram.ext import *

async def insert_link(query, context, user_id, channel_id):

    await query.answer()

    message_id = query.message.id
    context.user_data[user_id] = {'awaiting_link': True, 'message_id': message_id, 'channel_id': channel_id}
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Inserisci il link di Amazon:",
        reply_markup=reply_markup
    )