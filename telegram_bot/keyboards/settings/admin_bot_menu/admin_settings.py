from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from telegram_bot.messages.messages_it import get_admin_message, get_licenza_generata

from utils.generate_license import generate_license


from database.DAO.LicenzeDAO import addLicense,getLicenses,deleteLicense,getLicenseDetails


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

        addLicense(new_license)

        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data='admin_settings')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=get_licenza_generata(new_license),parse_mode="HTML", reply_markup=reply_markup)



async def view_licenses(query):
    licenses = getLicenses()

    if licenses:
        keyboard = [
            [InlineKeyboardButton(license['codice_licenza'], callback_data=f'views_{license["codice_licenza"]}')]
            for license in licenses
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
    license_details = getLicenseDetails(license_code)

    if license_details:
        text = f"Licenza: {license_details['codice_licenza']}\nStato: {license_details['stato']}"
        
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
    deleteLicense(license_code)
    
    text = f"Licenza '{license_code}' cancellata con successo!"
    keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data='view_licenses')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=reply_markup)

