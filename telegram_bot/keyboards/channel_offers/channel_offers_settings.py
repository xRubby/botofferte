from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from database.session import SessionLocal
from services.gestisce_service import GestisceService
from utils.channel_offers_utils import check_channel_id

async def channel_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    text = (
        "⚙️ <b>Impostazioni canale</b>\n\n"
        "Gestisci le opzioni del tuo canale da questa sezione."
    )

    keyboard = [
        [InlineKeyboardButton("🚪 Esci dal canale", callback_data=f'channeloffers_exitchannel_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_info_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def exit_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)

    text = (
        "⚠️ <b>Conferma uscita canale</b>\n\n"
        "Sei sicuro di voler uscire da questo canale?\n"
        "Dopo l’uscita non avrai più accesso ai contenuti."
    )

    keyboard = [
        [InlineKeyboardButton("✅ Conferma", callback_data=f'channeloffers_exitchannelconfirm_{channel_id}'), InlineKeyboardButton("❌ Annulla", callback_data=f'channeloffers_settings_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def exit_channel_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    channel_id = check_channel_id(query, context)
    user_id = update.effective_user.id

    keyboard = [
        [InlineKeyboardButton("🏠 Home", callback_data=f'back_to_main')]
    ]

    with SessionLocal() as session:
        gestisce_service = GestisceService(session)

        gestisce = gestisce_service.ottieni_gestione(user_id, channel_id)
        if gestisce and not gestisce.is_creator:
            gestisce_service.rimuovi_gestione(gestisce)
            text = (
                "🚪 <b>Rimozione completata</b>\n\n"
                "Sei stato rimosso dal canale."
            )
        elif gestisce.is_creator:
            text = (
                "⚠️ <b>Operazione non consentita</b>\n\n"
                "Non puoi essere rimosso dal canale perché sei il creatore."
            )
            keyboard = [
                [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_settings_{channel_id}')]
            ]
        else:
            text = (
                "❌ <b>Errore nella rimozione</b>\n\n"
                "Non è stato possibile completare l’operazione.\n"
                "Riprova più tardi."
            )

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
