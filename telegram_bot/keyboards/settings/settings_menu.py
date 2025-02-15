from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from database.DAO.UtenteDAO import UtenteDAO

from database.Entity.Utente import Utente

from telegram_bot.messages.messages_it import get_impostazioni

async def settings_menu(user_id, query): 
        keyboard = []

        with UtenteDAO() as utente_dao:
            utente = utente_dao.get(user_id)

        if utente.getIsAdmin():
            keyboard.append([InlineKeyboardButton("Pannello admin", callback_data='admin_settings')])

        keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data='back_to_main')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=get_impostazioni(),parse_mode="HTML", reply_markup=reply_markup)