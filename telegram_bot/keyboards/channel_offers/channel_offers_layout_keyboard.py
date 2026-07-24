from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from database.session import SessionLocal
from models.tastiera import Tastiera
from services.tastiera_service import TastieraService
from utils.channel_offers_utils import check_channel_id

ATTESA_NOME, ATTESA_MESSAGGIO = range(2)
ATTESA_NUOVO_MESSAGGIO = range(1)

async def keyboard_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    text = (
        "⌨️ <b>Tastiera Post</b>\n\n"
        "Gestisci la tastiera utilizzata nelle pubblicazioni delle offerte.\n\n"
        "Seleziona un’opzione per continuare 👇"
    )

    keyboard = [
        [
            InlineKeyboardButton("➕ Nuova tastiera", callback_data=f'channeloffers_addkeyboard_{channel_id}')
        ],
        [
            InlineKeyboardButton("📋 Seleziona tastiera", callback_data=f'channeloffers_showkeyboards_{channel_id}'),
            InlineKeyboardButton("✏️ Modifica tastiera", callback_data=f'channeloffers_editkeyboards_{channel_id}')
        ],
        [
            InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_layout_{channel_id}')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def keyboard_menu_add_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    context.user_data["channel_id"] = channel_id

    channel_id = check_channel_id(query, context)

    text = (
        "⌨️ <b>Nuova tastiera</b>\n\n"
        "✏️ Inserisci il nome da assegnare alla tastiera:"
    )

    keyboard = [
        [InlineKeyboardButton("❌ Annulla", callback_data=f'channeloffers_keyboards_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    context.user_data["msg_id"] = msg.message_id

    return ATTESA_NOME


async def keyboard_menu_add_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_id = context.user_data.get("channel_id")
    message_id = context.user_data.get("msg_id")
    nome_tastiera = update.message.text

    await update.message.delete()
    context.user_data["nome_tastiera"] = nome_tastiera

    text = (
        "⌨️ <b>Nuova tastiera</b>\n\n"
        "📝 Inserisci il contenuto della tastiera.\n\n"
        "📌 <b>Formato richiesto:</b>\n"
        "<code>messaggio1 - url1 || messaggio2 - url2</code>\n"
        "<code>messaggio3 - url3</code>\n\n"
        "🔗 Tag disponibile:\n<code>{url}</code> → link prodotto automatico"
    )

    keyboard = [
        [InlineKeyboardButton("❌ Annulla", callback_data=f'channeloffers_keyboards_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

    return ATTESA_MESSAGGIO

async def keyboard_menu_add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    channel_id = context.user_data.get("channel_id")
    message_id = context.user_data.get("msg_id")
    messaggio_tastiera = update.message.text
    await update.message.delete()

    nome_tastiera = context.user_data.pop("nome_tastiera")

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_keyboards_{channel_id}')]
    ]

    text = (
        "⌨️ <b>Nuova tastiera creata</b>\n\n"
        "La tastiera è stata salvata correttamente."
    )

    with SessionLocal() as session:
        tastiera_service = TastieraService(session)
        try:
            tastiera = Tastiera(nome_tastiera = nome_tastiera, messaggio = messaggio_tastiera, in_uso = 0, canale_id = channel_id)

            tastiera_service.crea_tastiera(tastiera)

            session.commit()
        except Exception:
            session.rollback()
            text = (
                "❌ <b>Errore tastiera</b>\n\n"
                "Non è stato possibile inserire la tastiera.\n"
                "Riprova più tardi."
            )

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def annulla_add_tastiera(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.pop("msg_id", None)
    context.user_data.pop("nome_tastiera", None)
    context.user_data.pop("channel_id", None)

    await keyboard_menu(update, context)
    return ConversationHandler.END

async def show_keyboards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    keyboard = []

    with SessionLocal() as session:
        tastiera_service = TastieraService(session)

        tastiere = tastiera_service.ottieni_tastiere_canale(channel_id)
        if tastiere:
            text = (
                "⌨️ <b>Le tue tastiere</b>\n\n"
                f"📊 Tastiere totali: <b>{len(tastiere)}</b>\n\n"
                "Scegli una tastiera per attivarla 👇"
            )
            for tastiera in tastiere:
                emoji_stato = "🟢" if tastiera.in_uso else "🔴"

                keyboard.append([InlineKeyboardButton(f"{tastiera.nome_tastiera}", callback_data=f'none'), InlineKeyboardButton(f"{emoji_stato}", callback_data=f'channeloffers_activatekeyboard_{channel_id}_{tastiera.tastiera_id}')])

        else:
            text = (
                "⌨️ <b>Nessuna tastiera presente</b>\n\n"
                "Non hai ancora creato alcuna tastiera.\n\n"
                "➕ Creane una per iniziare."
            )
            keyboard.append([InlineKeyboardButton("➕ Nuova tastiera", callback_data=f'channeloffers_addkeyboard_{channel_id}')])

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_keyboards_{channel_id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
    )

async def activate_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    parts = query.data.split("_")
    tastiera_id = int(parts[-1])
    context.user_data["channel_id"] = parts[-2]

    with SessionLocal() as session:
        tastiera_service = TastieraService(session)

        tastiera = tastiera_service.ottieni_tastiera(tastiera_id)

        if not tastiera:
            text = "⚠️ Errore durante l'attivazione della tastiera"
        else:
            try:   
                if(tastiera.in_uso):
                    tastiera.in_uso = False

                    session.commit()

                    text="🔴 Tastiera disattivata!"
                else:
                    tastiera_old = tastiera_service.ottieni_tastiera_in_uso(tastiera.canale_id)
                    if tastiera_old:
                        tastiera_old.in_uso = False
                    tastiera.in_uso = True

                    session.commit()

                    text="🟢 Tastiera selezionata!"
            except Exception:
                session.rollback()
                raise
    
    await query.answer(text=text, show_alert=True)

    await show_keyboards(update, context)

async def edit_keyboards(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    keyboard = []

    with SessionLocal() as session:
        tastiera_service = TastieraService(session)

        tastiere = tastiera_service.ottieni_tastiere_canale(channel_id)
        if tastiere:
            text = (
                "⌨️ <b>Modifica tastiera</b>\n\n"
                "Seleziona una tastiera da modificare 👇"
            )
            for tastiera in tastiere:
                keyboard.append([InlineKeyboardButton(f"{tastiera.nome_tastiera}", callback_data=f'channeloffers_editkeyboard_{channel_id}_{tastiera.tastiera_id}')])

        else:
            text = (
                "⌨️ <b>Nessuna tastiera presente</b>\n\n"
                "Non hai ancora creato alcuna tastiera.\n\n"
                "➕ Creane una per iniziare."
            )
            keyboard.append([InlineKeyboardButton("➕ Nuova tastiera", callback_data=f'channeloffers_addkeyboard_{channel_id}')])

    keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_keyboards_{channel_id}')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
    )

async def edit_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    tastiera_id = int(parts[-1])
    context.user_data["channel_id"] = parts[-2]

    with SessionLocal() as session:
        tastiera_service = TastieraService(session)

        tastiera = tastiera_service.ottieni_tastiera(tastiera_id)
    
    text = (
        f"⌨️ <b>Tastiera selezionata</b>\n\n"
        f"🏷️ <b>{tastiera.nome_tastiera}</b>\n\n"
        "📝 <b>Contenuto della tastiera</b>\n\n"
        f"<code>{tastiera.messaggio}</code>"
    )

    keyboard = [
        [InlineKeyboardButton("✏️ Modifica Contenuto", callback_data=f'channeloffers_editmessagekeyboard_{tastiera.canale_id}_{tastiera_id}'),InlineKeyboardButton("🗑️ Elimina Tastiera", callback_data=f'channeloffers_deletekeyboard_{tastiera.canale_id}_{tastiera.tastiera_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_editkeyboards_{tastiera.canale_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
    )

async def edit_keyboard_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    tastiera_id = parts[-1]
    channel_id= parts[-2]

    context.user_data["tastiera_id"]  = tastiera_id
    context.user_data["channel_id"] = channel_id

    text = (
        "⌨️ <b>Modifica tastiera</b>\n\n"
        "📝 Inserisci il nuovo contenuto della tastiera.\n\n"
        "📌 <b>Formato richiesto:</b>\n"
        "<code>messaggio1 - url1 || messaggio2 - url2</code>\n"
        "<code>messaggio3 - url3</code>\n\n"
        "🔗 <b>Tag disponibile:</b> <code>{url}</code> → link prodotto automatico"
    )

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_editkeyboard_{channel_id}_{tastiera_id}')]
    ]

    msg = await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    context.user_data["msg_id"] = msg.message_id

    return ATTESA_NUOVO_MESSAGGIO


async def ricevi_nuovo_messaggio_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tastiera_id  = int(context.user_data.get("tastiera_id"))
    channel_id = context.user_data.get("channel_id")
    message_id = context.user_data.get("msg_id")
    nuovo_messaggio = update.message.text

    await update.message.delete()

    with SessionLocal() as session:
        tastiera_service = TastieraService(session)
        tastiera = tastiera_service.ottieni_tastiera(tastiera_id)
        try:
            tastiera.messaggio = nuovo_messaggio

            session.commit()

            text = (
            "⌨️ <b>Tastiera aggiornata</b>\n\n"
            "Il contenuto è stato salvato con successo."
        )
        except Exception as e:
            session.rollback()

            text = (
                "❌ <b>Aggiornamento fallito</b>\n\n"
                "Non è stato possibile salvare le modifiche alla tastiera."
            )

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_editkeyboard_{channel_id}_{tastiera_id}')]
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
    context.user_data.pop("tastiera_id", None)
    context.user_data.pop("channel_id", None)

    await edit_keyboard(update, context)
    return ConversationHandler.END

async def delete_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    tastiera_id = parts[-1]
    channel_id = parts[-2]

    context.user_data["tastiera_id"] = tastiera_id
    context.user_data["channel_id"] = channel_id

    keyboard = [
        [
            InlineKeyboardButton("✅ Conferma", callback_data=f'channeloffers_confirmdeletekeyboard_{channel_id}_{tastiera_id}'),
            InlineKeyboardButton("❌ Annulla",  callback_data=f'channeloffers_editkeyboard_{channel_id}_{tastiera_id}')
        ]
    ]

    text = (
        "🗑️ <b>Elimina tastiera</b>\n\n"
        "Sei sicuro di voler eliminare questa tastiera?\n\n"
        "⚠️ <b>Attenzione:</b> questa operazione è irreversibile."
    )

    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def confirm_delete_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    tastiera_id = int(parts[-1])
    channel_id = parts[-2]

    with SessionLocal() as session:
        tastiera_service = TastieraService(session)

        tastiera = tastiera_service.ottieni_tastiera(tastiera_id)
        try:
            tastiera_service.rimuovi_tastiera(tastiera)

            session.commit()

            text = (
                "🗑️ <b>Tastiera eliminata</b>\n\n"
                "La tastiera è stata rimossa con successo."
            )
        except Exception as e:
            session.rollback()

            text = (
                "❌ <b>Eliminazione fallita</b>\n\n"
                "Non è stato possibile eliminare la tastiera.\n"
                "Riprova più tardi."
            )

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_editkeyboards_{channel_id}')]
    ]

    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


conv_keyboard = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(keyboard_menu_add_nome, pattern=r'^channeloffers_addkeyboard_-?\d+$'),
    ],
    states={
        ATTESA_NOME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, keyboard_menu_add_msg),
            CallbackQueryHandler(annulla_add_tastiera, pattern=r'^channeloffers_keyboards_-?\d+$'),
        ],
        ATTESA_MESSAGGIO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, keyboard_menu_add),
            CallbackQueryHandler(annulla_add_tastiera, pattern=r'^channeloffers_keyboards_-?\d+$'),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(annulla_add_tastiera, pattern=r'^channeloffers_keyboards_-?\d+$'),
    ],
    per_message=False,
    per_chat=True,
)

conv_edit_messaggio_keyboard = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(edit_keyboard_message, pattern=r'^channeloffers_editmessagekeyboard_(-?\d+)_(\d+)$'),
    ],
    states={
        ATTESA_NUOVO_MESSAGGIO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_nuovo_messaggio_keyboard),
            CallbackQueryHandler(annulla_edit_messaggio, pattern=r'^channeloffers_editkeyboard_-?\d+_\d+$'),
            
        ],
    },
    fallbacks=[
        CallbackQueryHandler(annulla_edit_messaggio, pattern=r'^channeloffers_editkeyboard_-?\d+_\d+$'),
    ],
    per_message=False,
    per_chat=True,
)