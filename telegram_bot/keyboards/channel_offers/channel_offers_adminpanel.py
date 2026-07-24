from datetime import datetime
import os
import secrets
import traceback
from dotenv import load_dotenv
import math

from telegram import *
from telegram.ext import *

from database.session import SessionLocal
from enums.StatoLicenza import StatoLicenza
from models.invito import Invito
from services.canale_service import CanaleService
from services.gestisce_service import GestisceService
from services.invito_service import InvitoService
from services.licenza_service import LicenzaService
from utils.channel_offers_utils import check_channel_id

load_dotenv()

ATTESA_ID_AFFILIATO = "ATTESA_ID_AFFILIATO"

BOT_USERNAME = os.getenv("BOT_USERNAME")

async def check_is_creator(query: CallbackQuery, update: Update, context: ContextTypes.DEFAULT_TYPE, channel_id):
    user_id = update.effective_user.id
    isCreator = context.user_data.get("isCreator", False)

    if not isCreator:
        with SessionLocal() as session:
            gestisce_service = GestisceService(session)

            gestisce_info = gestisce_service.ottieni_gestione(user_id, channel_id)

            if(gestisce_info and gestisce_info.is_creator):
                context.user_data['isCreator'] = True
                isCreator = True

    if isCreator:
        await query.answer()
        return True
    else:
        await query.answer(text="Non puoi visualizzare quest'area", show_alert=True)
        return False

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    channel_id = check_channel_id(query, context)

    if await check_is_creator(query, update, context, channel_id):
        
        text = (
            "🛠️ <b>Pannello Admin</b>\n\n"
            "📊 Gestisci le impostazioni del tuo canale.\n\n"
            "Seleziona un’opzione qui sotto 👇"
        )
        keyboard = [
            [InlineKeyboardButton("👥 Gestisci Membri", callback_data=f'channeloffers_managemembers_{channel_id}_0')],
            [InlineKeyboardButton("🏷️ Tag affiliato", callback_data=f'channeloffers_adminaffiliateid_{channel_id}'), InlineKeyboardButton("📄 Informazioni Licenza", callback_data=f'channeloffers_adminlicenseinfo_{channel_id}')],
            [InlineKeyboardButton("🗑️ Cancella canale", callback_data=f'channeloffers_admindeletechannel_{channel_id}')],
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_info_{channel_id}')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

MEMBERS_PER_PAGE = 10

async def admin_manage_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("_")

    channel_id = int(data[2])
    page = int(data[3]) if len(data) > 3 else 0

    if await check_is_creator(query, update, context, channel_id):

        offset = page * MEMBERS_PER_PAGE

        text = (
            "👥 <b>Gestione Membri</b>\n\n"
            "ℹ️ Qui puoi visualizzare tutti i membri che hanno accesso a questo canale.\n\n"
            "➕ Utilizza il pulsante <b>Invita membri</b> per aggiungere nuovi utenti."
        )

        keyboard = []

        keyboard.append([
            InlineKeyboardButton(
                "➕ Invita membri",
                callback_data=f"channeloffers_invitemember_{channel_id}"
            )
        ])

        keyboard.append([
            InlineKeyboardButton(
                "-----",
                callback_data=f"none"
            )
        ])

        with SessionLocal() as session:
            gestisce_service = GestisceService(session)

            lista_membri = gestisce_service.ottieni_lista_membri_canale(channel_id, MEMBERS_PER_PAGE, offset)

            total_members = gestisce_service.conta_membri_canale(channel_id)

            if lista_membri:
                for membro in lista_membri:
                    utente = membro.utente

                    keyboard.append([
                        InlineKeyboardButton(
                            utente.nome,
                            callback_data=f"channeloffers_memberinfo_{channel_id}_{utente.telegram_id}"
                        )
                    ])

        keyboard.append([
            InlineKeyboardButton(
                "-----",
                callback_data=f"none"
            )
        ])

        total_pages = max(1, math.ceil(total_members / MEMBERS_PER_PAGE))

        nav_row = []

        if page > 0:
            nav_row.append(
                InlineKeyboardButton(
                    "⬅️",
                    callback_data=f"channeloffers_managemembers_{channel_id}_{page - 1}"
                )
            )

        if (page + 1) < total_pages:
            nav_row.append(
                InlineKeyboardButton(
                    "➡️",
                    callback_data=f"channeloffers_managemembers_{channel_id}_{page + 1}"
                )
            )

        keyboard.append(nav_row)

        keyboard.append([
            InlineKeyboardButton(
                "⬅️ Indietro",
                callback_data=f"channeloffers_adminpanel_{channel_id}"
            )
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

async def admin_member_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data.split("_")

    channel_id = int(data[2])
    telegram_id = int(data[3])

    if await check_is_creator(query, update, context, channel_id):

        with SessionLocal() as session:
            gestisce_service = GestisceService(session)

            gestisce = gestisce_service.ottieni_gestione(telegram_id, channel_id)

            if not gestisce:
                return

            utente = gestisce.utente

            if not utente:
                return

        id_affiliato = gestisce.id_affiliato if gestisce.id_affiliato else "Nessuno"

        text = (
            "👤 <b>Info Membro</b>\n\n"
            f"🏷️ <b>Nome:</b> {utente.nome}\n"
            f"🧾 <b>ID affiliato:</b> {id_affiliato}"
        )

        keyboard = []

        if not gestisce.is_creator:
            keyboard.append([InlineKeyboardButton("🗑️ Rimuovi Membro", callback_data=f"channeloffers_removemember_{channel_id}_{telegram_id}")])

        keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f"channeloffers_managemembers_{channel_id}_0")])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    
