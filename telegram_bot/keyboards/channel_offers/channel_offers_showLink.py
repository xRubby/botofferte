from telegram import *
from telegram.ext import *

from telegram_bot.functions.send_message import publish_offer

from database.DAO import CanaleDAO, PubblicaDAO


async def show_links(query, context, channel_id, current_link_index=0):

    await query.answer()

    with PubblicaDAO() as pubblica_dao:
        links = pubblica_dao.get_channel_link_non_pubblicati_(channel_id)

    if not links:
        await query.edit_message_text(
            text="Non ci sono link nel database.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Torna indietro", callback_data=f'edit_channel_{channel_id}')
            ]])
        )
        return

    link = links[current_link_index]

    text = f"Link corrente: {current_link_index+1}\n\n{link.getMessaggio()}"

    keyboard = [
        [InlineKeyboardButton("Pubblica messaggio", callback_data=f'publish_{channel_id}_{link.getId()}')],
        [InlineKeyboardButton("Rimuovi prodotto", callback_data=f'remove_{channel_id}_{link.getId()}')],
        [InlineKeyboardButton("⬅️ Precedente", callback_data=f'prev_{channel_id}_{current_link_index}')],
        [InlineKeyboardButton("➡️ Successivo", callback_data=f'next_{channel_id}_{current_link_index}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='HTML')

async def publish_message(query, update, context, channel_id, link_id):

    await query.answer()

    with PubblicaDAO() as pubblica_dao:
        link = pubblica_dao.get(link_id)

        try:
            await publish_offer(update, context, channel_id, link.getMessaggio())

            await query.edit_message_text(
                text=f"Messaggio pubblicato nel canale!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Torna indietro", callback_data=f'channel_listlinks_{channel_id}')
                ]])
                
            )
            pubblica_dao.update_is_pubblicato(link.getId(), link.getIdCanale(), link.getAsinProdotti(), 1)
        except Exception as e:
            await query.edit_message_text(
                text="Errore durante la pubblicazione del messaggio. Il bot non ha i requisiti di amministratore all'interno del canale",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Torna indietro", callback_data=f'channel_listlinks_{channel_id}')
                ]])
            )

    
    

async def navigate_links(query, context, channel_id, direction, current_link_index):

    await query.answer()
    
    with PubblicaDAO() as pubblica_dao:
        links = pubblica_dao.get_channel_link_non_pubblicati_(channel_id)

    if(len(links) >=2):
        if direction == "prev":
            current_link_index = (current_link_index - 1) % len(links)
        elif direction == "next":
            current_link_index = (current_link_index + 1) % len(links)

        await show_links(query, context, channel_id, current_link_index)
    else: None

async def remove_product(query, context, id_channel, link_id):

    await query.answer()
    
    with PubblicaDAO() as pubblica_dao:
        link = pubblica_dao.get(link_id)

        if link:
            pubblica_dao.delete(link.getId(), link.getIdCanale(), link.getAsinProdotti())

            await query.edit_message_text(
                text=f"Link rimosso dalla lista.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Torna indietro", callback_data=f'channel_listlinks_{id_channel}')
                ]])
            )
        else:
            await query.edit_message_text(
                text="Errore: il link che stai cercando di rimuovere non esiste.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Torna indietro", callback_data=f'channel_listlinks_{id_channel}')
                ]])
            )