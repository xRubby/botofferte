from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, User
from telegram.ext import ContextTypes

import os

from database.session import SessionLocal
from enums.esito_invito import EsitoInvito
from services.invito_service import InvitoService
from services.utente_service import UtenteService

TASTIERA_HOME = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔍 Cerca prodotto", callback_data="cerca_prodotto")],
    [InlineKeyboardButton("🛒 Offerte Canale",  callback_data="channeloffers_main")],
    [InlineKeyboardButton("⚙️ Impostazioni",    callback_data="settings")],
])

def get_benvenuto(utente: User) -> str:
    user_link = f"<a href='tg://user?id={utente.id}'>{utente.first_name}</a>"
    return (
        f"📌 <b>Benvenuto</b> {user_link}\n\n"
        "Scegli ciò di cui hai bisogno dai tasti in basso ⤵️\n\n"
        "🔍 <b>Cerca prodotto</b> ti permette di ottenere il prodotto "
        "desiderato da Amazon e scoprire se è in sconto.\n\n"
        "🛒 <b>Offerte Canale</b> ti permette di pubblicare "
        "offerte <b>Amazon</b> nei tuoi canali Telegram.\n\n"
        "⚙️ <b>Impostazioni</b> ti permette di modificare le impostazioni "
        "di questa chat <b>(IN LAVORAZIONE)</b>."
    )

def aggiungiUtente(userID, first_name):
    USER_ID_ADMIN = os.getenv('USER_ID_ADMIN')

    with SessionLocal() as session:

        utente_service = UtenteService(session)
        try:
            if not utente_service.ottieni_utente(userID):
                if userID == int(USER_ID_ADMIN):
                    utente_service.crea_utente(userID, first_name, True)
                else:
                    utente_service.crea_utente(userID, first_name)

            session.commit()
        except Exception:
            session.rollback()
            raise

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    utente = update.effective_user

    aggiungiUtente(utente.id, utente.first_name)

    text=get_benvenuto(utente)

    keyboard = TASTIERA_HOME

    if ctx.args:
        token = ctx.args[0]
        with SessionLocal() as session:

            invito_service = InvitoService(session)

            try:

                esito = invito_service.accetta_invito(token = token, telegram_id = utente.id)

                match esito:
                    case EsitoInvito.OK:
                        text = "Sei stato inserito correttamente all'interno del canale!"

                    case EsitoInvito.NON_TROVATO:
                        text = "L'invito al canale non è stato trovato."

                    case EsitoInvito.SCADUTO:
                        text = "L'invito al canale è scaduto. Richiedine uno nuovo."

                    case EsitoInvito.GIA_MEMBRO:
                        text = "Fai già parte di questo canale."

                session.commit()

            except Exception:
                session.rollback()
                raise

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Home", callback_data="back_to_main")]
        ])

    await update.message.reply_text(
            text=text,
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    
async def handler_menu_principale(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    utente = update.effective_user
    testo = get_benvenuto(utente)

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=testo,
            parse_mode="HTML",
            reply_markup=TASTIERA_HOME,
        )
    else:
        await update.message.reply_text(
            text=testo,
            parse_mode="HTML",
            reply_markup=TASTIERA_HOME,
        )