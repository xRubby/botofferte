from telegram import *
from telegram.ext import *

from telegram_bot.messages.messages_it import *


async def search_product(query, context, user_id):
    user_id = query.from_user.id
    message_id = query.message.id

    context.user_data[user_id] = {'awaiting_input': True, 'message_id': message_id}

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Indietro", callback_data='back_to_main')]
    ])

    await query.edit_message_text(text=get_cerca_prodotto(),parse_mode="HTML", reply_markup=reply_markup)