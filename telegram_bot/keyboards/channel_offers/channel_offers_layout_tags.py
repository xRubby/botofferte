from telegram import *
from telegram.ext import *
import re

from database.Entity.Canale import Canale
from database.DAO.CanaleDAO import CanaleDAO
from utils.channel_offers_utils import check_channel_id

ATTESA_NUOVO_TAG = "ATTESA_NUOVO_TAG"
ATTESA_NUOVO_TAG_SPEDITO = "ATTESA_NUOVO_TAG_SPEDITO"

DEFAULT_TAGS = {
    "amazon": "Venduto e spedito da Amazon",
    "vndamazon": "Venduto da {venditore} e spedito da Amazon",
    "vnd": "Venduto e spedito da {venditore}",
    "preorder": "Preordine:",
    "prime": "Spedizione gratuita con Amazon Prime",
    "offertaexcl": "Offerta Speciale:"
}

async def edit_tags(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    keyboard = [
        [
            InlineKeyboardButton("{spedito}", callback_data=f'co_edittags_{channel_id}_sp'),
            InlineKeyboardButton("{prime}", callback_data=f'co_edittags_{channel_id}_prime'),
        ],
        [
            InlineKeyboardButton("{preorder}", callback_data=f'co_edittags_{channel_id}_preorder'),
            InlineKeyboardButton("{offertaexcl}", callback_data=f'co_edittags_{channel_id}_offertaexcl')
        ],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_layout_{channel_id}')]
    ]

    text = (
        "🏷️ <b>Modifica tag</b>\n\n"
        "Qui puoi aggiornare le informazioni dei tag."
    )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def edit_tags_spedito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    match = re.match(r'^co_edittags_(-\d+)_sp$', query.data)
    channel_id = match.group(1)

    keyboard = [
        [InlineKeyboardButton("🏪 Amazon", callback_data=f'co_edittags_{channel_id}_sp_amazon')],
        [InlineKeyboardButton("🏪 Venditore + 📦 Amazon", callback_data=f'co_edittags_{channel_id}_sp_vndamazon')],
        [InlineKeyboardButton("🏪 Venditore", callback_data=f'co_edittags_{channel_id}_sp_vnd')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'co_edittags_{channel_id}')]
    ]

    text = (
        "🚚 <b>Tipo di spedizione</b>\n\n"
        "Seleziona il tipo di vendita e spedizione da associare al tag 👇"
    )

    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def edit_tags_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    match = re.match(r'^co_edittags_(-\d+)_(prime|preorder|offertaexcl)$', query.data)
    channel_id = match.group(1)
    tag_type = match.group(2)

    context.user_data["tag_type"] = tag_type
    context.user_data["channel_id"] = channel_id

    with CanaleDAO() as canaleDAO:
        channel = canaleDAO.get(channel_id)

    if tag_type == "prime":
        current = channel.prime_tag
        label = "Prime"
    elif tag_type == "preorder":
        current = channel.preorder_tag
        label = "Preorder"
    elif tag_type == "offertaexcl":
        current = channel.offertaexcl_tag
        label = "Offerta Esclusiva"

    text = (
        f"🏷️ <b>Tag selezionato:</b> {label}\n\n"
        "📝 <b>Messaggio corrente</b>\n\n"
        f"<code>{current}</code>\n\n"
        "✏️ Invia il nuovo testo per aggiornare il tag:"
    )

    keyboard = [
        [InlineKeyboardButton("🔄 Ripristina default", callback_data=f'co_edittags_{channel_id}_reset_{tag_type}')],
        [InlineKeyboardButton("❌ Annulla", callback_data=f'co_edittags_{channel_id}')]
    ]
    msg = await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    context.user_data["msg_id"] = msg.id

    return ATTESA_NUOVO_TAG


