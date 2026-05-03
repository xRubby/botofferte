from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler, ContextTypes, ConversationHandler,
    MessageHandler, filters
)
from database.DAO.LicenzaDAO import LicenzaDAO
from utils.StatoLicenza import StatoLicenza
from utils.generate_license import calcola_tipo_scadenza, generate_license

ADMIN_MENU_MSG = "PANNELLO ADMIN"
LICENZE_GENERATE_MSG = "📋 *Lista licenze*"

LICENZE_PER_PAGINA = 5

ATTESA_TIPO_LICENZA = 1


async def admin_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("Genera Licenza", callback_data='generate_license')],
        [InlineKeyboardButton("Vedi Licenze", callback_data='admin_settings_visualizzalicenze_0')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data='settings')],
    ]
    await query.edit_message_text(
        text=ADMIN_MENU_MSG,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def generate_new_license(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    ctx.user_data['license_message_id'] = query.message.message_id
    ctx.user_data['license_chat_id'] = query.message.chat_id

    text = (
        "Inserisci il tipo della licenza. "
        "Puoi usare anche i tasti rapidi qui sotto.\n\n"
        "Esempi: <code>2 mesi</code>, <code>3 anni</code>"
    )
    keyboard = [
        [
            InlineKeyboardButton("1 Settimana", callback_data='admin_settings_generatelicense_7'),
            InlineKeyboardButton("30 Giorni", callback_data='admin_settings_generatelicense_30')
        ],
        [InlineKeyboardButton("⬅️ Indietro", callback_data='admin_settings')]
    ]
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ATTESA_TIPO_LICENZA


async def genera_licenza_da_testo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    tipo_licenza = update.message.text.strip()

    await update.message.delete()

    await _crea_licenza(
        tipo_licenza=tipo_licenza,
        chat_id=ctx.user_data.pop("license_chat_id", None),
        message_id=ctx.user_data.pop("license_message_id", None),
        ctx=ctx
    )
    return ConversationHandler.END


async def generate_license_days(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    days = int(query.data.split("_")[-1])
    tipo_licenza_map = {7: "1 settimana", 30: "30 giorni"}
    tipo_licenza = tipo_licenza_map.get(days)
    if not tipo_licenza:
        await query.answer("Tipo non valido", show_alert=True)
        return annulla_generazione(update, ctx)

    await query.answer()

    await _crea_licenza(
        tipo_licenza=tipo_licenza,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        ctx=ctx,
        query=query
    )
    return ConversationHandler.END


async def annulla_generazione(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await admin_menu(update, ctx)
    return ConversationHandler.END


async def _crea_licenza(
    tipo_licenza: str,
    chat_id: int,
    message_id: int,
    ctx: ContextTypes.DEFAULT_TYPE,
    query=None
):
    keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data='admin_settings')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if calcola_tipo_scadenza(tipo_licenza):
        codice_licenza = generate_license()
        with LicenzaDAO() as licenza_dao:
            licenza_dao.insert(codice_licenza, tipo_licenza)
        text = f"Licenza con codice <code>{codice_licenza}</code> generata correttamente!"
    else:
        text = "Il tipo della licenza è errato!"

    if query:
        await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=reply_markup)
    else:
        await ctx.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

async def visualizza_licenze(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pagina = int(query.data.split("_")[-1]) if query.data.startswith("admin_settings_visualizzalicenze_") else 0

    with LicenzaDAO() as licenza_dao:
        licenze, totale = licenza_dao.get_paginated(pagina, LICENZE_PER_PAGINA)

    if not licenze:
        tastiera = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Indietro", callback_data="admin_settings")],
        ])
        await query.edit_message_text(
            "📋 *Lista licenze*\n\nNessuna licenza disponibile",
            parse_mode="Markdown",
            reply_markup=tastiera,
        )
        return

    tastiera = [
        [InlineKeyboardButton(l.codice_licenza, callback_data=f"admin_settings_dettaglilicenza_{l.codice_licenza}")]
        for l in licenze
    ]

    n_pagine = -(-totale // LICENZE_PER_PAGINA)
    nav = []
    if pagina > 0:
        if n_pagine >= 3:
            nav.append(InlineKeyboardButton("⏮️", callback_data="admin_settings_visualizzalicenze_0"))
        nav.append(InlineKeyboardButton("◀️ Prec", callback_data=f"admin_settings_visualizzalicenze_{pagina - 1}"))
    if (pagina + 1) * LICENZE_PER_PAGINA < totale:
        nav.append(InlineKeyboardButton("Succ ▶️", callback_data=f"admin_settings_visualizzalicenze_{pagina + 1}"))
        if n_pagine >= 3:
            nav.append(InlineKeyboardButton("⏭️", callback_data=f"admin_settings_visualizzalicenze_{n_pagine - 1}"))

    if nav:
        tastiera.append(nav)
    tastiera.append([InlineKeyboardButton("🔙 Indietro", callback_data="admin_settings")])

    await query.edit_message_text(
        text=LICENZE_GENERATE_MSG,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(tastiera)
    )

async def dettagli_licenza(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    codice_licenza = query.data.removeprefix("admin_settings_dettaglilicenza_")

    with LicenzaDAO() as licenza_dao:
        licenza, stato, canale_id, nome_canale = licenza_dao.get_dettagli(codice_licenza)

    stato_map = {
        StatoLicenza.ATTIVA:       "🟢 Attiva",
        StatoLicenza.NON_ATTIVATA: "⚪️ Non ancora attivata",
        StatoLicenza.SCADUTA:      "🔴 Scaduta",
        StatoLicenza.DISATTIVATA:  "⛔️ Disattivata dall'admin",
    }
    stato_text = stato_map[stato]

    if not licenza:
        await query.edit_message_text(
            text="❌ Licenza non trovata.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Indietro", callback_data="admin_settings_visualizzalicenze_0")]
            ])
        )
        return

    text = (
        f"🔑 <b>Licenza</b>: <code>{licenza.codice_licenza}</code>\n"
        f"📦 <b>Tipo</b>: {licenza.tipo.title()}\n"
        f"📊 <b>Stato</b>: {stato_text}\n"
    )

    if licenza.data_attivazione:
        text += (
            f"\n📅 <b>Attivazione</b>: {licenza.data_attivazione}\n"
            f"⏳ <b>Scadenza</b>: {licenza.data_scadenza or 'Nessuna'}\n"
        )

    if canale_id:
        text += (
            f"\n📢 <b>Canale associato</b>: {nome_canale}\n"
            f"<i>(ID: {canale_id})</i>"
        )
    else:
        text += "\n📢 <b>Canale</b>: licenza non attivata da nessun canale"

    if stato == StatoLicenza.DISATTIVATA:
        azione_btn = InlineKeyboardButton("✅ Riattiva Licenza", callback_data=f"admin_settings_attivalicenza_{licenza.codice_licenza}")
    else:
        azione_btn = InlineKeyboardButton("🚫 Disattiva Licenza", callback_data=f"admin_settings_disattivalicenza_{licenza.codice_licenza}")

    keyboard = [
        [azione_btn],
        [InlineKeyboardButton("🔙 Indietro", callback_data="admin_settings_visualizzalicenze_0")],
    ]

    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def disattiva_licenza_confirm(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    codice_licenza = query.data.removeprefix("admin_settings_disattivalicenza_")
    text = (
        f"⚠️ <b>Sei sicuro di voler disattivare la licenza?</b>\n\n"
        f"🔑 <code>{codice_licenza}</code>\n\n"
        f"La licenza non sarà più utilizzabile da nessun canale."
    )
    keyboard = [
        [
            InlineKeyboardButton("✅ Sì, disattiva", callback_data=f"admin_settings_disattiva_ok_{codice_licenza}"),
            InlineKeyboardButton("❌ Annulla", callback_data=f"admin_settings_dettaglilicenza_{codice_licenza}"),
        ]
    ]
    await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))


