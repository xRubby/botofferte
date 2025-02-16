from telegram import *
from telegram.ext import *

from database.DAO.CanaleDAO import CanaleDAO

from telegram_bot.messages.messages_it import getTemplateMessage

async def layout_menu(query, channel_id):
    keyboard = [
        [InlineKeyboardButton("Aggiungi layout", callback_data=f'edit_channel_{channel_id}')],
        [InlineKeyboardButton("Seleziona layout", callback_data=f'channel_editmessage_{channel_id}'), InlineKeyboardButton("Modifica Layout", callback_data='none')],
        [InlineKeyboardButton("Modifica Tag (WIP)", callback_data='none')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="In questa pagina potrai modificare il layout del messaggio che verrà inviato all'interno del canale.\n\n"
        "Messaggio attuale:\n\n"
        f"{None}",
        reply_markup=reply_markup
    )

async def edit_message(query, context, user_id, channel_id):
    message_id = query.message.id
    context.user_data[user_id] = {'awaiting_newmessage_layout': True, 'message_id': message_id, 'channel_id': channel_id}
    
    keyboard = [
        [InlineKeyboardButton("Reset layout", callback_data=f'channel_resetlayout_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_layout_{channel_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Crea Layout\n\n"
         "Tag disponibili:\n"
         "- <code>{titolo}</code>\n"
         "- <code>{prezzo_nuovo}</code>\n"
         "- <code>{prezzo_vecchio}</code>\n"
         "- <code>{sconto}</code>\n"
         "- <code>{link}</code>\n"
         "- <code>{linkfull}</code>\n"
         "- <code>{valuta}</code>\n"
         "- <code>{spedito}</code>\n"
         "- <code>{prime}</code>\n"
         "- <code>{preorder}</code>\n"
         "- <code>{preorderdate}</code>\n"
         "- <code>{warehouse}</code>\n"
         "- <code>{condition}</code>\n"
         "- <code>{conditioncomm}</code>\n"
         "- <code>{minimo}</code>\n\n"
         "TAG Speciale:\n"
        "I TAG speciali {_ e _} permettono di collegare la Frase compresa tra i due TAG Speciali al TAG Post" 
        "inserito all'interno dei due tag speciali. In caso in cui il TAG Post sia nullo (ovvero manca" 
        "l'informazione su Amazon) la frase non viene visualizzata. Inoltre è possibile inserire più TAG Post," 
        "tra i due TAG Speciali, in caso manca UNO dei TAG Post la frase non viene visualizzata.",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def reset_layout(query, channel_id):

    #set_message_template(channel_id, getTemplateMessage())

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_layout_{channel_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Layout resettato con successo!",
        reply_markup=reply_markup
    )