async def ricevi_nuovo_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nuovo_testo = update.message.text
    channel_id = context.user_data.get("channel_id")
    tag_type = context.user_data.get("tag_type")
    message_id = context.user_data.pop("msg_id", None)

    await update.message.delete()

    with CanaleDAO() as canaleDAO:
        channel = canaleDAO.get(channel_id)
        if tag_type == "prime":
            channel.prime_tag = nuovo_testo
        elif tag_type == "preorder":
            channel.preorder_tag = nuovo_testo
        elif tag_type == "offertaexcl":
            channel.offertaexcl_tag = nuovo_testo

        canaleDAO.update_tags(
            channel.canale_id,
            channel.amazon_tag,
            channel.venditoreamazon_tag,
            channel.venditore_tag,
            channel.preorder_tag,
            channel.prime_tag,
            channel.offertaexcl_tag
        )

    keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data=f'co_edittags_{channel_id}')]]

    text = (
        "✅ <b>Tag aggiornato</b>\n\n"
        f"🏷️ Il tag <b>{{{tag_type}"
        "}</b> è stato aggiornato con successo."
    )

    if not message_id:
        await update.message.reply_text(
            text,
            parse_mode="HTML"
        )
    else:
        await context.bot.edit_message_text(
            text,
            chat_id=update.effective_chat.id,
            message_id=message_id,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    return ConversationHandler.END


async def annulla_edit_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await edit_tags(update, context)
    return ConversationHandler.END


async def reset_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    match = re.match(r'^co_edittags_(-\d+)_reset_(prime|preorder)$', query.data)
    channel_id = match.group(1)
    tag_type = match.group(2)

    with CanaleDAO() as canaleDAO:
        channel = canaleDAO.get(channel_id)
        if tag_type == "prime":
            channel.prime_tag = DEFAULT_TAGS["prime"]
        elif tag_type == "preorder":
            channel.preorder_tag = DEFAULT_TAGS["preorder"]
        elif tag_type == "offertaexcl":
            channel.offertaexcl_tag = DEFAULT_TAGS["offertaexcl"]

        canaleDAO.update_tags(
            channel.canale_id,
            channel.amazon_tag,
            channel.venditoreamazon_tag,
            channel.venditore_tag,
            channel.preorder_tag,
            channel.prime_tag,
            channel.offertaexcl_tag
        )

    await query.edit_message_text(
        "🔄 <b>Tag ripristinato</b>\n\n"
        f"🏷️ <b>{tag_type.capitalize()}</b> è stato riportato al valore predefinito.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'co_edittags_{channel_id}')]
        ])
    )

    return ConversationHandler.END


async def edit_tags_spedito_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    match = re.match(r'^co_edittags_(-\d+)_sp_(amazon|vndamazon|vnd)$', query.data)
    channel_id = match.group(1)
    spedito_type = match.group(2)

    context.user_data["spedito_type"] = spedito_type
    context.user_data["channel_id"] = channel_id

    with CanaleDAO() as canaleDAO:
        channel = canaleDAO.get(channel_id)

    labels = {
        "amazon": ("Amazon", channel.amazon_tag),
        "vndamazon": ("Venditore+Amazon", channel.venditoreamazon_tag),
        "vnd": ("Venditore", channel.venditore_tag),
    }
    label, current = labels[spedito_type]

    text = (
        f"🏷️ <b>Tag selezionato:</b> {label}\n\n"
        "📝 <b>Messaggio corrente</b>\n\n"
        f"<code>{current}</code>\n\n"
        "✏️ Invia il nuovo testo per aggiornare il tag:"
    )

    keyboard = [
        [InlineKeyboardButton("🔄 Ripristina default", callback_data=f'co_edittags_{channel_id}_reset_sp_{spedito_type}')],
        [InlineKeyboardButton("❌ Annulla", callback_data=f'co_edittags_{channel_id}_sp')]
    ]
    msg = await query.edit_message_text(text=text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))
    context.user_data["msg_id"] = msg.id

    return ATTESA_NUOVO_TAG_SPEDITO


