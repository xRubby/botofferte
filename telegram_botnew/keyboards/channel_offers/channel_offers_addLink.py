from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters

from telegram_botnew.functions.send_message import search_offer
from telegram_botnew.keyboards.channel_offers.channels_offers_info import channel_info
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
        text="Inserisci il link di Amazon:",
        reply_markup=reply_markup
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
    
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text="Elaboro il prodotto...",
        parse_mode="HTML",
    )

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f"channeloffers_info_{channel_id}")]
    ])

    try:
        await search_offer(update, context, keyword)
        testo = "Link aggiunto con successo."
    except ValueError as ve:
        testo = f"<b>Errore durante l'elaborazione del prodotto</b>\n\nErrore: {ve}"
    except Exception as e:
        testo = "<b>Errore durante l'elaborazione del prodotto</b>\n\nErrore generico"
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