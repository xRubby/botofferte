from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram_bot.messages.messages_it import get_admin_message, get_licenza_generata

from utils.generate_license import generate_license

from database.Entity.Licenza import Licenza


from database.DAO.LicenzaDAO import LicenzaDAO


async def admin_menu(query): 
        keyboard = [
        [InlineKeyboardButton("Genera Licenza", callback_data='generate_license')],
        [InlineKeyboardButton("Vedi Licenze", callback_data='view_licenses')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data='settings')],
    ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=get_admin_message(),parse_mode="HTML", reply_markup=reply_markup)

async def generate_new_license(query): 
        new_license = generate_license()

        with LicenzaDAO() as licenza_dao:
            licenza_dao.insert(Licenza(new_license, "2050-12-31", True))

        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data='admin_settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=get_licenza_generata(new_license),parse_mode="HTML", reply_markup=reply_markup)



async def view_licenses(query):

    with LicenzaDAO() as licenza_dao:
        licenze = licenza_dao.get_all()

    if licenze:
        keyboard = [
            [InlineKeyboardButton(licenza.getCodiceLicenza(), callback_data=f'views_{licenza.getCodiceLicenza()}')]
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

async def view_license_details(query, license_code):

    with LicenzaDAO() as licenza_dao:
        licenza = licenza_dao.get(license_code)

    if licenza:
        text = f"Licenza: {licenza.getCodiceLicenza()}\nStato: {'Attiva' if licenza.getStato() else 'Non attiva'}\nData scadenza: {licenza.getScadenza()}"
        
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


async def delete_license_confirm(query, license_code):

    with LicenzaDAO() as licenza_dao:
        licenza_dao.delete(license_code)
    
    text = f"Licenza '{license_code}' cancellata con successo!"
    keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data='view_licenses')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=reply_markup)

