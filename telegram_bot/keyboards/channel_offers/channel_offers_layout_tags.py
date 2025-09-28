from telegram import *
from telegram.ext import *

async def edit_tags(query, channel_id):

    await query.answer()



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

async def edit_tag_menu(query, context, channel_id, tag_type):
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
    else:
        text="Tipo di tag non valido."

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_edittags_{channel_id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )

async def edit_tag_submenu(query, context, channel_id, tag_type, tag_subtype):
    await query.answer("Funzione in sviluppo", show_alert=True)