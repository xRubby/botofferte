from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database.session import SessionLocal
from services.canale_service import CanaleService
from utils.channel_offers_utils import check_channel_id, delete_preview_message

async def channel_info(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    
    channel_id = check_channel_id(query, context)

    #Se esco dal pannello admin imposto la variabile a False così da aggiornare il valore
    context.user_data['isCreator'] = False

    #Cancella messaggio preview di Lista Link
    await delete_preview_message(
        chat_id=query.message.chat_id,
        context=context
    )

    with SessionLocal() as session:
        canale_service = CanaleService(session)
        canale = canale_service.ottieni_canale(channel_id)

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