async def admin_remove_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    data = query.data.split("_")
    channel_id = int(data[2])
    telegram_id = int(data[3])

    if await check_is_creator(query, update, context, channel_id): 
        keyboard = [
            [InlineKeyboardButton("✅ Sì, rimuovi", callback_data=f"channeloffers_confirmremovemember_{channel_id}_{telegram_id}")],
            [InlineKeyboardButton("❌ Annulla", callback_data=f"channeloffers_memberinfo_{channel_id}_{telegram_id}")]
        ]

        text = (
            "⚠️ <b>Conferma rimozione</b>\n\n"
            "Sei sicuro di voler rimuovere questo membro?")

        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

async def admin_remove_member_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    data = query.data.split("_")
    channel_id = int(data[2])
    telegram_id = int(data[3])

    if await check_is_creator(query, update, context, channel_id):
        with SessionLocal() as session:
            gestisce_service = GestisceService(session)

            gestione = gestisce_service.ottieni_gestione(telegram_id, channel_id)

            text = "⚠️ <b>Operazione non consentita</b>\n\nNon puoi rimuovere il creatore del canale."

            if not gestione.is_creator:
                try:
                    gestisce_service.rimuovi_gestione(gestione)

                    session.commit()

                    text="✅ Membro rimosso con successo."
                except Exception:
                    session.rollback()

                    text = "❌ Errore durante la rimozione dell'utente."


        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Torna ai membri", callback_data=f"channeloffers_managemembers_{channel_id}_0")]
            ])
        )

