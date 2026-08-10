import math

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions, Update
from telegram.ext import ContextTypes

from database.session import SessionLocal
from services.pubblica_service import PubblicaService
from utils.channel_offers_utils import check_channel_id

async def channel_publishedlink_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    
    channel_id = check_channel_id(query, context)
        
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🆕 Ultimi pubblicati (WIP)", callback_data='none')],
        [InlineKeyboardButton("⏰ Da ripubblicare", callback_data=f'channeloffers_stale_0_{channel_id}')] ,
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_info_{channel_id}')]    
    ]

    text = (
        "🔗 <b>Link pubblicati</b>\n\n"

        "Qui puoi consultare i link pubblicati nel canale, vedere le pubblicazioni più recenti e individuare quelle da ripubblicare."
    )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    await query.answer()

async def channel_staleprodotti(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    
    channel_id = check_channel_id(query, context)
    pagina = int(query.data.split("_")[-2])
    pagina_size = 5
        
    await query.answer()

    with SessionLocal() as session:
        pubblica_service = PubblicaService(session)

        pubblicazioni, totale = pubblica_service.ottieni_prodotti_non_pubblicati_da_tanto_tempo(channel_id, pagina, pagina_size)

        totale_pagine = math.ceil(totale / pagina_size)

        text = "⏰ <b>Da ripubblicare</b>"

        if totale == 0:
            text += "\n\nNessun link da ripubblicare."

        else:
            text += f" • <i>Pagina {pagina + 1}/{totale_pagine}</i>\n\n"

            for pubblicazione in pubblicazioni:
                prodotto = pubblicazione.prodotto

                text += (
                    f"📦 <b>{prodotto.titolo}</b>\n"
                    f"🔖 <code>{prodotto.asin}</code>\n"
                    f"🕒 <i>Pubblicato il:</i> {pubblicazione.data_pubblicazione}\n"
                )

                if pubblicazione.storico_prezzo is not None:
                    text += (
                        f"💰 <b>Prezzo alla pubblicazione:</b> "
                        f"{pubblicazione.storico_prezzo.prezzo}"
                        f"{pubblicazione.storico_prezzo.valuta}\n"
                    )

                text += f"🔗 <a href=\"{prodotto.link}\">Vai al prodotto</a>\n\n"

    keyboard = [
    ]

    if totale_pagine > 1:
        keyboard.extend([
            [InlineKeyboardButton("⏮️", callback_data=f'channeloffers_stale_0_{channel_id}' if pagina != 0 else f'none'),
            InlineKeyboardButton("⬅️", callback_data=f'channeloffers_stale_{(pagina - 1) % totale_pagine}_{channel_id}'),
            InlineKeyboardButton("➡️", callback_data=f'channeloffers_stale_{(pagina + 1) % totale_pagine}_{channel_id}'),
            InlineKeyboardButton("⏭️", callback_data=f'channeloffers_stale_{totale_pagine-1}_{channel_id}' if pagina != totale_pagine - 1 else f'none')],
        ]
        )

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_publishedlink_{channel_id}')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
    await query.answer()