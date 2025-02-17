from telegram import *
from telegram.ext import *

from database.DAO.GestisceDAO import GestisceDAO

from database.Entity.Gestisce import Gestisce

async def admin_panel(query: CallbackQuery, channel_id: str, user_id: str) -> None:

    with GestisceDAO() as gestisce_dao:
        gestisce_info = gestisce_dao.get(user_id, channel_id)

        if(gestisce_info.isCreator):
            await query.answer()
        else:
            await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
            return
        
    text = "Benvenuto nel pannello Admin!\n\nAttraverso di esso potrai invitare altri utenti alla gestione del tuo canale oppure inserire il tuo id affiliato che verrà usato durante la pubblicazione dei prodotti"

    keyboard = [
        [InlineKeyboardButton("Invita membri (WIP)", callback_data=f'none')],
        [InlineKeyboardButton("Tag affiliato", callback_data=f'channel_adminaffiliateid_{channel_id}')],
        [InlineKeyboardButton("Cancella canale (WIP)", callback_data='none')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )

    
