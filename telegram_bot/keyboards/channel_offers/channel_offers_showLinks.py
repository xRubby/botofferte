import html
import traceback

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, error
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from database.session import SessionLocal
from services.pubblica_service import PubblicaService
from telegram_bot.functions.send_message import publish_offer
from utils.channel_offers_utils import check_channel_id, delete_preview_message


ATTESA_NUOVO_MESSAGGIO = range(1)



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

        with SessionLocal() as session:
            pubblica_service = PubblicaService(session)
            links = pubblica_service.ottieni_link_non_pubblicati_per_canale(channel_id)
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

    with SessionLocal() as session:
        link = session.merge(link)

        text_utente = f" - <i>Inserito da {link.utente.nome}</i>" if link.utente else ""


    text = f"🔗 <b>Link {current_index + 1}</b>{text_utente}\n\n{link.messaggio}"

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
        [InlineKeyboardButton("✏️ Modifica", callback_data=f'channeloffers_editlink_{link.id}_{channel_id}'), InlineKeyboardButton("🗑️ Rimuovi", callback_data=f'channeloffers_removelink_{link.id}_{channel_id}')]
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

    return ConversationHandler.END

async def publish_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    channel_id = check_channel_id(query, context)
    link_id = int(query.data.split("_")[-2])


    with SessionLocal() as session:
        pubblica_service = PubblicaService(session)

        link = pubblica_service.ottieni_link_da_id_canale(link_id, channel_id)
        pubblicato = pubblica_service.ottieni_link_pubblicato_ultime_24h(channel_id, link.asin_prodotti)
        if not pubblicato:
            link_confronto, pubblicato_stesso_prezzo = pubblica_service.confronta_prezzo_ultimo_pubblicato(link)

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
        with SessionLocal() as session:
            pubblica_service = PubblicaService(session)
            links = pubblica_service.ottieni_link_non_pubblicati_per_canale(channel_id)
            context.user_data["links"] = links
        return
    
    if not context.user_data.get("pubblicato", None):
        prosegui = True

        if pubblicato:
            await query.answer(
                text=(
                    "⚠️ Questo prodotto è già stato pubblicato nelle ultime 24 ore.\n\n"
                    "Premi di nuovo per confermare la pubblicazione."
                ),
                show_alert=True
            )
        elif link_confronto and pubblicato_stesso_prezzo:
            data_formattata = link_confronto.data_pubblicazione.strftime("%d/%m/%Y alle %H:%M")

            await query.answer(
            text=(
                f"⚠️ Questo prodotto è già stato pubblicato allo stesso prezzo in data {data_formattata}.\n\n"
                "Premi di nuovo per confermare la pubblicazione."
            ),
                show_alert=True
            )
        else:
            prosegui = False

        if prosegui:
            context.user_data["pubblicato"] = True

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

        with SessionLocal() as session:
            pubblica_service = PubblicaService(session)
            link = session.merge(link)

            pubblica_service.segna_pubblicato(link)

            session.commit()

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

    with SessionLocal() as session:
        pubblica_service = PubblicaService(session)
        links = pubblica_service.ottieni_link_non_pubblicati_per_canale(channel_id)
        context.user_data["links"] = links

async def edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    link_id = int(query.data.split("_")[-2])

    await delete_preview_message(
        chat_id=query.message.chat_id,
        context=context
    )

    with SessionLocal() as session:
        pubblica_service = PubblicaService(session)
        link = pubblica_service.ottieni_link_da_id_canale(link_id, channel_id)

        if not link:
            await query.edit_message_text(
                text=("🔍 <b>Link non trovato</b>\n\n"
                    "Il link che stai cercando di modificare non esiste o è già stato eliminato."),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_link_0_{channel_id}')
                ]]),
                parse_mode='HTML'
            )

            links = pubblica_service.ottieni_link_non_pubblicati_per_canale(channel_id)
            context.user_data["links"] = links
            return

    text = (
        "✏️ <b>Modifica il tuo messaggio</b>\n\n"
        "📋 Tocca il messaggio qui sotto per copiarlo "
        "e poterlo modificare o inviare direttamente in chat.\n\n"
        f"<code>{html.escape(link.messaggio)}</code>\n\n"
    )

    msg = await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_link_0_{channel_id}')
        ]]),
        parse_mode='HTML'
    )

    context.user_data["edit_message_id"] = msg.id
    context.user_data["link_id"] = link_id
    context.user_data["channel_id"] = channel_id

    return ATTESA_NUOVO_MESSAGGIO


async def receive_edit_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg_id = context.user_data.get("edit_message_id")
    link_id = context.user_data.get("link_id")
    channel_id = context.user_data.get("channel_id")
    new_msg = update.message.text_html

    new_msg = html.unescape(new_msg)

    await update.message.delete()

    with SessionLocal() as session:
        pubblica_service = PubblicaService(session)
        link = pubblica_service.ottieni_link_da_id_canale(link_id, channel_id)

        links = pubblica_service.ottieni_link_non_pubblicati_per_canale(channel_id)
        context.user_data["links"] = links

        if not link:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=msg_id,
                text=("🔍 <b>Link non trovato</b>\n\n"
                    "Il link che stai cercando di modificare non esiste o è già stato eliminato."),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_link_0_{channel_id}')
                ]]),
                parse_mode='HTML'
            )
            return

        link.messaggio = new_msg
        session.commit()

        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=msg_id,
            text = "✅ <b>Messaggio aggiornato con successo!</b>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_link_0_{channel_id}')
            ]]),
            parse_mode='HTML'
        )

        return ConversationHandler.END

async def remove_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    link_id = int(query.data.split("_")[-2])

    await delete_preview_message(
        chat_id=query.message.chat_id,
        context=context
    )

    with SessionLocal() as session:
        pubblica_service = PubblicaService(session)
        link = pubblica_service.ottieni_link_da_id_canale(link_id, channel_id)

        if not link:
            await query.edit_message_text(
                text=("🔍 <b>Link non trovato</b>\n\n"
                    "Il link che stai cercando di rimuovere non esiste o è già stato eliminato."),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_link_0_{channel_id}')
                ]]),
                parse_mode='HTML'
            )

            links = pubblica_service.ottieni_link_non_pubblicati_per_canale(channel_id)
            context.user_data["links"] = links
            return

        pubblica_service.rimuovi_link(link)
        session.commit()

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

    with SessionLocal() as session:
        pubblica_service = PubblicaService(session)
        links = pubblica_service.ottieni_link_non_pubblicati_per_canale(channel_id)
        context.user_data["links"] = links


# ── ConversationHandler ───────────────────────────────────────────────────────

conv_edit_link = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(edit_message, pattern=r"channeloffers_editlink_\d+_.+$")
    ],
    states={
        ATTESA_NUOVO_MESSAGGIO: [
            MessageHandler(filters.ALL & ~filters.COMMAND, receive_edit_message),
            CallbackQueryHandler(insert_link_entry, pattern=r"^channeloffers_link_\d+_-?\d+$"),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(insert_link_entry, pattern=r"^channeloffers_link_\d+_-?\d+$")
    ],
    per_message=False,
    per_chat=True,
)