async def admin_edit_affiliateid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    channel_id = check_channel_id(query, context)

    if await check_is_creator(query, update, context, channel_id):

        with SessionLocal() as session:
            canale_service = CanaleService(session)

            canale = canale_service.ottieni_canale(channel_id)
            
        id_affiliato = canale.id_affiliato if canale.id_affiliato else "Nessuno"
            
        text = (
            "🏷️ <b>Configurazione ID Affiliato</b>\n\n"
            "ℹ️ Questo ID verrà utilizzato automaticamente come predefinito durante la pubblicazione dei prodotti.\n\n"
            f"🔑 <b>ID attuale:</b> <code>{id_affiliato}</code>\n\n"
            "✏️ Invia un nuovo ID per aggiornarlo."
        )

        keyboard = [
            [InlineKeyboardButton("❌ Rimuovi ID Affiliato", callback_data=f'channeloffers_adminremoveaffiliateid_{channel_id}')],
            [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_adminpanel_{channel_id}')]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = await query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

        context.user_data["msg_id"] = msg.id

        return ATTESA_ID_AFFILIATO

async def admin_ricevi_affiliate_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    message_id = context.user_data.pop("msg_id", None)
    channel_id = context.user_data.get('channel_id')
    affiliate_id = update.message.text

    await update.message.delete()
    with SessionLocal() as session:
        try:
            canale_service = CanaleService(session)

            canale = canale_service.ottieni_canale(channel_id)
            
            canale.id_affiliato = affiliate_id

            session.commit()

            text = f"✅ <b>ID Affiliato aggiornato con successo!</b>\n\n"
            text += f"🔑 Nuovo ID: <code>{affiliate_id}</code>"
        except Exception as e:
            session.rollback()

            text = (
                "❌ <b>Errore durante l'aggiornamento</b>\n\n"
                "⚠️ Non è stato possibile aggiornare l'ID Affiliato.\n"
                "Riprova più tardi o verifica i dati inseriti."
            )

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
    channel_id = check_channel_id(query, context)

    if await check_is_creator(query, update, context, channel_id):
        with SessionLocal() as session:
            try:
                
                canale_service = CanaleService(session)

                canale = canale_service.ottieni_canale(channel_id)
                
                canale.id_affiliato = ""

                session.commit()

                text = (
                    "🗑️ <b>ID Affiliato rimosso con successo</b>"
                )
            except Exception as e:
                session.rollback()
                text = (
                    "❌ <b>Errore durante la rimozione</b>\n\n"
                    "⚠️ Non è stato possibile rimuovere l'ID Affiliato.\n"
                    "Riprova più tardi."
                )

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

    if await check_is_creator(query, update, context, channel_id):

        try:

            with SessionLocal() as session:
                canale_service = CanaleService(session)

                canale = canale_service.ottieni_canale(channel_id)

                if not canale:
                    raise ValueError()

                licenza = canale.licenza

                if not licenza:
                    raise ValueError()

                stato_licenza = LicenzaService(session).get_stato(licenza)

            text = (
                f"📄 <b>Informazioni Licenza</b>\n\n"
                f"🔑 <b>Codice:</b> <code>{licenza.codice_licenza}</code>\n"
                f"📦 <b>Tipo:</b> {licenza.tipo.title()}\n\n"
            )

            if stato_licenza == StatoLicenza.ATTIVA:
                text += (
                    f"🟢 <b>Stato:</b> Attiva\n"
                    f"📅 <b>Attivazione:</b> {licenza.data_attivazione}\n"
                    f"⏳ <b>Scadenza:</b> {"Mai" if not licenza.data_scadenza else licenza.data_scadenza}"
                )
            else:
                text += "🔴 <b>Stato:</b> Non attiva"
            
            keyboard = [
                [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_adminpanel_{channel_id}')]
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
    
async def admin_delete_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    channel_id = check_channel_id(query, context)

    if await check_is_creator(query, update, context, channel_id):
        keyboard = [
                [InlineKeyboardButton("✅ Conferma", callback_data=f'channeloffers_admindeletechannelconfirm_{channel_id}')],
                [InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_adminpanel_{channel_id}')]
            ]
        
        text = (
            "⚠️ <b>Conferma eliminazione canale</b>\n\n"
            "Sei sicuro di voler <b>cancellare definitivamente</b> questo canale?\n"
            "Questa azione è <b>irreversibile</b>."
        )
        
        await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
    

async def admin_delete_channel_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    channel_id = check_channel_id(query, context)

    if await check_is_creator(query, update, context, channel_id):

        with SessionLocal() as session:
            try:
                canale_service = CanaleService(session)

                canale = canale_service.ottieni_canale(channel_id)

                canale_service.rimuovi_canale(canale)

                session.commit()

                text = (
                    "🗑️ <b>Canale eliminato con successo</b>\n\n"
                    "ℹ️ Il canale è stato rimosso definitivamente."
                )
            except:

                traceback.print_exc()
                session.rollback()

                text = (
                    "❌ <b>Errore durante la cancellazione</b>\n\n"
                    "⚠️ Non è stato possibile eliminare il canale.\n"
                    "Riprova più tardi o verifica i permessi."
                )

            keyboard = [
                [InlineKeyboardButton("⬅️ Home", callback_data=f'back_to_main')]
            ]

            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )

async def admin_invite_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    channel_id = check_channel_id(query, context)

    if await check_is_creator(query, update, context, channel_id):
    
        create_link = context.user_data.pop('create_link', None)
        token = context.user_data.pop('token', None)
        
        text = (
            "➕ <b>Gestione Inviti Canale</b>\n\n"
            "ℹ️ In questa sezione puoi invitare altri membri a collaborare nella gestione del tuo canale.\n"
        )

        keyboard = [
        ]

        if create_link and token:
            text += (
                "\n🔗 <b>Link di invito generato:</b>\n"
                f"<code>t.me/{BOT_USERNAME}?start={token}</code>"
            )
            keyboard.append([InlineKeyboardButton("🗑️ Rimuovi link membro", callback_data=f"channeloffers_adminremovelinkmember_{channel_id}")])
        else:
            keyboard.append([InlineKeyboardButton("🔗 Genera link membro", callback_data=f"channeloffers_admincreatelinkmember_{channel_id}")])

        keyboard.append([InlineKeyboardButton("⬅️ Indietro", callback_data=f'channeloffers_managemembers_{channel_id}_0')])
        

        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

def cancella_invito_se_esiste(invito_service: InvitoService, channel_id: str) -> None:

    invito_canale = invito_service.ottieni_invito_per_canale(channel_id)
    if invito_canale:
        invito_service.cancella_invito(invito_canale)

async def admin_invite_member_createlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    channel_id = check_channel_id(query, context)

    if await check_is_creator(query, update, context, channel_id):

        token = secrets.token_hex(4).upper()

        with SessionLocal() as session:
            try:
                invito_service = InvitoService(session)

                cancella_invito_se_esiste(invito_service, channel_id)

                invito = Invito(token=token, data_creazione = datetime.today().replace(microsecond=0), canale_id = channel_id)

                invito_service.crea_invito(invito)

                session.commit()

            except Exception as e:
                session.rollback()

                print(e)

        context.user_data['create_link'] = True
        context.user_data['token'] = token

        await admin_invite_member(update, context)

async def admin_invite_member_removelink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    channel_id = check_channel_id(query, context)

    if await check_is_creator(query, update, context, channel_id):
    
        context.user_data['create_link'] = False

        with SessionLocal() as session:
            try:
                invito_service = InvitoService(session)

                cancella_invito_se_esiste(invito_service, channel_id)

                session.commit()
            except Exception as e:
                session.rollback()
                print(e)

        await admin_invite_member(update, context)