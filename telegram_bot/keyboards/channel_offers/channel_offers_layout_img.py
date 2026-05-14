from telegram import *
from telegram.ext import *

from DTO.ProductConfig import ProductConfig
from database.DAO.LayoutImmagineDAO import LayoutImmagineDAO
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

    await query.edit_message_text(
        text="🖼️ <b>Gestione Immagini Template</b>",
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

    keyboard = [[InlineKeyboardButton("⬅️ Annulla", callback_data=f'layoutimg_menu_{channel_id}')]]

    msg = await query.edit_message_text(
        text=(
            "Invia il template come <b>documento</b> per mantenere la qualità originale.\n\n"
            "Puoi aggiungere un nome al template scrivendolo nella didascalia dell'immagine, "
            "altrimenti verrà usata la dimensione come nome."
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
                text="⚠️ Formato non supportato. Invia solo immagini <b>JPG</b> o <b>PNG</b>.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Annulla", callback_data=f'layoutimg_menu_{channel_id}')]]),
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
            text="⚠️ Invia un'immagine JPG o PNG come documento.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Annulla", callback_data=f'layoutimg_menu_{channel_id}')]]),
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
            text="❌ Impossibile leggere l'immagine. Riprova con un file valido.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Annulla", callback_data=f'layoutimg_menu_{channel_id}')]])
        )
        return ATTESA_TEMPLATE_IMG

    nome = update.message.caption or f"Template {tw}x{th}"

    try:
        with LayoutImmagineDAO() as imgDAO:
            immagine_id = imgDAO.insert(channel_id, nome, template_bytes, tw, th)
        context.user_data["immagine_id"] = immagine_id
        text = (
            f"✅ Template <b>{nome}</b> salvato ({tw}x{th}px)\n\n"
            f"Posizione prodotto: <b>50% x 50%</b>\n"
            f"Dimensioni prodotto: <b>50% x 50%</b>\n\n"
            "Puoi modificare posizione e dimensioni dal menu <b>Modifica immagine</b>."
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
        text = f"🖼️ <b>Template disponibili</b> — totali: {len(immagini)}"
        for img in immagini:
            emoji = "🟢" if img.in_uso else "🔴"
            keyboard.append([
                InlineKeyboardButton(img.nome, callback_data='none'),
                InlineKeyboardButton(emoji, callback_data=f'layoutimg_activate_{channel_id}_{img.immagine_id}')
            ])
    else:
        text = "Nessun template presente. Aggiungine uno prima."

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
            await query.answer("Template non trovato.", show_alert=True)
            return

        if img.in_uso:
            imgDAO.disattiva(channel_id)
            testo_risposta = "Template disattivato!"
        else:
            imgDAO.set_in_uso(immagine_id, channel_id)
            testo_risposta = "Template attivato!"

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
        text = "Seleziona un template da modificare"
        for img in immagini:
            keyboard.append([
                InlineKeyboardButton(img.nome, callback_data=f'layoutimg_editone_{channel_id}_{img.immagine_id}')
            ])
    else:
        text = "Nessun template presente."

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
    immagine_id = int(parts[-1])
    channel_id = parts[-2]

    context.user_data["immagine_id"] = immagine_id
    context.user_data["channel_id"] = channel_id

    with LayoutImmagineDAO() as imgDAO:
        img = imgDAO.get(immagine_id)

    if not img:
        await query.edit_message_text("Template non trovato.")
        return

    text = (
        f"✏️ <b>{img.nome}</b>\n\n"
        f"Dimensioni template: <b>{img.template_w}x{img.template_h}px</b>\n"
        f"Posizione prodotto: <b>{img.prod_x}% x {img.prod_y}%</b>\n"
        f"Dimensioni prodotto: <b>{img.prod_w_pct}% x {img.prod_h_pct}%</b>"
    )

    keyboard = [
        [InlineKeyboardButton("📍 Modifica posizione", callback_data=f'layoutimg_setpos_{channel_id}_{immagine_id}')],
        [InlineKeyboardButton("📐 Modifica dimensioni", callback_data=f'layoutimg_setsize_{channel_id}_{immagine_id}')],
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
    preview_url = "https://m.media-amazon.com/images/I/81XMD4tmSkL._AC_SL1500_.jpg"
    try:

        prodotto = ProductConfig(preview_url, img.prod_x, img.prod_y, img.prod_w_pct, img.prod_h_pct)
        preview_bytes = componi_immagine(img.template_img, prodotto)
        
        preview_msg = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=preview_bytes,
            caption="👆 Anteprima composizione"
        )
        context.user_data["preview_msg_id"] = preview_msg.message_id
    except Exception:
        context.user_data.pop("preview_msg_id", None)

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
    immagine_id = int(parts[-1])
    channel_id = parts[-2]

    context.user_data["immagine_id"] = immagine_id
    context.user_data["channel_id"] = channel_id

    keyboard = [[InlineKeyboardButton("⬅️ Annulla", callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}')]]

    msg = await query.edit_message_text(
        text=(
            "📍 <b>Modifica posizione</b>\n\n"
            "Invia la posizione nel formato: <code>x y</code>\n"
            "I valori sono percentuali (0–100) rispetto alle dimensioni del template.\n\n"
            "Es: <code>50 30</code> → centro orizzontale, 30% dall'alto"
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

    await update.message.delete()

    try:
        parts = update.message.text.strip().split()
        prod_x, prod_y = int(parts[0]), int(parts[1])
        assert 0 <= prod_x <= 100 and 0 <= prod_y <= 100
    except (IndexError, ValueError, AssertionError):
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text="⚠️ Formato non valido. Invia due numeri tra 0 e 100, es: <code>50 30</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Annulla", callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}')]]),
            parse_mode="HTML"
        )
        return ATTESA_SET_POS

    try:
        with LayoutImmagineDAO() as imgDAO:
            imgDAO.update_posizione(immagine_id, prod_x, prod_y)
        text = f"✅ Posizione aggiornata: <b>{prod_x}% x {prod_y}%</b>"
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
    immagine_id = int(parts[-1])
    channel_id = parts[-2]

    context.user_data["immagine_id"] = immagine_id
    context.user_data["channel_id"] = channel_id

    keyboard = [[InlineKeyboardButton("⬅️ Annulla", callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}')]]

    msg = await query.edit_message_text(
        text=(
            "📐 <b>Modifica dimensioni prodotto</b>\n\n"
            "Invia le dimensioni nel formato: <code>larghezza altezza</code>\n"
            "I valori sono percentuali (1–100) rispetto alle dimensioni del template.\n\n"
            "Es: <code>40 40</code> → il prodotto occupa il 40% in larghezza e il 40% in altezza"
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

    await update.message.delete()

    try:
        parts = update.message.text.strip().split()
        prod_w_pct, prod_h_pct = int(parts[0]), int(parts[1])
        assert 0 < prod_w_pct <= 100 and 0 < prod_h_pct <= 100
    except (IndexError, ValueError, AssertionError):
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text="⚠️ Formato non valido. Invia due numeri tra 1 e 100, es: <code>40 40</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Annulla", callback_data=f'layoutimg_editone_{channel_id}_{immagine_id}')]]),
            parse_mode="HTML"
        )
        return ATTESA_SET_SIZE

    try:
        with LayoutImmagineDAO() as imgDAO:
            imgDAO.update_dimensioni(immagine_id, prod_w_pct, prod_h_pct)
        text = f"✅ Dimensioni aggiornate: <b>{prod_w_pct}% x {prod_h_pct}%</b>"
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
        text="Sei sicuro di voler eliminare questo template?\n\n⚠️ L'operazione è irreversibile.",
        reply_markup=InlineKeyboardMarkup(keyboard)
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
        text = "✅ Template eliminato con successo."
    except Exception:
        text = "❌ Errore durante l'eliminazione."

    keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data=f'layoutimg_edit_{channel_id}')]]

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
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
        CallbackQueryHandler(set_pos_start, pattern=r'^layoutimg_setpos_-?\d+_\d+$'),
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
        CallbackQueryHandler(set_size_start, pattern=r'^layoutimg_setsize_-?\d+_\d+$'),
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