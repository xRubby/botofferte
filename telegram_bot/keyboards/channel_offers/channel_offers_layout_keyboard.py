from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from database.DAO.TastieraDAO import TastieraDAO
from utils.channel_offers_utils import check_channel_id

ATTESA_NOME, ATTESA_MESSAGGIO = range(2)

async def keyboard_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    text = "Tastiera post\n\nFunzionalità che riguardano la tastiera che verrà utilizzata nella pubblicazione delle offerte" 

    keyboard = [
        [InlineKeyboardButton("Aggiungi Tastiera", callback_data=f'channeloffers_addkeyboard_{channel_id}')],
        [InlineKeyboardButton("Seleziona Tastiera", callback_data=f'channeloffers_showkeyboards_{channel_id}'), InlineKeyboardButton("Modifica Tastiera", callback_data=f'channeloffers_editkeyboards_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_layout_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )

async def keyboard_menu_add_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    context.user_data["channel_id"] = channel_id

    channel_id = check_channel_id(query, context)

    text = "Tastiera post\n\nInserisci nome" 

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_keyboards_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = await query.edit_message_text(
        text=text,
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

    text = "Tastiera post\n\nInserisci messaggio" 

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_keyboards_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=text,
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

    text = "Tastiera post\n\nInserimento avvenuto correttamente" 

    try:
        with TastieraDAO() as tastieraDAO:
            tastieraDAO.insert(nome_tastiera, messaggio_tastiera, 0, channel_id)
    except Exception:
        text = "Errore nell'inserimento della tastiera"

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=text,
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

    with TastieraDAO() as tastieraDAO:
        tastiere = tastieraDAO.get_channel_keyboards(channel_id)
        if tastiere:
            text=f"Le tue tastiere\n\nTastiere totali: {len(tastiere)}"
            for tastiera in tastiere:
                emoji_stato = "🟢" if tastiera.in_uso else "🔴"

                keyboard.append([InlineKeyboardButton(f"{tastiera.nome_tastiera}", callback_data=f'none'), InlineKeyboardButton(f"{emoji_stato}", callback_data=f'channeloffers_activatekeyboard_{channel_id}_{tastiera.tastiera_id}')])

        else:
            text = "Nessun layout presente"

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
    keyboard_id = parts[-1]
    context.user_data["channel_id"] = parts[-2]

    with TastieraDAO() as tastieraDAO:
        tastiera = tastieraDAO.get(keyboard_id)

        if not  tastiera:
            text = "Errore durante l'attivazione della tastiera"
        else:   
            id_canale = tastiera.canale_id

            if( tastiera.in_uso):
                tastieraDAO.update_stato(tastiera.tastiera_id, 0)
                text="Tastiera disattivata!"
            else:
                tastiera_old = tastieraDAO.get_in_uso(id_canale)
                if tastiera_old:
                    tastieraDAO.update_stato(tastiera_old.tastiera_id, 0)
                tastieraDAO.update_stato( tastiera.tastiera_id, 1)
                text="Tastiera selezionata!"
    
    await query.answer(text=text, show_alert=True)

    await show_keyboards(update, context)

conv_keyboard = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(keyboard_menu_add_nome, pattern=r'^channeloffers_addkeyboard_-?\d+$'),
    ],
    states={
        ATTESA_NOME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, keyboard_menu_add_msg),
            CallbackQueryHandler(annulla_add_tastiera, pattern=r'^channeloffers_addkeyboard_-?\d+$'),
        ],
        ATTESA_MESSAGGIO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, keyboard_menu_add),
            CallbackQueryHandler(annulla_add_tastiera, pattern=r'^channeloffers_addkeyboard_-?\d+$'),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(annulla_add_tastiera, pattern=r'^channeloffers_addkeyboard_-?\d+$'),
    ],
    per_message=False,
    per_chat=True,
)