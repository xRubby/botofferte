import traceback

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, error
from telegram.ext import ContextTypes

from database.DAO.PubblicaDAO import PubblicaDAO
from telegram_bot.functions.send_message import publish_offer
from utils.channel_offers_utils import check_channel_id, delete_preview_message



async def insert_link_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    await delete_preview_message(
        chat_id=query.message.chat_id,
        context=context
    )

    links = context.user_data.get("links")

    if not links:
        with PubblicaDAO() as pubblicaDAO:
            links = pubblicaDAO.get_channel_link_non_pubblicati(channel_id)
            context.user_data["links"] = links

    if not links:
        await query.edit_message_text(
            text=(
                "🔗 <b>Lista Link</b>\n\n"
                "Non hai ancora aggiunto alcun link.\n\n"
                "➕ Aggiungine uno per iniziare."
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Inserisci Link", callback_data=f'channeloffers_addlink_{channel_id}')],
                [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_info_{channel_id}')]
            ]),
            parse_mode='HTML'
        )
        return
    
    current_index = int(query.data.split("_")[-2])
    link = links[current_index]
    context.user_data.pop("pubblicato", None)

    text = f"🔗 <b>Link {current_index + 1}</b>\n\n{link.messaggio}"

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
        [InlineKeyboardButton("📢 Pubblica messaggio", callback_data=f'channeloffers_publishlink_{link.id}_{channel_id}')],
        [InlineKeyboardButton("🗑️ Rimuovi link", callback_data=f'channeloffers_removelink_{link.id}_{channel_id}')]
    ])

    

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_info_{channel_id}')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='HTML')

    if hasattr(link, "img_bytes") and link.img_bytes:
        photo_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "❌ Elimina anteprima",
                    callback_data="delete_preview"
                )
            ]
        ])

        preview_msg = await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=link.img_bytes,
            caption=f"🖼️ Anteprima link {current_index + 1}",
            reply_markup=photo_keyboard
        )

        context.user_data["preview_message_id"] = preview_msg.message_id

async def publish_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    channel_id = check_channel_id(query, context)
    link_id = int(query.data.split("_")[-2])


    with PubblicaDAO() as pubblicaDAO:
        link = pubblicaDAO.get_channel_link_by_id(link_id, channel_id)
        pubblicato = pubblicaDAO.get_pubblicato_ultime_24h(channel_id, link.asin_prodotti)

    BACK_BTN = InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_link_0_{channel_id}')
                ]])

    if not link:
        await query.edit_message_text(
            text=(
                "🔍 <b>Link non trovato</b>\n\n"
                "Il link selezionato non è più disponibile."
            ),
            reply_markup=BACK_BTN,
            parse_mode='HTML'
        )
        with PubblicaDAO() as pubblicaDAO:
            links = pubblicaDAO.get_channel_link_non_pubblicati(channel_id)
            context.user_data["links"] = links
        return
    
    if pubblicato and not context.user_data.get("pubblicato", None):
        context.user_data["pubblicato"] = True

        await query.answer(
            text=(
                "⚠️ Questo prodotto è già stato pubblicato nelle ultime 24 ore.\n\n"
                "Premi di nuovo per confermare la pubblicazione."
            ),
            show_alert=True
        )

        keyboard = query.message.reply_markup.inline_keyboard
        new_keyboard = []

        for row in keyboard:
            new_row = []

            for btn in row:
                if btn.callback_data and f"channeloffers_publishlink_{link_id}" in btn.callback_data:
                    new_row.append(
                        InlineKeyboardButton(
                            "⚠️ Pubblica messaggio",
                            callback_data=btn.callback_data
                        )
                    )
                else:
                    new_row.append(btn)

            new_keyboard.append(new_row)

        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(new_keyboard)
        )
        return
    
    await query.answer()
    context.user_data.pop("pubblicato", None)

    await delete_preview_message(
        chat_id=query.message.chat_id,
        context=context
    )
    
    try:
        await publish_offer(update, context, link)

        await query.edit_message_text(
            text=(
                "📢 <b>Pubblicazione completata</b>\n\n"
                "Il messaggio è stato inviato nel canale con successo."
            ),
            reply_markup=BACK_BTN,
            parse_mode='HTML'
        )
        with PubblicaDAO() as pubblicaDAO:
            pubblicaDAO.update_pubblicato(link.id, 1)
    except error.BadRequest:
        await query.edit_message_text(
            text=("❌ <b>Errore di pubblicazione</b>\n\n"
            "Il bot non ha i permessi di amministratore per mandare il messaggio nel canale."),
            parse_mode='HTML',
            reply_markup=BACK_BTN
        )
        traceback.print_exc()
    except Exception as e:
        await query.edit_message_text(
            text=("❌ <b>Errore di pubblicazione</b>\n\n"
            "Non è stato possibile inviare il messaggio nel canale.\n"
            "Riprova più tardi."),
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

    await delete_preview_message(
        chat_id=query.message.chat_id,
        context=context
    )

    with PubblicaDAO() as pubblica_dao:
        link = pubblica_dao.get_channel_link_by_id(link_id, channel_id)

        if not link:
            await query.edit_message_text(
                text=("🔍 <b>Link non trovato</b>\n\n"
                    "Il link che stai cercando di rimuovere non esiste o è già stato eliminato."),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_link_0_{channel_id}')
                ]]),
                parse_mode='HTML'
            )

            links = pubblica_dao.get_channel_link_non_pubblicati(channel_id)
            context.user_data["links"] = links
            return

        pubblica_dao.delete(link.id, link.id_canale, link.asin_prodotti)

    await query.edit_message_text(
            text=(
            "🗑️ <b>Link rimosso</b>\n\n"
            "Il link è stato eliminato dalla lista con successo."
        ),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_link_0_{channel_id}')
        ]]),
        parse_mode='HTML'
    )

    with PubblicaDAO() as pubblicaDAO:
            links = pubblicaDAO.get_channel_link_non_pubblicati(channel_id)
            context.user_data["links"] = links