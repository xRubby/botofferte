from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database.DAO.CanaleDAO import CanaleDAO
from utils.channel_offers_utils import check_channel_id

async def channel_info(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    
    channel_id = check_channel_id(query, context)

    with CanaleDAO() as canaleDAO:
        canale = canaleDAO.get(channel_id)

    if not canale:
        await query.answer(text="Canale non trovato", show_alert=True)
        return
        
    await query.answer()

    context.user_data.pop("links", None)

    keyboard = [
        [InlineKeyboardButton("➕ Inserisci Link", callback_data=f'channeloffers_addlink_{channel_id}')],
        [InlineKeyboardButton("🔗 Lista Link", callback_data=f'channeloffers_link_0_{channel_id}'), InlineKeyboardButton("🌟 Affiliazione", callback_data=f'channeloffers_affiliateid_{channel_id}')],
        [InlineKeyboardButton("📈 Statistiche (WIP)", callback_data=f'none'), InlineKeyboardButton("⚙️ Impostazioni", callback_data=f'channeloffers_settings_{channel_id}')],
        [InlineKeyboardButton("🎨 Layout", callback_data=f'channeloffers_layout_{channel_id}'), InlineKeyboardButton("👨‍💼 Pannello Admin", callback_data=f'channeloffers_adminpanel_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data='channeloffers_main')]
    ]

    text = (
        "⚙️ <b>Gestione canale</b>\n\n"
        f"📢 <b>{canale.nome_canale}</b>\n\n"
        "Scegli una sezione per gestire il tuo canale 👇"
    )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    await query.answer()