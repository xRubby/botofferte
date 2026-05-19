import html

from telegram import *
from telegram.ext import *

from database.Entity.Layout import Layout

from database.DAO.LayoutDAO import LayoutDAO

from utils.channel_offers_utils import check_channel_id

(
    ATTESA_NOME_LAYOUT,
    ATTESA_MESSAGGIO_LAYOUT,
    ATTESA_NUOVO_MESSAGGIO_LAYOUT,
) = range(3)

RESET_LAYOUT_MSG=(
    "📦 <b>{titolo}</b>\n"
    "💲 <i>Prezzo vecchio:</i> {old_prezzo}{valuta}\n"
    "💰 <i>Prezzo nuovo:</i> <b>{prezzo}{valuta}</b>\n"
    "📉 <i>Sconto:</i> {sconto}%\n\n"
    "🚚 {spedito}\n\n"
    "🔗 <b>Scopri l'offerta:</b> <a href=\"{link}\">Clicca qui!</a>"
)

def _tag_disponibili_text() -> str:
    tags = [
        "titolo", "prezzo", "old_prezzo", "valuta", "sconto",
        "link", "link_short", "brand", "spedito", "prime",
        "preorder", "data_preordine"
    ]
    return "\n".join(f"- <code>{{{tag}}}</code>" for tag in tags)

async def layout_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)    

    keyboard = [
        [
            InlineKeyboardButton("➕ Nuovo Layout", callback_data=f'channeloffers_addlayout_{channel_id}')
        ],
        [
            InlineKeyboardButton("📋 Seleziona Layout", callback_data=f'channeloffers_showlayouts_{channel_id}'),
            InlineKeyboardButton("✏️ Modifica Layout", callback_data=f'channeloffers_editlayouts_{channel_id}')
        ],
        [
            InlineKeyboardButton("🏷️ Tag", callback_data=f'co_edittags_{channel_id}'),
            InlineKeyboardButton("🖼️ Template Immagine", callback_data=f'layoutimg_menu_{channel_id}')
        ],
        [
            InlineKeyboardButton("⌨️ Tastiera Post", callback_data=f"channeloffers_keyboards_{channel_id}")
        ],
        [
            InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_info_{channel_id}')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=(
            "🎨 <b>Gestione Layout</b>\n\n"
            "Personalizza l’aspetto dei messaggi pubblicati nel tuo canale.\n\n"
            "Seleziona un’opzione per continuare 👇"
        ),
        parse_mode="HTML",
        reply_markup=reply_markup
    )


