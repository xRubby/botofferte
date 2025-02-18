from telegram import *
from telegram.ext import *

from database.Entity.Canale import Canale

from database.DAO.CanaleDAO import CanaleDAO
from database.DAO.LicenzaDAO import LicenzaDAO

async def edit_channel(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, user_id: int, channel_id: str):

    with LicenzaDAO() as licenza_dao, CanaleDAO() as canale_dao:
        canale = canale_dao.get(channel_id)
        licenza = licenza_dao.get(canale.codice_licenza)

        if(licenza):
            if not licenza_dao.get_stato(licenza.codice_licenza):
                text= "Licenza del canale scaduta.\n\nInviami la nuova licenza."
                await update_channel_license(query, context, user_id, text, channel_id)
                return
        else:
            text= "Licenza del canale non trovata.\n\nInviami la nuova licenza."
            await update_channel_license(query, context, user_id, text, channel_id)
            return

    keyboard = [
        [InlineKeyboardButton("➕ Inserisci link", callback_data=f'channel_link_{channel_id}')],
        [InlineKeyboardButton("🔗 Lista link", callback_data=f'channel_listlinks_{channel_id}'), InlineKeyboardButton("Affiliazione", callback_data=f'channel_affiliateid_{channel_id}')],
        [InlineKeyboardButton("Layout", callback_data=f'channel_layout_{channel_id}'), InlineKeyboardButton("Impostazioni (WIP)", callback_data=f'none')],
        [InlineKeyboardButton("Pannello Admin", callback_data=f'channel_adminpanel_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data='offerte_canale')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Gestisci il canale <b>{canale.nome_canale}</b>",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

    await query.answer()

async def update_channel_license(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, user_id: int, text: str, channel_id: str):

    message_id = query.message.id
    context.user_data[user_id] = {'awaiting_newlicense': True, 'message_id': message_id, 'channel_id': channel_id}

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data='offerte_canale')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

    await query.answer()