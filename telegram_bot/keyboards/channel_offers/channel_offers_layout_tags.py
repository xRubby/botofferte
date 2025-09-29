from telegram import *
from telegram.ext import *

from database.Entity.Canale import Canale

from database.DAO.CanaleDAO import CanaleDAO

async def edit_tags(query, context, user_id, channel_id):

    await query.answer()

    if 'awaiting_tag_type_message' in context.user_data[user_id]:
        context.user_data[user_id]['awaiting_tag_type_message'] = False



    keyboard = [
        [
            InlineKeyboardButton("{spedito}", callback_data=f'channel_edittags_{channel_id}_spedito'),
            InlineKeyboardButton("{prime}", callback_data=f'channel_edittags_{channel_id}_prime'),
        ],
        [
            InlineKeyboardButton("{preorder}", callback_data=f'channel_edittags_{channel_id}_preorder')
        ],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_layout_{channel_id}')]
    ]



    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Qui puoi modificare le informazioni dei tag.",
        reply_markup=reply_markup
    )

async def edit_tag_menu(query, context, user_id, channel_id, tag_type):
    await query.answer()

    keyboard = []
    if tag_type in ['spedito', 'prime', 'preorder']:
        if tag_type == 'spedito':
            text="""Usa questi pulsanti per aggiornare il messaggio del canale con il tipo di vendita e spedizione del prodotto:

Venduto e spedito da Amazon → Aggiorna il messaggio indicando che Amazon gestisce sia la vendita che la spedizione.

Venduto da VENDITORE e spedito da Amazon → Aggiorna il messaggio indicando che il venditore vende il prodotto, ma la spedizione è gestita da Amazon.

Venduto e spedito da VENDITORE → Aggiorna il messaggio indicando che il venditore gestisce sia la vendita che la spedizione."""
            spedito_keyboard = [
                [InlineKeyboardButton("Venduto e spedito da Amazon", callback_data=f'channel_edittags_{channel_id}_spedito_amazon')],
                [InlineKeyboardButton("Venduto da VENDITORE e spedito da Amazon", callback_data=f'channel_edittags_{channel_id}_spedito_venditoreamazon')],
                [InlineKeyboardButton("Venduto e spedito da VENDITORE", callback_data=f'channel_edittags_{channel_id}_spedito_venditore')]
            ]
            keyboard.extend(spedito_keyboard)
        
        elif tag_type == 'prime':
            message_id = query.message.id
            context.user_data[user_id] = {'awaiting_tag_type_message': True, 'tag_type': tag_type,'message_id': message_id, 'channel_id': channel_id}
            with CanaleDAO() as canale_dao:
                canale = canale_dao.get(channel_id)
            text=f"Hai selezionato: Prime.\n\nMessaggio corrente: {canale.prime_tag}"
            keyboard.append([InlineKeyboardButton("Resetta messaggio", callback_data=f'channel_edittags_{channel_id}_prime_reset')])
        elif tag_type == 'preorder':
            message_id = query.message.id
            context.user_data[user_id] = {'awaiting_tag_type_message': True, 'tag_type': tag_type,'message_id': message_id, 'channel_id': channel_id}
            with CanaleDAO() as canale_dao:
                canale = canale_dao.get(channel_id)
            text=f"Hai selezionato: Preordine.\n\nMessaggio corrente: {canale.preorder_tag}"
            keyboard.append([InlineKeyboardButton("Resetta messaggio", callback_data=f'channel_edittags_{channel_id}_preorder_reset')])
    else:
        text="Tipo di tag non valido."

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_edittags_{channel_id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )

async def edit_tag_submenu(query, context, user_id, channel_id, tag_type, tag_subtype):
    await query.answer()

    keyboard = []

    message_id = query.message.id
    context.user_data[user_id] = {'awaiting_tag_subtype_message': True, 'tag_type': tag_type, 'tag_subtype': tag_subtype, 'message_id': message_id, 'channel_id': channel_id}

    with CanaleDAO() as canale_dao:
        canale = canale_dao.get(channel_id)

    if tag_type == 'spedito':
        if tag_subtype in ['amazon', 'venditoreamazon', 'venditore']:
            if tag_subtype == 'amazon':
                text=f"Hai selezionato: Venduto e spedito da Amazon.\n\nMessaggio corrente: {canale.amazon_tag}"
            elif tag_subtype == 'venditoreamazon':
                text=f"Hai selezionato: Venduto da VENDITORE e spedito da Amazon.\n\nMessaggio corrente: {canale.venditoreamazon_tag}"
            elif tag_subtype == 'venditore':
                text=f"Hai selezionato: Venduto e spedito da VENDITORE.\n\nMessaggio corrente: {canale.venditore_tag}"
    else:
        text="Tag non valido."
        context.user_data[user_id]['awaiting_tag_subtype_message'] = False

    keyboard.append([InlineKeyboardButton("Resetta messaggio", callback_data=f'channel_edittags_{channel_id}_{tag_type}_{tag_subtype}_reset')])
    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_edittags_{channel_id}_{tag_type}')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )

async def reset_tag_message(query, context, user_id, channel_id, tag_type, tag_subtype):
    await query.answer()

    if 'awaiting_tag_subtype_message' in context.user_data[user_id]:
        context.user_data[user_id]['awaiting_tag_subtype_message'] = False

    with CanaleDAO() as canale_dao:
        if tag_type == 'spedito':
            if tag_subtype == 'amazon':
                canale_dao.update_tag(channel_id, 'amazon', 'Venduto e spedito da Amazon')
                text = "Messaggio aggiornato a: Venduto e spedito da Amazon."
            elif tag_subtype == 'venditoreamazon':
                canale_dao.update_tag(channel_id, 'venditoreamazon', 'Venduto da {venditore} e spedito da Amazon')
                text = "Messaggio aggiornato a: Venduto da {venditore} e spedito da Amazon."
            elif tag_subtype == 'venditore':
                canale_dao.update_tag(channel_id, 'venditore', 'Venduto e spedito da {venditore}')
                text = "Messaggio aggiornato a: Venduto e spedito da {venditore}"
        elif tag_type == 'prime':
            canale_dao.update_tag(channel_id, 'prime', 'Spedizione gratuita con Amazon Prime')
            text = "Messaggio aggiornato a: Spedizione gratuita con Amazon Prime."
        elif tag_type == 'preorder':
            canale_dao.update_tag(channel_id, 'preorder', 'Preordine')
            text = "Messaggio aggiornato a: Preordine"

    keyboard = []

    if tag_subtype is not None:
        keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_edittags_{channel_id}_{tag_type}_{tag_subtype}')])
    else:
        keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_edittags_{channel_id}_{tag_type}')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )