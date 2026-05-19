from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)

from DTO.ProductConfig import ProductConfig
from DTO.TextConfig import TextConfig
from database.DAO.LayoutImmagineDAO import LayoutImmagineDAO
from database.Entity.LayoutImmagine import LayoutImmagine
from utils.channel_offers_utils import check_channel_id
from utils.image_composer import componi_immagine, leggi_dimensioni_template

(
    ATTESA_TEMPLATE_IMG,
    ATTESA_NOME_IMMAGINE,
    ATTESA_SET_POS,
    ATTESA_SET_SIZE,
) = range(4)

# ──────────────────────────────────────────────
# MENU PRINCIPALE
# ──────────────────────────────────────────────

async def immagine_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    keyboard = [
        [InlineKeyboardButton("➕ Aggiungi immagine", callback_data=f'layoutimg_add_{channel_id}')],
        [InlineKeyboardButton("🖼️ Seleziona immagine", callback_data=f'layoutimg_show_{channel_id}'), InlineKeyboardButton("✏️ Modifica immagine",  callback_data=f'layoutimg_edit_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_layout_{channel_id}')]
    ]

    text = (
        "🖼️ <b>Immagini template</b>\n\n"
        "Gestisci i template grafici utilizzati nei post delle offerte.\n\n"
        "Scegli un’azione 👇"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

# ──────────────────────────────────────────────
# AGGIUNGI IMMAGINE
# ──────────────────────────────────────────────

async def add_immagine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    context.user_data["channel_id"] = channel_id

    keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data=f'layoutimg_menu_{channel_id}')]]

    msg = await query.edit_message_text(
        text = (
            "🖼️ <b>Nuovo template</b>\n\n"
            "📤 Carica il template come <b>documento</b> per evitare perdita di qualità.\n\n"
            "🏷️ Aggiungi un nome nella didascalia (opzionale).\n"
            "Se non specificato, verrà usata la dimensione come nome."
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    context.user_data["msg_id"] = msg.message_id

    return ATTESA_TEMPLATE_IMG


async def ricevi_template_img(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = context.user_data.get("channel_id")
    message_id = context.user_data.get("msg_id")

    await update.message.delete()

    FORMATI_ACCETTATI = {"image/jpeg", "image/png"}

    if update.message.document:
        if update.message.document.mime_type not in FORMATI_ACCETTATI:
            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=message_id,
                text=(
                    "⚠️ <b>Formato non supportato</b>\n\n"
                    "Invia un’immagine nei formati <b>JPG</b> o <b>PNG</b>."
                ),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annulla", callback_data=f'layoutimg_menu_{channel_id}')]]),
                parse_mode="HTML"
            )
            return ATTESA_TEMPLATE_IMG
        file = await context.bot.get_file(update.message.document.file_id)
    elif update.message.photo:
        file = await context.bot.get_file(update.message.photo[-1].file_id)
    else:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text=(
                "⚠️ <b>Formato non valido</b>\n\n"
                "Invia un’immagine in formato <b>JPG</b> o <b>PNG</b> come <b>documento</b>."
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annulla", callback_data=f'layoutimg_menu_{channel_id}')]]),
            parse_mode="HTML"
        )
        return ATTESA_TEMPLATE_IMG

    template_bytes = bytes(await file.download_as_bytearray())

    try:
        tw, th = leggi_dimensioni_template(template_bytes)
    except Exception:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text=(
                "❌ <b>Errore di elaborazione</b>\n\n"
                "Non è stato possibile leggere l’immagine.\n"
                "Assicurati che il file sia valido e riprova."
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annulla", callback_data=f'layoutimg_menu_{channel_id}')]])
        )
        return ATTESA_TEMPLATE_IMG

    nome = update.message.caption or f"Template {tw}x{th}"

    try:
        with LayoutImmagineDAO() as imgDAO:
            immagine_id = imgDAO.insert(channel_id, nome, template_bytes, tw, th)
        context.user_data["immagine_id"] = immagine_id
        text = (
            f"🖼️ <b>Template salvato</b>\n\n"
            f"🏷️ Nome: <b>{nome}</b>\n"
            f"📐 Dimensioni: <b>{tw}x{th}px</b>\n\n"
            "📦 <b>Prodotto</b>\n"
            "• Posizione: <b>50% x 50%</b>\n"
            "• Dimensioni: <b>50% x 50%</b>\n\n"
            "⚙️ Puoi modificare questi parametri dal menu <b>Modifica immagine</b>."
        )
    except Exception:
        text = "❌ Errore durante il salvataggio del template."

    keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data=f'layoutimg_menu_{channel_id}')]]

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return ConversationHandler.END


async def annulla_add_immagine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("msg_id", None)
    context.user_data.pop("channel_id", None)
    await immagine_menu(update, context)
    return ConversationHandler.END

# ──────────────────────────────────────────────
# SELEZIONA / ATTIVA IMMAGINE
# ──────────────────────────────────────────────

async def show_immagini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    keyboard = []

    with LayoutImmagineDAO() as imgDAO:
        immagini = imgDAO.get_by_canale(channel_id)

    if immagini:
        text = (
            "🖼️ <b>Template disponibili</b>\n\n"
            f"📊 Totale: <b>{len(immagini)}</b>\n\n"
            "Scegli un template per attivarlo 👇"
        )
        for img in immagini:
            emoji = "🟢" if img.in_uso else "🔴"
            keyboard.append([
                InlineKeyboardButton(img.nome, callback_data='none'),
                InlineKeyboardButton(emoji, callback_data=f'layoutimg_activate_{channel_id}_{img.immagine_id}')
            ])
    else:
        text = (
            "🖼️ <b>Nessun template disponibile</b>\n\n"
            "Non hai ancora caricato alcun template.\n\n"
            "➕ Aggiungine uno per iniziare."
        )
        keyboard.append([InlineKeyboardButton("➕ Aggiungi immagine", callback_data=f'layoutimg_add_{channel_id}')])

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'layoutimg_menu_{channel_id}')])

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def activate_immagine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    parts = query.data.split("_")
    immagine_id = int(parts[-1])
    channel_id = parts[-2]

    with LayoutImmagineDAO() as imgDAO:
        img = imgDAO.get(immagine_id)
        if not img:
            await query.answer("⚠️ Template non trovato.", show_alert=True)
            return

        if img.in_uso:
            imgDAO.disattiva(channel_id)
            testo_risposta = "🔴 Template disattivato!"
        else:
            imgDAO.set_in_uso(immagine_id, channel_id)
            testo_risposta = "🟢 Template attivato!"

    await query.answer(testo_risposta, show_alert=True)
    await show_immagini(update, context)

# ──────────────────────────────────────────────
# MODIFICA IMMAGINE — lista
# ──────────────────────────────────────────────

async def edit_immagini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Cancella la preview se presente
    preview_msg_id = context.user_data.pop("preview_msg_id", None)
    if preview_msg_id:
        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=preview_msg_id
            )
        except Exception:
            pass

    channel_id = check_channel_id(query, context)
    keyboard = []

    with LayoutImmagineDAO() as imgDAO:
        immagini = imgDAO.get_by_canale(channel_id)

    if immagini:
        text = (
            "🖼️ <b>Modifica template</b>\n\n"
            "Seleziona un template da modificare 👇"
        )
        for img in immagini:
            keyboard.append([
                InlineKeyboardButton(img.nome, callback_data=f'layoutimg_editone_{channel_id}_{img.immagine_id}')
            ])
    else:
        text = (
            "🖼️ <b>Nessun template disponibile</b>\n\n"
            "Non hai ancora caricato alcun template.\n\n"
            "➕ Aggiungine uno per iniziare."
        )
        keyboard.append([InlineKeyboardButton("➕ Aggiungi immagine", callback_data=f'layoutimg_add_{channel_id}')])

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'layoutimg_menu_{channel_id}')])

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


# ──────────────────────────────────────────────
# MODIFICA IMMAGINE — dettaglio singolo
# ──────────────────────────────────────────────

async def edit_immagine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    immagine_id = int(parts[3])
    channel_id = parts[2]

    context.user_data["immagine_id"] = immagine_id
    context.user_data["channel_id"] = channel_id

    with LayoutImmagineDAO() as imgDAO:
        img = imgDAO.get(immagine_id)

    if not img:
        await query.edit_message_text("⚠️ Template non trovato.")
        return
    
    context.user_data["img"] = img

    text = (
        "🖼️ <b>Editor template</b>\n\n"
        f"🏷️ <b>{img.nome}</b>\n\n"
        f"📐 {img.template_w} x {img.template_h}px"
    )

    keyboard = [
        [InlineKeyboardButton("📦 Prodotto", callback_data=f"layoutimg_prodottomenu_{channel_id}_{immagine_id}"), InlineKeyboardButton("💰 Prezzo", callback_data=f"layoutimg_prezzomenu_{channel_id}_{immagine_id}")],
        [InlineKeyboardButton("💶 Prezzo consigliato", callback_data=f"layoutimg_prezzooldmenu_{channel_id}_{immagine_id}"), InlineKeyboardButton("🛍️ Sconto", callback_data=f"layoutimg_scontomenu_{channel_id}_{immagine_id}")],
        [InlineKeyboardButton("🗑️ Elimina", callback_data=f'layoutimg_delete_{channel_id}_{immagine_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'layoutimg_edit_{channel_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Aggiorna il messaggio principale (testo)
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

    # Manda la preview come messaggio separato
    preview_url = "https://m.media-amazon.com/images/I/61Xd7yu2MnL._AC_SL1500_.jpg"
    try:

        prodotto = ProductConfig(preview_url, img.prod_x, img.prod_y, img.prod_w_pct, img.prod_h_pct)
        prezzo = TextConfig("122,99€", img.prezzo_x, img.prezzo_y, img.prezzo_w_pct, img.prezzo_h_pct, img.prezzo_active)
        prezzo_old = TextConfig("149,98€", img.prezzo_old_x, img.prezzo_old_y, img.prezzo_old_w_pct, img.prezzo_old_h_pct, img.prezzo_old_active)
        sconto = TextConfig("-18%", img.sconto_x, img.sconto_y, img.sconto_w_pct, img.sconto_h_pct, img.sconto_active)
        preview_bytes = componi_immagine(img.template_img, prodotto, prezzo, prezzo_old, sconto)
        
        if not context.user_data.get("preview_msg_id"):
            preview_msg = await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=preview_bytes,
                caption="👆 Anteprima composizione"
            )
            context.user_data["preview_msg_id"] = preview_msg.message_id
    except Exception:
        context.user_data.pop("preview_msg_id", None)


async def layoutimg_prodotto_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    immagine_id = int(parts[3])
    channel_id = parts[2]

    tasto_indietro = [[
        InlineKeyboardButton(
            "⬅️ Indietro",
            callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}'
        )
    ]]

    with LayoutImmagineDAO() as imgDAO:
        img = imgDAO.get(immagine_id)
    if not img:
        await query.edit_message_text("Template non trovato.", reply_markup=InlineKeyboardMarkup(tasto_indietro))
        return

    text = (
        "🖼️ <b>Modifica prodotto</b>\n\n"
        "📍 <b>Posizione</b>\n"
        f"{img.prod_x}% x {img.prod_y}%\n\n"
        "📐 <b>Dimensioni</b>\n"
        f"{img.prod_w_pct}% x {img.prod_h_pct}%\n"
    )
    keyboard = [
        [InlineKeyboardButton("📍 Modifica Posizione", callback_data=f'layoutimg_setpos_{channel_id}_{immagine_id}_prodotto'), InlineKeyboardButton("📐 Modifica Dimensioni", callback_data=f'layoutimg_setsize_{channel_id}_{immagine_id}_prodotto')],
    ]
    keyboard.extend(tasto_indietro)

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def layoutimg_attr_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    immagine_id = int(parts[3])
    channel_id = parts[2]
    tipo = parts[1]

    tasto_indietro = [[
        InlineKeyboardButton(
            "⬅️ Indietro",
            callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}'
        )
    ]]

    with LayoutImmagineDAO() as imgDAO:
        img = imgDAO.get(immagine_id)
    if not img:
        await query.edit_message_text("Template non trovato.", reply_markup=InlineKeyboardMarkup(tasto_indietro))
        return
    
    keyboard = []

    if tipo == "prezzomenu":
        text = (
            "💰 <b>Modifica prezzo</b>\n\n"
            f"⚙️ Stato: <b>{'Attivo' if img.prezzo_active else 'Non attivo'}</b>\n\n"
            "📍 <b>Posizione</b>\n"
            f"{img.prezzo_x}% x {img.prezzo_y}%\n\n"
            "📐 <b>Dimensioni</b>\n"
            f"{img.prezzo_w_pct}% x {img.prezzo_h_pct}%"
        )

        keyboard = [[InlineKeyboardButton("🔴 Disattiva Prezzo" if img.prezzo_active else "🟢 Attiva Prezzo", callback_data=f"layoutimg_activateattr_{channel_id}_{immagine_id}_prezzo")],
            [InlineKeyboardButton("📍 Modifica Posizione", callback_data=f'layoutimg_setpos_{channel_id}_{immagine_id}_prezzo'), InlineKeyboardButton("📐 Modifica Dimensioni", callback_data=f'layoutimg_setsize_{channel_id}_{immagine_id}_prezzo')]
        ]
    elif tipo == "prezzooldmenu":
        text = (
            "💸 <b>Modifica prezzo consigliato</b>\n\n"
            f"⚙️ Stato: <b>{'Attivo' if img.prezzo_old_active else 'Non attivo'}</b>\n\n"
            "📍 <b>Posizione</b>\n"
            f"{img.prezzo_old_x}% x {img.prezzo_old_y}%\n\n"
            "📐 <b>Dimensioni</b>\n"
            f"{img.prezzo_old_w_pct}% x {img.prezzo_old_h_pct}%"
        )

        keyboard = [
            [InlineKeyboardButton("🔴 Disattiva Prezzo Consigliato" if img.prezzo_old_active else "🟢 Attiva Prezzo Consigliato", callback_data=f"layoutimg_activateattr_{channel_id}_{immagine_id}_prezzoold")],
            [InlineKeyboardButton("📍 Modifica Posizione", callback_data=f'layoutimg_setpos_{channel_id}_{immagine_id}_prezzoold'), InlineKeyboardButton("📐 Modifica Dimensioni", callback_data=f'layoutimg_setsize_{channel_id}_{immagine_id}_prezzoold')]
        ]

    elif tipo == "scontomenu":
        text = (
            "🔥 <b>Modifica sconto</b>\n\n"
            f"⚙️ Stato: <b>{'Attivo' if img.sconto_active else 'Non attivo'}</b>\n\n"
            "📍 <b>Posizione</b>\n"
            f"{img.sconto_x}% x {img.sconto_y}%\n\n"
            "📐 <b>Dimensioni</b>\n"
            f"{img.sconto_w_pct}% x {img.sconto_h_pct}%"
        )

        keyboard = [
            [InlineKeyboardButton("🔴 Disattiva Sconto" if img.sconto_active else "🟢 Attiva Sconto", callback_data=f"layoutimg_activateattr_{channel_id}_{immagine_id}_sconto")],
            [InlineKeyboardButton("📍 Modifica Posizione", callback_data=f'layoutimg_setpos_{channel_id}_{immagine_id}_sconto'), InlineKeyboardButton("📐 Modifica Dimensioni", callback_data=f'layoutimg_setsize_{channel_id}_{immagine_id}_sconto')],
        ]
    else:
        await query.edit_message_text("Tipo non trovato", reply_markup=InlineKeyboardMarkup(tasto_indietro))
        return
    
    keyboard.extend(tasto_indietro)

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

# ──────────────────────────────────────────────
# SET POSIZIONE
# ──────────────────────────────────────────────

async def set_pos_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    preview_msg_id = context.user_data.pop("preview_msg_id", None)
    if preview_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=preview_msg_id)
        except Exception:
            pass

    parts = query.data.split("_")
    tipo = parts[4]
    immagine_id = int(parts[3])
    channel_id = parts[2]

    context.user_data["immagine_id"] = immagine_id
    context.user_data["channel_id"] = channel_id
    context.user_data["tipo"] = tipo

    keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}')]]

    msg = await query.edit_message_text(
        text = (
            "📍 <b>Modifica posizione</b>\n\n"
            "✏️ Invia la nuova posizione nel formato:\n"
            "<code>x y</code>\n\n"
            "📊 Valori in percentuale (0–100)\n"
            "Rispetto alle dimensioni del template\n\n"
            "💡 Esempio:\n"
            "<code>50 30</code> → centro orizzontale, 30% dall’alto"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    context.user_data["msg_id"] = msg.message_id

    return ATTESA_SET_POS


async def ricevi_set_pos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    immagine_id = context.user_data.get("immagine_id")
    channel_id  = context.user_data.get("channel_id")
    message_id  = context.user_data.get("msg_id")
    tipo = context.user_data.get("tipo")

    await update.message.delete()

    try:
        parts = update.message.text.strip().split()
        x_pct, y_pct = int(parts[0]), int(parts[1])
        assert 0 <= x_pct <= 100 and 0 <= y_pct <= 100
    except (IndexError, ValueError, AssertionError):
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text="⚠️ Formato non valido. Invia due numeri tra 0 e 100, es: <code>50 30</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annulla", callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}')]]),
            parse_mode="HTML"
        )
        return ATTESA_SET_POS

    try:
        mapping = {
            "prodotto": "update_posizione_prodotto",
            "prezzo": "update_posizione_prezzo",
            "prezzoold": "update_posizione_prezzoold",
            "sconto": "update_posizione_sconto",
        }

        metodo = mapping.get(tipo)
        if not metodo:
            raise ValueError(f"Tipo non valido: {tipo}")

        with LayoutImmagineDAO() as imgDAO:
            getattr(imgDAO, metodo)(immagine_id, x_pct, y_pct)

        text = f"✅ Dimensioni aggiornate: <b>{x_pct}% x {y_pct}%</b>"
    except Exception:
        text = "❌ Errore durante l'aggiornamento della posizione."

    keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}')]]

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return ConversationHandler.END