async def ricevi_nuovo_tag_spedito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nuovo_testo = update.message.text
    channel_id = context.user_data.get("channel_id")
    spedito_type = context.user_data.get("spedito_type")
    message_id = context.user_data.pop("msg_id", None)

    await update.message.delete()

    with CanaleDAO() as canaleDAO:
        channel = canaleDAO.get(channel_id)
        if spedito_type == "amazon":
            channel.amazon_tag = nuovo_testo
        elif spedito_type == "vndamazon":
            channel.venditoreamazon_tag = nuovo_testo
        elif spedito_type == "vnd":
            channel.venditore_tag = nuovo_testo

        canaleDAO.update_tags(
            channel.canale_id,
            channel.amazon_tag,
            channel.venditoreamazon_tag,
            channel.venditore_tag,
            channel.preorder_tag,
            channel.prime_tag,
            channel.offertaexcl_tag
        )

    keyboard = [[InlineKeyboardButton("⬅️ Indietro", callback_data=f'co_edittags_{channel_id}_sp')]]

    text = (
        "✅ <b>Tag aggiornato</b>\n\n"
        f"🏷️ Il tag è stato aggiornato con successo."
    )

    if not message_id:
        await update.message.reply_text(
            text,
            parse_mode="HTML"
        )
    else:
        await context.bot.edit_message_text(
            text,
            chat_id=update.effective_chat.id,
            message_id=message_id,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    return ConversationHandler.END


async def annulla_edit_tag_spedito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await edit_tags_spedito(update, context)
    return ConversationHandler.END


async def reset_tag_spedito(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    match = re.match(r'^co_edittags_(-\d+)_reset_sp_(amazon|vndamazon|vnd)$', query.data)
    channel_id = match.group(1)
    spedito_type = match.group(2)

    with CanaleDAO() as canaleDAO:
        channel = canaleDAO.get(channel_id)
        if spedito_type == "amazon":
            channel.amazon_tag = DEFAULT_TAGS["amazon"]
        elif spedito_type == "vndamazon":
            channel.venditoreamazon_tag = DEFAULT_TAGS["vndamazon"]
        elif spedito_type == "vnd":
            channel.venditore_tag = DEFAULT_TAGS["vnd"]

        canaleDAO.update_tags(
            channel.canale_id,
            channel.amazon_tag,
            channel.venditoreamazon_tag,
            channel.venditore_tag,
            channel.preorder_tag,
            channel.prime_tag,
            channel.offertaexcl_tag
        )

    await query.edit_message_text(
        "🔄 <b>Tag ripristinato</b>\n\n"
        f"🏷️ <b>Il tag è stato riportato al valore predefinito.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'co_edittags_{channel_id}_sp')]
        ])
    )

    return ConversationHandler.END


conv_edit_tag = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(edit_tags_type, pattern=r'^co_edittags_(-\d+)_(prime|preorder|offertaexcl)$'),
    ],
    states={
        ATTESA_NUOVO_TAG: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_nuovo_tag),
            CallbackQueryHandler(reset_tag, pattern=r'^co_edittags_-?\d+_reset_(prime|preorder|offertaexcl)$'),
            CallbackQueryHandler(annulla_edit_tag, pattern=r'^co_edittags_-?\d+$'),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(annulla_edit_tag, pattern=r'^co_edittags_-?\d+$'),
    ],
    per_message=False,
    per_chat=True,
)

conv_edit_tag_spedito = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(edit_tags_spedito_type, pattern=r'^co_edittags_(-\d+)_sp_(amazon|vndamazon|vnd)$'),
    ],
    states={
        ATTESA_NUOVO_TAG_SPEDITO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, ricevi_nuovo_tag_spedito),
            CallbackQueryHandler(reset_tag_spedito, pattern=r'^co_edittags_-?\d+_reset_sp_(amazon|vndamazon|vnd)$'),
            CallbackQueryHandler(annulla_edit_tag_spedito, pattern=r'^co_edittags_-?\d+_sp$'),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(annulla_edit_tag_spedito, pattern=r'^co_edittags_-?\d+_sp$'),
    ],
    per_message=False,
    per_chat=True,
)