from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from database.DAO.UtentiDAO import isAdmin

from telegram_bot.messages.messages_it import get_impostazioni

async def settings_menu(user_id, query): 
        keyboard = []

        print(isAdmin(user_id))

        if isAdmin(user_id):
            keyboard.append([InlineKeyboardButton("Pannello admin", callback_data='admin_settings')])

        keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data='back_to_main')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=get_impostazioni(),parse_mode="HTML", reply_markup=reply_markup)