async def disattiva_licenza_ok(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    codice_licenza = query.data.removeprefix("admin_settings_disattiva_ok_")
    with LicenzaDAO() as licenza_dao:
        licenza_dao.disattiva(codice_licenza)
    text = f"🚫 Licenza <code>{codice_licenza}</code> disattivata."
    keyboard = [[InlineKeyboardButton("🔙 Indietro", callback_data=f"admin_settings_dettaglilicenza_{codice_licenza}")]]
    await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))


async def attiva_licenza_ok(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    codice_licenza = query.data.removeprefix("admin_settings_attivalicenza_")
    with LicenzaDAO() as licenza_dao:
        licenza_dao.attiva(codice_licenza)
    text = f"✅ Licenza <code>{codice_licenza}</code> riattivata."
    keyboard = [[InlineKeyboardButton("🔙 Indietro", callback_data=f"admin_settings_dettaglilicenza_{codice_licenza}")]]
    await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

# --- ConversationHandler ---
conv_genera_licenza = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(generate_new_license, pattern='^generate_license$')
    ],
    states={
        ATTESA_TIPO_LICENZA: [
            CallbackQueryHandler(generate_license_days, pattern=r'^admin_settings_generatelicense_\d+$'),
        
            CallbackQueryHandler(annulla_generazione, pattern='^admin_settings$'),
            
            MessageHandler(filters.TEXT & ~filters.COMMAND, genera_licenza_da_testo),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(annulla_generazione, pattern='^admin_settings$')
    ],
    per_message=False,
    per_chat=True,
)