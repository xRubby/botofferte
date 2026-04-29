from telegram import *
from telegram.ext import *

from database.DAO.GestisceDAO import GestisceDAO
from database.DAO.CanaleDAO import CanaleDAO
from database.DAO.LicenzaDAO import LicenzaDAO
from utils.channel_offers_utils import check_channel_id

ATTESA_ID_AFFILIATO = "ATTESA_ID_AFFILIATO"

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    channel_id = check_channel_id(query, context)
    user_id = update.effective_user.id

    with GestisceDAO() as gestisce_dao:
        gestisce_info = gestisce_dao.get(user_id, channel_id)

        if(gestisce_info and gestisce_info.isCreator):
            await query.answer()
            context.user_data['isCreator'] = gestisce_info.isCreator
        else:
            await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
            return
        
    text = "Benvenuto nel pannello Admin!\n\nAttraverso di esso potrai invitare altri utenti alla gestione del tuo canale oppure inserire il tuo id affiliato che verrà usato durante la pubblicazione dei prodotti"

    keyboard = [
        [InlineKeyboardButton("Invita membri (WIP)", callback_data='none')],
        [InlineKeyboardButton("Tag affiliato", callback_data=f'channeloffers_adminaffiliateid_{channel_id}'), InlineKeyboardButton("Informazioni Licenza", callback_data=f'channeloffers_adminlicenseinfo_{channel_id}')],
        [InlineKeyboardButton("Cancella canale", callback_data=f'channeloffers_admindeletechannel_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_info_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )

async def admin_edit_affiliateid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    channel_id = check_channel_id(query, context)

    isCreator = context.user_data.get("isCreator", None)

    if(isCreator):
        await query.answer()
    else:
        await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
        return
    
    with CanaleDAO() as canaleDAO:
        canale = canaleDAO.get(channel_id)
        
    id_affiliato = canale.id_affiliato if canale.id_affiliato else "Nessuno"
        
    text= f"Inserisci l'ID Affiliato che verrà usato di default durante la pubblicazione dei prodotti.\n\nID Attuale: {id_affiliato}"

    keyboard = [
        [InlineKeyboardButton("Rimuovi ID Affiliato", callback_data=f'channeloffers_adminremoveaffiliateid_{channel_id}')],
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_adminpanel_{channel_id}')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = await query.edit_message_text(
        text=text,
        reply_markup=reply_markup
    )

    context.user_data["msg_id"] = msg.id

    return ATTESA_ID_AFFILIATO

async def admin_ricevi_affiliate_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    message_id = context.user_data.pop("msg_id", None)
    channel_id = context.user_data.get('channel_id')
    affiliate_id = update.message.text

    await update.message.delete()
    try:
        with CanaleDAO() as canaleDAO:
            canaleDAO.update_id_affiliato(channel_id, affiliate_id)

        text = f"ID Affiliato aggiornato in: <b>{affiliate_id}</b>"
    except Exception as e:
        text = f"Errore durante l'aggiornamento dell'ID Affiliato..."

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_adminaffiliateid_{channel_id}')]
    ])

    if not message_id:
        await update.message.reply_text(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else: 
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            text=text,
            message_id=message_id,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    return ConversationHandler.END

async def admin_annulla_inserimento_affiliateid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.pop("msg_id", None)

    await admin_panel(update, context)
    return ConversationHandler.END

async def admin_remove_affiliate_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    isCreator = context.user_data.get("isCreator", None)

    if(isCreator):
        await query.answer()
    else:
        await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
        return
    
    channel_id = check_channel_id(query, context)

    try:
        with CanaleDAO() as canaleDAO:
            canaleDAO.update_id_affiliato(channel_id, "")

        text = f"ID Affiliato rimosso"
    except Exception as e:
        text = f"Errore durante la rimozione dell'ID Affiliato..."

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_adminaffiliateid_{channel_id}')]
    ])
    
    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard
    )

    return ConversationHandler.END

conv_edit_admin_affiliateid = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(admin_edit_affiliateid, pattern=r'^channeloffers_adminaffiliateid_(-\d+)$'),
    ],
    states={
        ATTESA_ID_AFFILIATO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, admin_ricevi_affiliate_id),
            CallbackQueryHandler(admin_remove_affiliate_id, pattern=r'^channeloffers_adminremoveaffiliateid_-?\d+'),
            CallbackQueryHandler(admin_annulla_inserimento_affiliateid, pattern="^channeloffers_adminpanel_.+$"),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(admin_annulla_inserimento_affiliateid, pattern="^channeloffers_adminpanel_.+$"),
    ],
    per_message=False,
    per_chat=True,
)

async def admin_license_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    channel_id = check_channel_id(query, context)

    isCreator = context.user_data.get("isCreator", None)

    if not isCreator:
        await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
        return

    try:
        with CanaleDAO() as canaleDAO:
            canale = canaleDAO.get(channel_id)

        if not canale:
            raise ValueError()

        with LicenzaDAO() as licenzaDAO:
            licenza = licenzaDAO.get(canale.codice_licenza)
            stato = licenzaDAO.get_stato(canale.codice_licenza)

        if not licenza:
            raise ValueError()

        text = f"Licenza: <code>{licenza.codice_licenza}</code>\nTipo: {licenza.tipo.title()}\n"

        if(stato):
            text += f"Stato: 'Attiva'\n\nData attivazione: {licenza.data_attivazione}\nData scadenza: {licenza.data_scadenza}"
        else:
            text += "Stato: 'Non attiva'"
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_adminpanel_{channel_id}')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.answer()

        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    except Exception as e:
        await query.answer(text="Errore durante il recupero delle informazioni", show_alert=True)
        return
    
async def admin_delete_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    isCreator = context.user_data.get("isCreator", None)

    if(isCreator):
        await query.answer()
    else:
        await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
        return
    
    channel_id = check_channel_id(query, context)

    keyboard = [
            [InlineKeyboardButton("✅ Conferma", callback_data=f'channeloffers_admindeletechannelconfirm_{channel_id}')],
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_adminpanel_{channel_id}')]
        ]
    
    await query.edit_message_text(
            text="Sei sicuro di voler cancellare il canale?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    

async def admin_delete_channel_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    isCreator = context.user_data.get("isCreator", None)

    if(isCreator):
        await query.answer()
    else:
        await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
        return
    
    channel_id = check_channel_id(query, context)

    try:
        with CanaleDAO() as canaleDAO:
            canaleDAO.delete(channel_id)
        text = "Canale cancellato con successo!"
    except:
        text = "Errore nella cancellazione del canale..."

    keyboard = [
        [InlineKeyboardButton("⬅️ Home", callback_data=f'back_to_main')]
    ]

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )