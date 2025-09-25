from telegram import *
from telegram.ext import *

from database.DAO.GestisceDAO import GestisceDAO
from database.DAO.CanaleDAO import CanaleDAO
from database.DAO.LicenzaDAO import LicenzaDAO

async def admin_panel(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, channel_id: str, user_id: str) -> None:

    if context.user_data[user_id].get('awaiting_admin_affiliateid'):
        context.user_data[user_id]['awaiting_admin_affiliateid'] = False

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
        [InlineKeyboardButton("Tag affiliato", callback_data=f'channel_adminaffiliateid_{channel_id}'), InlineKeyboardButton("Informazioni Licenza", callback_data=f'channel_adminlicenseinfo_{channel_id}')],
        [InlineKeyboardButton("Cancella canale", callback_data=f'channel_admindelete_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'edit_channel_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )

async def admin_edit_affiliateid(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, channel_id: str, user_id: int):

    with GestisceDAO() as gestisce_dao, CanaleDAO() as canale_dao:
        gestisce_info = gestisce_dao.get(user_id, channel_id)
        canale = canale_dao.get(channel_id)

    if(gestisce_info.isCreator):
        await query.answer()
    else:
        await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
        return
        
    id_affiliato = canale.id_affiliato if canale.id_affiliato else "Nessuno"
        
    text= f"Inserisci l'ID Affiliato che verrà usato di default durante la pubblicazione dei prodotti.\n\n ID Attuale: {id_affiliato}"

    message_id = query.message.id
    context.user_data[user_id] = {'awaiting_admin_affiliateid': True, 'message_id': message_id, 'channel_id': channel_id}

    keyboard = [
        [InlineKeyboardButton("Rimuovi ID Affiliato", callback_data=f'channel_adminremoveaffiliateid_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_adminpanel_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )
    

async def admin_remove_affiliateid(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, channel_id: str, user_id: int):
    
    if context.user_data[user_id].get('awaiting_admin_affiliateid'):
        context.user_data[user_id]['awaiting_admin_affiliateid'] = False

    with GestisceDAO() as gestisce_dao, CanaleDAO() as canale_dao:
        gestisce_info = gestisce_dao.get(user_id, channel_id)
        
        if(gestisce_info.isCreator):
            await query.answer()
        else:
            await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
            return
        
        canale_dao.update_id_affiliato(channel_id, "")
    
    text = "ID Affiliato rimosso con successo!"

    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_adminpanel_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )
    
async def admin_delete_channel(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, channel_id: str, user_id: int):
    
    with GestisceDAO() as gestisce_dao:
        gestisce_info = gestisce_dao.get(user_id, channel_id)

        if(gestisce_info.isCreator):
            await query.answer()
        else:
            await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
            return

    with CanaleDAO() as canale_dao:
        canale = canale_dao.get(channel_id)

    
    
    keyboard = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'offerte_canale')]
    ]

    try:
        with CanaleDAO() as canale_dao:
            canale_dao.delete(channel_id)
        text = f"Canale <b>{canale.nome_canale}</b> eliminato con successo!"
    except Exception as e:
        text = f"Errore durante l'eliminazione del canale"

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def admin_license_info(query: CallbackQuery, context: ContextTypes.DEFAULT_TYPE, channel_id: str, user_id: int):
    try:
        with GestisceDAO() as gestisce_dao:
            gestisce_info = gestisce_dao.get(user_id, channel_id)

            if(gestisce_info.isCreator):
                await query.answer()
            else:
                await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
                return

        with CanaleDAO() as canale_dao:
            canale = canale_dao.get(channel_id)

        with LicenzaDAO() as licenza_dao:
            licenza = licenza_dao.get(canale.codice_licenza)
            stato = licenza_dao.get_stato(canale.codice_licenza)

        

        if licenza:
            text = f"Licenza: <code>{licenza.codice_licenza}</code>\nTipo: {licenza.tipo.title()}\n"

            if(stato):
                text += f"Stato: 'Attiva'\n\nData attivazione: {licenza.data_attivazione}\nData scadenza: {licenza.data_scadenza}"
            else:
                text += "Stato: 'Non attiva'"
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channel_adminpanel_{channel_id}')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    except Exception as e:
        await query.answer(text="Errore durante il recupero delle informazioni", show_alert=True)
        return