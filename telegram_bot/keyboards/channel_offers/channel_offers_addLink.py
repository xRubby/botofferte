from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from telegram_bot.functions.send_message import search_offer
from telegram_bot.keyboards.channel_offers.channels_offers_info import channel_info
from utils.channel_offers_utils import check_channel_id

ATTESA_KEYWORD = range(1)


async def insert_link_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    if not channel_id:
        return

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_info_{channel_id}')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = await query.edit_message_text(
        text = (
            "🔗 <b>Inserisci link Amazon</b>\n\n"
            "Incolla il link del prodotto che vuoi aggiungere 👇"
        ),
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    context.user_data["msg_id"] = msg.message_id
    return ATTESA_KEYWORD


async def ricevi_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyword = update.message.text
    channel_id = context.user_data.get('channel_id')
    message_id = context.user_data.get("msg_id")

    await update.message.delete()

    if not channel_id or not message_id:
        return
    
    msg = await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=("🔍 <b>Ricerca in corso...</b>\n\n"
        "Sto analizzando il prodotto Amazon."),
        parse_mode="HTML",
    )

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f"channeloffers_info_{channel_id}")]
    ])

    try:
        await search_offer(update, context, keyword, update.effective_chat.id, msg.message_id)
        testo = (
            "✅ <b>Operazione completata</b>\n\n"
            "🔗 Il link è stato aggiunto correttamente nella lista."
        )
    except ValueError as ve:
        testo = (
            "❌ <b>Errore nell'elaborazione del prodotto</b>\n\n"
            "⚠️ Il link o i dati forniti non sono validi.\n"
            "Controlla il contenuto e riprova."
        )
    except Exception as e:
        testo = (
            "❌ <b>Errore imprevisto</b>\n\n"
            "Si è verificato un problema durante l'elaborazione del prodotto.\n"
            "Riprova più tardi."
        )
        import traceback
        traceback.print_exc()

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=testo,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
    return ConversationHandler.END


async def annulla_insert_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await channel_info(update, context)
    return ConversationHandler.END


# --- ConversationHandler ---
conv_insert_link = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(insert_link_entry, pattern=r'^channeloffers_addlink_-?\d+$')
    ],
    states={
        ATTESA_KEYWORD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_keyword),
            CallbackQueryHandler(annulla_insert_link, pattern=r'^channeloffers_info_-?\d+$'),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(annulla_insert_link, pattern=r'^channeloffers_info_-?\d+$')
    ],
    per_message=False,
    per_chat=True,
)