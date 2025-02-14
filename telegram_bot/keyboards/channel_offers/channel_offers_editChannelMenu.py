from telegram import *
from telegram.ext import *

from database.DAO.CanaleDAO import *

async def edit_channel(query, channel_id):

    nome_canale = get_channel(channel_id).get_nome_canale()

    keyboard = [
        [InlineKeyboardButton("➕ Inserisci link", callback_data=f'channel_link_{channel_id}')],
        [InlineKeyboardButton("🔗 Lista link", callback_data=f'channel_listlinks_{channel_id}'), InlineKeyboardButton("Affiliazione", callback_data=f'channel_affiliateid_{channel_id}')],
        [InlineKeyboardButton("Layout", callback_data=f'channel_layout_{channel_id}'), InlineKeyboardButton("Impostazioni", callback_data=f'channel_settings_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data='offerte_canale')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Gestisci il canale <b>{nome_canale}</b>",
        parse_mode="HTML",
        reply_markup=reply_markup
    )