async def _annulla_set_pos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await edit_immagine(update, context)
    return ConversationHandler.END


# ──────────────────────────────────────────────
# SET DIMENSIONI
# ──────────────────────────────────────────────

async def set_size_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    preview_msg_id = context.user_data.pop("preview_msg_id", None)
    if preview_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=preview_msg_id)
        except Exception:
            pass

    parts = query.data.split("_")
    tipo = parts[4]
    immagine_id = int(parts[3])
    channel_id = parts[2]


    context.user_data["immagine_id"] = immagine_id
    context.user_data["channel_id"] = channel_id
    context.user_data["tipo"] = tipo

    keyboard = [[InlineKeyboardButton("❌ Annulla", callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}')]]

    msg = await query.edit_message_text(
        text = (
            "📐 <b>Modifica dimensioni</b>\n\n"
            "✏️ Invia le nuove dimensioni nel formato:\n"
            "<code>larghezza altezza</code>\n\n"
            "📊 Valori in percentuale (1–100)\n"
            "Rispetto alle dimensioni del template\n\n"
            "💡 Esempio:\n"
            "<code>40 40</code> → 40% larghezza e 40% altezza"
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    context.user_data["msg_id"] = msg.message_id

    return ATTESA_SET_SIZE


async def ricevi_set_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    immagine_id = context.user_data.get("immagine_id")
    channel_id  = context.user_data.get("channel_id")
    message_id  = context.user_data.get("msg_id")
    tipo = context.user_data.get("tipo")

    await update.message.delete()

    try:
        parts = update.message.text.strip().split()
        w_pct, h_pct = int(parts[0]), int(parts[1])
        assert 0 < w_pct <= 100 and 0 < h_pct <= 100
    except (IndexError, ValueError, AssertionError):
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text="⚠️ Formato non valido. Invia due numeri tra 1 e 100, es: <code>40 40</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Annulla", callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}')]]),
            parse_mode="HTML"
        )
        return ATTESA_SET_SIZE

    try:
        mapping = {
            "prodotto": "update_dimensioni_prodotto",
            "prezzo": "update_dimensioni_prezzo",
            "prezzoold": "update_dimensioni_prezzoold",
            "sconto": "update_dimensioni_sconto",
        }

        metodo = mapping.get(tipo)
        if not metodo:
            raise ValueError(f"Tipo non valido: {tipo}")

        with LayoutImmagineDAO() as imgDAO:
            getattr(imgDAO, metodo)(immagine_id, w_pct, h_pct)

        text = f"✅ Dimensioni aggiornate: <b>{w_pct}% x {h_pct}%</b>"
    except Exception:
        text = "❌ Errore durante l'aggiornamento delle dimensioni."

    keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}')]]

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return ConversationHandler.END

async def _annulla_set_size(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await edit_immagine(update, context)
    return ConversationHandler.END


# ──────────────────────────────────────────────
# ATTIVA/DISATTIVA ATTRIBUTI IMMAGINE
# ──────────────────────────────────────────────
async def activate_attr_img(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    preview_msg_id = context.user_data.pop("preview_msg_id", None)
    if preview_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=preview_msg_id)
        except Exception:
            pass

    parts = query.data.split("_")
    immagine_id = int(parts[3])
    tipo = parts[4]
    with LayoutImmagineDAO() as imgDAO:
        img = imgDAO.get(immagine_id)
        if not img:
            await query.answer("⚠️ Layout immagine non trovata.", show_alert=True)
            return

        if tipo == "prezzo":
            if img.prezzo_active:
                imgDAO.disattiva_prezzo(immagine_id)
                testo_risposta = "🔴 Prezzo disattivato!"
            else:
                imgDAO.attiva_prezzo(immagine_id)
                testo_risposta = "🟢 Prezzo attivato!"
        elif tipo == "prezzoold":
            if img.prezzo_old_active:
                imgDAO.disattiva_prezzo_old(immagine_id)
                testo_risposta = "🔴 Prezzo consigliato disattivato!"
            else:
                imgDAO.attiva_prezzo_old(immagine_id)
                testo_risposta = "🟢 Prezzo consigliato attivato!"
        elif tipo == "sconto":
            if img.sconto_active:
                imgDAO.disattiva_sconto(immagine_id)
                testo_risposta = "🔴 Sconto disattivato!"
            else:
                imgDAO.attiva_sconto(immagine_id)
                testo_risposta = "🟢 Sconto attivato!"
        else:
            testo_risposta = "⚠️ Attributo non trovato."

    await query.answer(testo_risposta, show_alert=True)
    await edit_immagine(update, context)

# ──────────────────────────────────────────────
# ELIMINA IMMAGINE
# ──────────────────────────────────────────────

async def delete_immagine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    preview_msg_id = context.user_data.pop("preview_msg_id", None)
    if preview_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=preview_msg_id)
        except Exception:
            pass

    parts = query.data.split("_")
    immagine_id = int(parts[-1])
    channel_id = parts[-2]

    keyboard = [
        [
            InlineKeyboardButton("✅ Conferma", callback_data=f'layoutimg_confirmdelete_{channel_id}_{immagine_id}'),
            InlineKeyboardButton("❌ Annulla",  callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}')
        ]
    ]

    await query.edit_message_text(
        text = (
            "🖼️ <b>Elimina template</b>\n\n"
            "Sei sicuro di voler eliminare questo template?\n\n"
            "⚠️ <b>Attenzione:</b> l’operazione è irreversibile."
        ),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def confirm_delete_immagine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    immagine_id = int(parts[-1])
    channel_id = parts[-2]

    try:
        with LayoutImmagineDAO() as imgDAO:
            imgDAO.delete(immagine_id)
        text = (
            "🗑️ <b>Template eliminato</b>\n\n"
            "Il template è stato rimosso con successo."
        )
    except Exception:
        text = (
            "❌ <b>Eliminazione fallita</b>\n\n"
            "Non è stato possibile eliminare il template.\n"
            "Riprova più tardi."
        )

    keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data=f'layoutimg_edit_{channel_id}')]]

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


