from telegram import *
from telegram.ext import *

from database.DAO.GestisceDAO import GestisceDAO
from database.DAO.CanaleDAO import CanaleDAO
from database.DAO.LicenzaDAO import LicenzaDAO
from utils.channel_offers_utils import check_channel_id

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    channel_id = query.data.split("_")[-1]
    user_id = update.effective_user.id

    with GestisceDAO() as gestisce_dao:
        gestisce_info = gestisce_dao.get(user_id, channel_id)

        if(gestisce_info and gestisce_info.isCreator):
            await query.answer()
        else:
            await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
            return
        
    text = "Benvenuto nel pannello Admin!\n\nAttraverso di esso potrai invitare altri utenti alla gestione del tuo canale oppure inserire il tuo id affiliato che verrà usato durante la pubblicazione dei prodotti"

    keyboard = [
        [InlineKeyboardButton("Invita membri (WIP)", callback_data='none')],
        [InlineKeyboardButton("Tag affiliato", callback_data=f'channeloffers_adminaffiliateid_{channel_id}'), InlineKeyboardButton("Informazioni Licenza", callback_data=f'channeloffers_adminlicenseinfo_{channel_id}')],
        [InlineKeyboardButton("Cancella canale", callback_data=f'none')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_info_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )