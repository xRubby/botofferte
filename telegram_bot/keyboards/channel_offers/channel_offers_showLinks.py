import traceback

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database.DAO.PubblicaDAO import PubblicaDAO
from telegram_bot.functions.send_message import publish_offer
from utils.channel_offers_utils import check_channel_id



async def insert_link_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    links = context.user_data.get("links")

    if not links:
        with PubblicaDAO() as pubblicaDAO:
            links = pubblicaDAO.get_channel_link_non_pubblicati(channel_id)
            context.user_data["links"] = links

    if not links:
        await query.edit_message_text(
            text="Non ci sono link nel database.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Torna indietro", callback_data=f'channeloffers_info_{channel_id}')
            ]])
        )
        return
    
    current_index = int(query.data.split("_")[-2])
    link = links[current_index]

    text = f"Link corrente: {current_index+1}\n\n{link.messaggio}"

    keyboard = []

    if len(links) > 1:
        keyboard.extend([
            [InlineKeyboardButton("⏮️", callback_data=f'channeloffers_link_0_{channel_id}' if current_index != 0 else f'none'),
            InlineKeyboardButton("⬅️", callback_data=f'channeloffers_link_{(current_index - 1) % len(links)}_{channel_id}'),
            InlineKeyboardButton("➡️", callback_data=f'channeloffers_link_{(current_index + 1) % len(links)}_{channel_id}'),
            InlineKeyboardButton("⏭️", callback_data=f'channeloffers_link_{len(links)-1}_{channel_id}' if current_index != len(links)-1 else f'none')],
        ]
        )

    keyboard.extend( [
        [InlineKeyboardButton("Pubblica messaggio", callback_data=f'channeloffers_publishlink_{link.id}_{channel_id}')],
        [InlineKeyboardButton("Rimuovi prodotto", callback_data=f'channeloffers_removelink_{link.id}_{channel_id}')]
    ])

    

    keyboard.append([InlineKeyboardButton("🔙 Indietro", callback_data=f'channeloffers_info_{channel_id}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='HTML')

async def publish_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    link_id = int(query.data.split("_")[-2])

    with PubblicaDAO() as pubblicaDAO:
        link = pubblicaDAO.get_channel_link_by_id(link_id, channel_id)

    BACK_BTN = InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Torna indietro", callback_data=f'channeloffers_link_0_{channel_id}')
                ]])

    if not link:
        await query.edit_message_text(
                text=f"Link da pubblicare non trovato.",
                reply_markup=BACK_BTN
            )
        return
    
    try:
        await publish_offer(update, context, link)

        await query.edit_message_text(
            text=f"Messaggio pubblicato nel canale!",
            reply_markup=BACK_BTN
        )
        with PubblicaDAO() as pubblicaDAO:
            pubblicaDAO.update_pubblicato(link.id, 1)
    except Exception as e:
        await query.edit_message_text(
            text="Errore durante la pubblicazione del messaggio.",
            parse_mode='HTML',
            reply_markup=BACK_BTN
        )
        traceback.print_exc()

    with PubblicaDAO() as pubblicaDAO:
        links = pubblicaDAO.get_channel_link_non_pubblicati(channel_id)
        context.user_data["links"] = links

async def remove_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    link_id = int(query.data.split("_")[-2])

    with PubblicaDAO() as pubblica_dao:
        link = pubblica_dao.get_channel_link_by_id(link_id, channel_id)

        if not link:
            await query.edit_message_text(
                text="Errore: il link che stai cercando di rimuovere non esiste.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Torna indietro", callback_data=f'channeloffers_link_0_{channel_id}')
                ]])
            )
            return

        pubblica_dao.delete(link.id, link.id_canale, link.asin_prodotti)

    await query.edit_message_text(
        text=f"Link rimosso dalla lista.",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Torna indietro", callback_data=f'channeloffers_link_0_{channel_id}')
        ]])
    )

    with PubblicaDAO() as pubblicaDAO:
            links = pubblicaDAO.get_channel_link_non_pubblicati(channel_id)
            context.user_data["links"] = links