conv_add_immagine = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(add_immagine, pattern=r'^layoutimg_add_-?\d+$'),
    ],
    states={
        ATTESA_TEMPLATE_IMG: [
            MessageHandler(filters.PHOTO | filters.Document.IMAGE, ricevi_template_img),
            CallbackQueryHandler(annulla_add_immagine, pattern=r'^layoutimg_menu_-?\d+$'),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(annulla_add_immagine, pattern=r'^layoutimg_menu_-?\d+$'),
    ],
    per_message=False,
    per_chat=True,
)

conv_set_pos = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(set_pos_start, pattern=r'^layoutimg_setpos_-?\d+_\d+_[a-zA-Z]+$'),
    ],
    states={
        ATTESA_SET_POS: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_set_pos),
            CallbackQueryHandler(_annulla_set_pos, pattern=r'^layoutimg_editone_-?\d+_\d+$'),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(_annulla_set_pos, pattern=r'^layoutimg_editone_-?\d+_\d+$'),
    ],
    per_message=False,
    per_chat=True,
)

conv_set_size = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(set_size_start, pattern=r'^layoutimg_setsize_-?\d+_\d+_[a-zA-Z]+$'),
    ],
    states={
        ATTESA_SET_SIZE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_set_size),
            CallbackQueryHandler(_annulla_set_size, pattern=r'^layoutimg_editone_-?\d+_\d+$'),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(_annulla_set_size, pattern=r'^layoutimg_editone_-?\d+_\d+$'),
    ],
    per_message=False,
    per_chat=True,
)