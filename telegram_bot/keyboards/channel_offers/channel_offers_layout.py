from telegram import *
from telegram.ext import *

from database.Entity.Layout import Layout

from database.DAO.LayoutDAO import LayoutDAO

from telegram_bot.messages.messages_it import getTemplateMessage

async def layout_menu(query, context: ContextTypes, channel_id: str, user_id: int):

    await query.answer()

    if context.user_data[user_id].get('awaiting_name_layout'):
        context.user_data[user_id]['awaiting_name_layout'] = False
    if context.user_data[user_id].get('awaiting_message_layout'):
        context.user_data[user_id]['awaiting_message_layout'] = False

    keyboard = [
        [InlineKeyboardButton("Aggiungi layout", callback_data=f'channel_addlayout_{channel_id}')],
        [InlineKeyboardButton("Seleziona layout", callback_data=f'channel_showlayouts_{channel_id}'), InlineKeyboardButton("Modifica Layout", callback_data=f'channel_editlayouts_{channel_id}')],
        [InlineKeyboardButton("Modifica Tag", callback_data=f'channel_edittags_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="In questa pagina potrai gestire il layout del messaggio che verrà inviato all'interno del canale.\n\n",
        reply_markup=reply_markup
    )


async def add_layout(query, context, channel_id, user_id):

    await query.answer()

    message_id = query.message.id
    context.user_data[user_id] = {'awaiting_name_layout': True, 'message_id': message_id, 'channel_id': channel_id}

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_layout_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Inserisci il nome da dare al layout.\n\n",
        reply_markup=reply_markup
    )

async def select_layouts_buildMessage(query, channel_id):
    keyboard = []

    with LayoutDAO() as layout_dao:
        layouts = layout_dao.get_channel_layouts(channel_id)
        if layouts:
            text=f"I tuoi layout\n\nLayout totali: {len(layouts)}"
            for layout in layouts:
                emoji_stato = "🟢" if layout.in_uso else "🔴"

                keyboard.append([InlineKeyboardButton(f"{layout.nome_layout}", callback_data=f'none'), InlineKeyboardButton(f"{emoji_stato}", callback_data=f'channel_activatelayout_{channel_id}_{layout.layout_id}')])

        else:
            text = "Nessun layout presente"

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_layout_{channel_id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
    )

async def select_layouts(query, channel_id):

    await query.answer()

    await select_layouts_buildMessage(query, channel_id)

    

async def activate_layout(query, layout_id):

    with LayoutDAO() as layout_dao:
        layout = layout_dao.get(layout_id)
        id_canale = layout.canale_id

        if(layout.in_uso):
            layout_dao.update_stato(0, layout.layout_id)
            text="Layout disattivato!"
        else:
            layout_old = layout_dao.get_channel_layout_activated(id_canale)
            if layout_old:
                layout_dao.update_stato(0, layout_old.layout_id)
            layout_dao.update_stato(1, layout.layout_id)
            text="Layout selezionato!"
    
    await query.answer(text=text, show_alert=True)

    await select_layouts_buildMessage(query, id_canale)


async def edit_layouts(query, channel_id):

    await query.answer()

    keyboard = []

    with LayoutDAO() as layout_dao:
        layouts = layout_dao.get_channel_layouts(channel_id)
        if layouts:
            text=f"Seleziona un layout da modificare"
            for layout in layouts:
                keyboard.append([InlineKeyboardButton(f"{layout.nome_layout}", callback_data=f'channel_editlayout_{channel_id}_{layout.layout_id}')])

        else:
            text = "Nessun layout presente"

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_layout_{channel_id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
    )





async def edit_layout(query, context, user_id, layout_id):

    await query.answer()

    if user_id is not None and context.user_data[user_id].get('awaiting_newmessage_layout'):
        context.user_data[user_id]['awaiting_newmessage_layout'] = False

    with LayoutDAO() as layout_dao:
        layout = layout_dao.get(layout_id)
    
    text = (f"Layout selezionato: {layout.nome_layout}\n\n"
            f"Messaggio attuale\n\n{layout.messaggio}")

    keyboard = [
        [InlineKeyboardButton("Modifica messaggio", callback_data=f'channel_editmessagelayout_{layout.canale_id}_{layout_id}'),InlineKeyboardButton("Cancella Layout", callback_data=f'channel_deletelayout_{layout.canale_id}_{layout.layout_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_editlayouts_{layout.canale_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
            text=text,
            reply_markup=reply_markup
    )

async def edit_layout_message(query, context, user_id, layout_id, canale_id):
    await query.answer()

    message_id = query.message.id
    context.user_data[user_id] = {'awaiting_newmessage_layout': True, 'message_id': message_id, 'layout_id': layout_id, 'channel_id': canale_id}

    text = ("Modifica Layout\n\n"
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
        "tra i due TAG Speciali, in caso manca UNO dei TAG Post la frase non viene visualizzata.")
        

    keyboard = [
        [InlineKeyboardButton("Resetta Layout", callback_data=f'channel_resetlayout_{canale_id}_{layout_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_editlayout_{canale_id}_{layout_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
    )


async def delete_layout(query, layout_id, canale_id):

    await query.answer()

    with LayoutDAO() as layout_dao:
        layout_dao.delete(layout_id)

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_editlayouts_{canale_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
            text="Layout eliminato con successo",
            reply_markup=reply_markup,
            parse_mode="HTML"
    )

async def reset_layout(query, channel_id, layout_id):
    with LayoutDAO() as layout_dao:
        layout_dao.update_messaggio(getTemplateMessage(), layout_id)

    await query.answer("Layout resettato con successo!", show_alert=True)

    await edit_layout(query, None, None, layout_id)