async def add_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    context.user_data["channel_id"] = channel_id

    keyboard = [
        [InlineKeyboardButton("❌ Annulla", callback_data=f'channeloffers_layout_{channel_id}')]
    ]

    msg = await query.edit_message_text(
        text = (
            "🎨 <b>Nuovo layout</b>\n\n"
            "✏️ Inserisci il nome da assegnare al layout."
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data["msg_id"] = msg.message_id

    return ATTESA_NOME_LAYOUT


async def ricevi_nome_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = context.user_data.get("channel_id")
    message_id = context.user_data.get("msg_id")
    nome_layout = update.message.text

    await update.message.delete()
    context.user_data["nome_layout"] = nome_layout

    keyboard = [
        [InlineKeyboardButton("❌ Annulla", callback_data=f'channeloffers_layout_{channel_id}')]
    ]

    text = (
        f"🎨 <b>Nuovo layout</b>\n\n"
        f"🏷️ <b>Nome:</b> {nome_layout}\n\n"
        "📝 Inserisci il messaggio che verrà utilizzato nel layout.\n\n"
        "🏷️ <b>Tag disponibili:</b>\n"
        + _tag_disponibili_text()
        + "\n\n"
        "🌐 <b>Tag HTML supportati</b>\n"
        "<code>&lt;b&gt;</code> - grassetto\n"
        "<code>&lt;i&gt;</code> - corsivo\n"
        "<code>&lt;code&gt;</code> - codice inline\n"
        "<code>&lt;u&gt;</code> - sottolineato\n"
        "<code>&lt;s&gt;</code> - barrato\n"
        "<code>&lt;blockquote&gt;</code> - citazione\n\n"
        "⚙️ <b>Tag speciali</b>\n"
        "I tag <code>{_</code> e <code>_}</code> permettono di mostrare una parte del messaggio solo se il dato è presente.\n\n"
        "Se uno dei valori è assente, il contenuto tra i tag non verrà mostrato.\n"
        "È possibile usarli anche con più campi contemporaneamente."
    )

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return ATTESA_MESSAGGIO_LAYOUT

async def ricevi_messaggio_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = context.user_data.get("channel_id")
    message_id = context.user_data.get("msg_id")
    nome_layout = context.user_data.get("nome_layout")
    messaggio = update.message.text

    await update.message.delete()

    try:
        with LayoutDAO() as layout_dao:
            layout_dao.insert(nome_layout, messaggio, 0, channel_id)
        text = (
            f"🎨 <b>Layout creato</b>\n\n"
            f"Il layout <b>{nome_layout}</b> è stato creato con successo."
        )
    except Exception as e:
        text = (
            "❌ <b>Creazione fallita</b>\n\n"
            "Si è verificato un errore durante la creazione del layout.\n"
            "Riprova più tardi."
        )

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_layout_{channel_id}')]
    ]

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return ConversationHandler.END

async def annulla_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.pop("msg_id", None)
    context.user_data.pop("channel_id", None)
    context.user_data.pop("nome_layout", None)

    await layout_menu(update, context)
    return ConversationHandler.END

async def show_layouts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    keyboard = []

    with LayoutDAO() as layout_dao:
        layouts = layout_dao.get_channel_layouts(channel_id)
        if layouts:
            text = (
                "🎨 <b>I tuoi layout</b>\n\n"
                f"📊 Layout totali: <b>{len(layouts)}</b>\n\n"
                "Seleziona un layout per gestirlo 👇"
            )
            for layout in layouts:
                emoji_stato = "🟢" if layout.in_uso else "🔴"

                keyboard.append([InlineKeyboardButton(f"{layout.nome_layout}", callback_data=f'none'), InlineKeyboardButton(f"{emoji_stato}", callback_data=f'channeloffers_activatelayout_{channel_id}_{layout.layout_id}')])

        else:
            text = (
                "🎨 <b>Nessun layout presente</b>\n\n"
                "Non hai ancora creato alcun layout.\n\n"
                "➕ Creane uno per iniziare."
            )
            keyboard.append([InlineKeyboardButton("➕ Nuovo Layout", callback_data=f'channeloffers_addlayout_{channel_id}')])

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_layout_{channel_id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
    )

    

async def activate_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    parts = query.data.split("_")
    layout_id = parts[-1]
    context.user_data["channel_id"] = parts[-2]

    with LayoutDAO() as layoutDAO:
        layout = layoutDAO.get(layout_id)

        if not layout:
            text = "⚠️ Errore durante l'attivazione del layout"
        else:   
            id_canale = layout.canale_id

            if(layout.in_uso):
                layoutDAO.update_stato(layout.layout_id, 0)
                text="🔴 Layout disattivato!"
            else:
                layout_old = layoutDAO.get_in_uso(id_canale)
                if layout_old:
                    layoutDAO.update_stato(layout_old.layout_id, 0)
                layoutDAO.update_stato(layout.layout_id, 1)
                text="🟢 Layout selezionato!"
    
    await query.answer(text=text, show_alert=True)

    await show_layouts(update, context)


async def edit_layouts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    keyboard = []

    with LayoutDAO() as layoutDAO:
        layouts = layoutDAO.get_channel_layouts(channel_id)
        if layouts:
            text=(
                "🎨 <b>Modifica layout</b>\n\n"
                "Seleziona un layout da modificare 👇"
            )
            for layout in layouts:
                keyboard.append([InlineKeyboardButton(f"{layout.nome_layout}", callback_data=f'channeloffers_editlayout_{channel_id}_{layout.layout_id}')])

        else:
            text = (
                "🎨 <b>Gestione layout</b>\n\n"
                "Non hai ancora layout creati.\n\n"
                "➕ Aggiungine uno per poterlo modificare."
            )

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_layout_{channel_id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
    )

async def edit_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    layout_id = parts[-1]
    context.user_data["channel_id"] = parts[-2]

    with LayoutDAO() as layout_dao:
        layout = layout_dao.get(layout_id)
    
    safe_message = html.escape(layout.messaggio)
    
    text = (
        f"🎨 <b>Layout selezionato</b>\n\n"
        f"🏷️ <b>{layout.nome_layout}</b>\n\n"
        "📝 <b>Messaggio attuale</b>\n\n"
        f"<code>{safe_message}</code>")

    keyboard = [
        [InlineKeyboardButton("✏️ Modifica Messaggio", callback_data=f'channeloffers_editmessagelayout_{layout.canale_id}_{layout_id}'),InlineKeyboardButton("🗑️ Cancella Layout", callback_data=f'channeloffers_deletelayout_{layout.canale_id}_{layout.layout_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_editlayouts_{layout.canale_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
    )

async def edit_layout_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    layout_id = parts[-1]
    channel_id= parts[-2]

    context.user_data["layout_id"]  = layout_id
    context.user_data["channel_id"] = channel_id

    text = (
        "Modifica Layout\n\n"
        "Tag disponibili:\n"
        + _tag_disponibili_text() +
        "\n\n"
        "🌐 <b>Tag HTML supportati</b>\n"
        "<code>&lt;b&gt;</code> - grassetto\n"
        "<code>&lt;i&gt;</code> - corsivo\n"
        "<code>&lt;code&gt;</code> - codice inline\n"
        "<code>&lt;u&gt;</code> - sottolineato\n"
        "<code>&lt;s&gt;</code> - barrato\n"
        "<code>&lt;blockquote&gt;</code> - citazione\n\n"
        "⚙️ <b>Tag speciali</b>\n"
        "I tag <code>{_</code> e <code>_}</code> permettono di mostrare una parte del messaggio solo se il dato è presente.\n\n"
        "Se uno dei valori è assente, il contenuto tra i tag non verrà mostrato.\n"
        "È possibile usarli anche con più campi contemporaneamente."
    )

    keyboard = [
        [InlineKeyboardButton("♻️ Reset layout", callback_data=f'channeloffers_resetlayout_{channel_id}_{layout_id}')],
        [InlineKeyboardButton("⬅️ Indietro",    callback_data=f'channeloffers_editlayout_{channel_id}_{layout_id}')]
    ]

    msg = await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    context.user_data["msg_id"] = msg.message_id

    return ATTESA_NUOVO_MESSAGGIO_LAYOUT


async def ricevi_nuovo_messaggio_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    layout_id  = context.user_data.get("layout_id")
    channel_id = context.user_data.get("channel_id")
    message_id = context.user_data.get("msg_id")
    nuovo_messaggio = update.message.text

    await update.message.delete()

    try:
        with LayoutDAO() as layoutDAO:
            layoutDAO.update_messaggio(layout_id, nuovo_messaggio)
        text = (
            "✅ <b>Messaggio aggiornato</b>\n\n"
            "Il contenuto del layout è stato aggiornato con successo."
        )
    except Exception as e:
        text = (
            "❌ <b>Aggiornamento fallito</b>\n\n"
            "Si è verificato un errore durante l’aggiornamento del messaggio.\n"
            "Riprova più tardi."
        )

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_editlayout_{channel_id}_{layout_id}')]
    ]

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

    return ConversationHandler.END


async def annulla_edit_messaggio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.pop("msg_id", None)
    context.user_data.pop("layout_id", None)
    context.user_data.pop("channel_id", None)

    await edit_layout(update, context)
    return ConversationHandler.END

async def reset_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    context.user_data.pop("msg_id", None)
    layout_id  = context.user_data.get("layout_id")
    
    try:
        with LayoutDAO() as layoutDAO:
            layoutDAO.update_messaggio(layout_id, RESET_LAYOUT_MSG)
            text = (
                "♻️ Layout resettato con successo.\n\n"
            )
    except Exception as e:
        text = (
            "❌ Non è stato possibile ripristinare il messaggio del layout."
        )

    await query.answer(text, show_alert=True)

    await edit_layout(update, context)

    return ConversationHandler.END

async def delete_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    layout_id = parts[-1]
    channel_id = parts[-2]

    context.user_data["layout_id"] = layout_id
    context.user_data["channel_id"] = channel_id

    keyboard = [
        [
            InlineKeyboardButton("✅ Conferma", callback_data=f'channeloffers_confirmdeletelayout_{channel_id}_{layout_id}'),
            InlineKeyboardButton("❌ Annulla",  callback_data=f'channeloffers_editlayout_{channel_id}_{layout_id}')
        ]
    ]

    text = (
        "🗑️ <b>Elimina layout</b>\n\n"
        "Sei sicuro di voler eliminare questo layout?\n\n"
        "⚠️ <b>Attenzione:</b> questa operazione è irreversibile."
    )

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def confirm_delete_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    layout_id = parts[-1]
    channel_id = parts[-2]

    try:
        with LayoutDAO() as layout_dao:
            layout_dao.delete(layout_id)
        text = (
            "🗑️ <b>Layout eliminato</b>\n\n"
            "Il layout è stato rimosso con successo."
        )
    except Exception as e:
        text = (
            "❌ <b>Eliminazione fallita</b>\n\n"
            "Si è verificato un errore durante la rimozione del layout.\n"
            "Riprova più tardi."
        )

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_editlayouts_{channel_id}')]
    ]

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

conv_layout = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(add_layout, pattern=r'^channeloffers_addlayout_-?\d+$'),
    ],
    states={
        ATTESA_NOME_LAYOUT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_nome_layout),
            CallbackQueryHandler(annulla_layout, pattern=r'^channeloffers_layout_-?\d+$'),
        ],
        ATTESA_MESSAGGIO_LAYOUT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_messaggio_layout),
            CallbackQueryHandler(annulla_layout, pattern=r'^channeloffers_layout_-?\d+$'),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(annulla_layout, pattern=r'^channeloffers_layout_-?\d+$'),
        CallbackQueryHandler(annulla_layout, pattern=r'^channeloffers_info_-?\d+$'),
    ],
    per_message=False,
    per_chat=True,
)

conv_edit_messaggio_layout = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(edit_layout_message, pattern=r'^channeloffers_editmessagelayout_(-?\d+)_(\d+)$'),
    ],
    states={
        ATTESA_NUOVO_MESSAGGIO_LAYOUT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_nuovo_messaggio_layout),
            CallbackQueryHandler(annulla_edit_messaggio, pattern=r'^channeloffers_editlayout_-?\d+_\d+$'),
            CallbackQueryHandler(reset_layout, pattern=r'^channeloffers_resetlayout_-?\d+_\d+$'),
            
        ],
    },
    fallbacks=[
        CallbackQueryHandler(annulla_edit_messaggio, pattern=r'^channeloffers_editlayout_-?\d+_\d+$'),
    ],
    per_message=False,
    per_chat=True,
)