from telegram import *
from telegram.ext import *

from telegram_bot.messages.messages_it import get_admin_message, get_licenza_generata

from utils.generate_license import generate_license

from database.Entity.Licenza import Licenza


from database.DAO.LicenzaDAO import LicenzaDAO


async def admin_menu(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, user_id: str):
        
        if context.user_data[user_id].get('awaiting_tipo_license'):
            context.user_data[user_id]['awaiting_tipo_license'] = False

        await query.answer()

        keyboard = [
        [InlineKeyboardButton("Genera Licenza", callback_data='generate_license')],
        [InlineKeyboardButton("Vedi Licenze", callback_data='view_licenses')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data='settings')],
    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=get_admin_message(),parse_mode="HTML", reply_markup=reply_markup)

async def generate_new_license(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, user_id: str): 
        
    await query.answer()

    message_id = query.message.id
    context.user_data[user_id] = {'awaiting_tipo_license': True, 'message_id': message_id}

    text = "Inserisci il tipo della licenza. Puoi usare anche i tasti rapidi qui sotto.\n\nEsempi: 2 mesi, 3 anni"

    keyboard = [
        [InlineKeyboardButton("1 Settimana (WIP)", callback_data='none'), InlineKeyboardButton("30 Giorni (WIP)", callback_data='none')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data='admin_settings')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)



    await query.edit_message_text(text=text,parse_mode="HTML", reply_markup=reply_markup)



async def view_licenses(query: CallbackQuery):

    await query.answer()

    with LicenzaDAO() as licenza_dao:
        licenze = licenza_dao.get_all()

    if licenze:
        keyboard = [
            [InlineKeyboardButton(licenza.codice_licenza, callback_data=f'views_{licenza.codice_licenza}')]
            for licenza in licenze
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data='admin_settings')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "Licenze generate:"
    else:
        text = "Nessuna licenza trovata."
        keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data='admin_settings')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=reply_markup)

async def view_license_details(query: CallbackQuery, license_code: str):

    await query.answer()

    with LicenzaDAO() as licenza_dao:
        licenza = licenza_dao.get(license_code)
        stato = licenza_dao.get_stato(license_code)

    if licenza:
        text = f"Licenza: {licenza.codice_licenza}\nTipo: {licenza.tipo.title()}\n"

        if(stato):
            text += f"Stato: 'Attiva'\n\nData attivazione: {licenza.data_attivazione}\nData scadenza: {licenza.data_scadenza}"
        else:
            text += "Stato: 'Non attiva'"

        
        keyboard = [
            [InlineKeyboardButton("Cancella Licenza", callback_data=f'confirmdelete_{license_code}')],
            [InlineKeyboardButton("⬅️ Indietro", callback_data='view_licenses')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        text = "Licenza non trovata."
        keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data='view_licenses')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=reply_markup)


async def delete_license_confirm(query: CallbackQuery, license_code: str):

    await query.answer()

    with LicenzaDAO() as licenza_dao:
        licenza_dao.delete(license_code)
    
    text = f"Licenza '{license_code}' cancellata con successo!"
    keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data='view_licenses')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=reply_markup)

