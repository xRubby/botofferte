from telegram import *
from telegram.ext import *

from database.Entity.Canale import Canale

from database.DAO.CanaleDAO import CanaleDAO

async def edit_channel(query, channel_id):

    await query.answer()

    canale_dao = CanaleDAO()

    nome_canale = canale_dao.get(channel_id).getNomeCanale()

    keyboard = [
        [InlineKeyboardButton("➕ Inserisci link", callback_data=f'channel_link_{channel_id}')],
        [InlineKeyboardButton("🔗 Lista link", callback_data=f'channel_listlinks_{channel_id}'), InlineKeyboardButton("Affiliazione", callback_data=f'channel_affiliateid_{channel_id}')],
        [InlineKeyboardButton("Layout", callback_data=f'channel_layout_{channel_id}'), InlineKeyboardButton("Impostazioni", callback_data=f'channel_settings_{channel_id}')],
        [InlineKeyboardButton("Pannello Admin", callback_data=f'channel_adminpanel_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data='offerte_canale')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Gestisci il canale <b>{nome_canale}</b>",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

    canale_dao.close()