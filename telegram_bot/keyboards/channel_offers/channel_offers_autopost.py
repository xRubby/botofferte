import asyncio
from datetime import datetime, timedelta
import html
import math

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions, Update
import telegram
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from database.session import SessionLocal
from services.canale_service import CanaleService
from services.pubblica_service import PubblicaService
from telegram_bot.functions.send_message import search_offer
from utils.channel_offers_utils import check_channel_id

ATTESA_LINK_AUTOPOST = range(1)
QUEUE_PAGE_SIZE = 5


async def autopost_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    with SessionLocal() as session:
        canale = CanaleService(session).ottieni_canale(channel_id)

        if canale:
            attivo = canale.autopost_attivo
            intervallo = canale.autopost_intervallo_min
            in_coda = PubblicaService(session).conta_link_autopost(channel_id)
            prossimo_invio_data = canale.autopost_prossimo_invio.date()
            prossimo_invio_ora = canale.autopost_prossimo_invio.time().strftime("%H:%M:%S")

    if not canale:
        await query.edit_message_text(
            text="🔍 <b>Canale non trovato</b>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Indietro", callback_data='channeloffers_main')]])
        )
        return

    stato = "🟢 Attivo" if attivo else "🔴 Non attivo"

    text = (
        "⚡ <b>AutoPost</b>\n\n"
        "I link nella coda vengono pubblicati automaticamente nel canale, uno alla volta.\n\n"
        f"⚙️ <b>Stato:</b> {stato}\n"
        f"⏱️ <b>Intervallo:</b> ogni {intervallo} min\n"
        f"📦 <b>Link in coda:</b> {in_coda}"
    )

    if attivo:
        text+= f"\n<b>Prossimo invio:</b> {prossimo_invio_data} alle ore {prossimo_invio_ora}"

    keyboard = [
        [InlineKeyboardButton("🔴 Disattiva AutoPost" if attivo else "🟢 Attiva AutoPost", callback_data=f'channeloffers_autoposttoggle_{channel_id}')],
        [
            InlineKeyboardButton("➕ Aggiungi link", callback_data=f'channeloffers_autopostaddlink_{channel_id}'),
            InlineKeyboardButton("📋 Visualizza coda", callback_data=f'channeloffers_autopostqueue_0_{channel_id}')
        ],
        [
            InlineKeyboardButton("⚙️ Impostazioni", callback_data=f'none'),
            InlineKeyboardButton("🔄 Aggiorna", callback_data=f'channeloffers_autopostrefresh_{channel_id}')
        ],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_info_{channel_id}')]
    ]

    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def autopost_aggiorna_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        await autopost_main_menu(update, context)
    except telegram.error.BadRequest as e:
        if "Message is not modified" in str(e):
            return
        raise

async def autopost_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    channel_id = check_channel_id(query, context)

    with SessionLocal() as session:
        canale = CanaleService(session).ottieni_canale(channel_id)

        if not canale:
            await query.answer("⚠️ Canale non trovato.", show_alert=True)
            return

        try:
            if canale.autopost_attivo:
                canale.autopost_attivo = False
                testo = "🔴 AutoPost disattivato!"
            else:
                canale.autopost_attivo = True
                canale.autopost_prossimo_invio = datetime.now() + timedelta(minutes=canale.autopost_intervallo_min)
                testo = "🟢 AutoPost attivato!"

            session.commit()
        except Exception:
            session.rollback()
            testo = "❌ Errore durante l'aggiornamento."

    await query.answer(text=testo, show_alert=True)

    await autopost_main_menu(update, context)

async def autopost_queue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    pagina = int(query.data.split("_")[-2])

    with SessionLocal() as session:
        pubblica_service = PubblicaService(session)

        pubblicazioni, totale = pubblica_service.ottieni_lista_link_autopost(channel_id, pagina, QUEUE_PAGE_SIZE)

        totale_pagine = max(1, math.ceil(totale / QUEUE_PAGE_SIZE))

        text = "📋 <b>Coda AutoPost</b>"

        if totale == 0:
            text += "\n\nLa coda è vuota.\n\n➕ Aggiungi un link per iniziare."
        else:
            text += f" • <i>Pagina {pagina + 1}/{totale_pagine}</i>\n\n"

            for i, pubblicazione in enumerate(pubblicazioni, start=pagina * QUEUE_PAGE_SIZE + 1):
                prodotto = pubblicazione.prodotto

                titolo = prodotto.titolo
                if len(titolo) > 70:
                    titolo = titolo[:67] + "..."
                titolo = html.escape(titolo)

                prezzo = str(prodotto.prezzo).replace(".", ",")
                link = html.escape(prodotto.link, quote=True)

                text += (
                    f"<b>{i}.</b> 📦 {titolo}\n"
                    f"💰 {prezzo}{prodotto.valuta}\n"
                    f"🔗 <a href=\"{link}\">Vai al prodotto</a>\n\n"
                )

    keyboard = []

    if totale_pagine > 1:
        keyboard.append([
            InlineKeyboardButton("⏮️", callback_data=f'channeloffers_autopostqueue_0_{channel_id}' if pagina != 0 else 'none'),
            InlineKeyboardButton("⬅️", callback_data=f'channeloffers_autopostqueue_{(pagina - 1) % totale_pagine}_{channel_id}'),
            InlineKeyboardButton("➡️", callback_data=f'channeloffers_autopostqueue_{(pagina + 1) % totale_pagine}_{channel_id}'),
            InlineKeyboardButton("⏭️", callback_data=f'channeloffers_autopostqueue_{totale_pagine - 1}_{channel_id}' if pagina != totale_pagine - 1 else 'none'),
        ])

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_autopost_{channel_id}')])

    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


async def autopost_add_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_autopost_{channel_id}')]
    ]

    msg = await query.edit_message_text(
        text=(
            "🤖 <b>Aggiungi link alla coda AutoPost</b>\n\n"
            "Incolla il link del prodotto Amazon da inserire nella coda 👇"
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data["msg_id"] = msg.message_id

    return ATTESA_LINK_AUTOPOST


async def ricevi_link_autopost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyword = update.message.text
    channel_id = context.user_data.get("channel_id")
    message_id = context.user_data.get("msg_id")
    user_id = update.effective_user.id

    await update.message.delete()

    if not channel_id or not message_id:
        return ConversationHandler.END

    msg = await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=(
            "🔍 <b>Ricerca in corso...</b>\n\n"
            "Sto analizzando il prodotto Amazon."
        ),
        parse_mode="HTML",
    )

    asyncio.create_task(
        search_offer(
            user_id,
            context,
            keyword,
            update.effective_chat.id,
            msg.message_id,
            for_autopost=True
        )
    )

    return ConversationHandler.END


async def annulla_add_link_autopost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("msg_id", None)

    await autopost_main_menu(update, context)
    return ConversationHandler.END


conv_autopost_add_link = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(autopost_add_link, pattern=r'^channeloffers_autopostaddlink_-?\d+$')
    ],
    states={
        ATTESA_LINK_AUTOPOST: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_link_autopost),
            CallbackQueryHandler(annulla_add_link_autopost, pattern=r'^channeloffers_autopost_-?\d+$'),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(annulla_add_link_autopost, pattern=r'^channeloffers_autopost_-?\d+$')
    ],
    per_message=False,
    per_chat=True,
)