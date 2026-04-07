import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram_botnew.functions.send_message import search_and_send_offer
from telegram_botnew.keyboards.main_menu import handler_menu_principale

KEYWORD = range(1)

CERCA_PRODOTTO_MSG=(
    "<b>🔍 Cerca prodotto</b>"
    "\n\n"
    "Per favore, inviami il nome oppure il link del prodotto che vuoi cercare."
)

async def handler_avvia_ricerca(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Indietro", callback_data="back_to_main")]
    ])
    msg = await query.edit_message_text(
        text=CERCA_PRODOTTO_MSG,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )

    ctx.user_data["msg_id"] = msg.message_id

    return KEYWORD



async def handler_keyword(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:

    keyword = update.message.text
    message_id=ctx.user_data.get("msg_id", None)

    if(message_id is None):
        return ConversationHandler.END
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Indietro", callback_data="back_to_main")]
    ])

    await update.message.delete()
    await ctx.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text="<b>🔍 Cerca prodotto</b>\n\nSto elaborando il tuo link...",
        parse_mode="HTML"
    )

    await asyncio.sleep(2)
    
    try:
        await search_and_send_offer(update, ctx, keyword)
    except ValueError as ve:
        await ctx.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text=f"<b>Errore durante l'elaborazione del prodotto</b>\n\nErrore: {ve}",
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
    except Exception:
        await ctx.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text=f"<b>Errore durante l'elaborazione del prodotto</b>\n\nErrore generico",
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
    
 
    return ConversationHandler.END


async def handler_annulla_ricerca(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> int:

    query = update.callback_query
    await query.answer()

    await handler_menu_principale(update, ctx)
    return ConversationHandler.END


conv_cerca_prodotto = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(handler_avvia_ricerca, pattern=r"^cerca_prodotto$")
    ],
    states={
        KEYWORD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handler_keyword),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(handler_annulla_ricerca, pattern=r"^back_to_main$"),
    ],
    per_message=False,
    per_chat=True,
)
