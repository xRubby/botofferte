from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, User
from telegram.ext import ContextTypes

from database.Connessione import Connessione

import os

from database.DAO.GestisceDAO import GestisceDAO
from database.DAO.InvitoDAO import InvitoDAO
from database.DAO.UtenteDAO import UtenteDAO

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
        "📢 <b>Offerte Canale</b> ti permette di pubblicare "
        "offerte <b>Amazon</b> nei tuoi canali Telegram.\n\n"
        "⚙️ <b>Impostazioni</b> ti permette di modificare le impostazioni "
        "di questa chat <b>(IN LAVORAZIONE)</b>."
    )

def aggiungiUtente(userID, first_name):
    USER_ID_ADMIN = os.getenv('USER_ID_ADMIN')
    with UtenteDAO() as utenteDAO:
        if not utenteDAO.get(userID):
            if userID == int(USER_ID_ADMIN):
                utenteDAO.insert(userID, first_name, 1)
            else:
                utenteDAO.insert(userID, first_name)



async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"[DEBUG] update.message.text: {update.message.text}")
    print(f"[DEBUG] ctx.args: {ctx.args}")
    print(f"[DEBUG] ctx.args type: {type(ctx.args)}")
    utente = update.effective_user

    aggiungiUtente(utente.id, utente.first_name)

    text=get_benvenuto(utente)

    keyboard = TASTIERA_HOME

    if ctx.args:
        token = ctx.args[0]
        print("Token ricevuto")
        with InvitoDAO() as invitoDAO:
            invito = invitoDAO.get(token)

            if not invito:
                await handler_menu_principale(update, ctx)
                return
            
            invitoDAO.delete(token)
        if(datetime.today() < datetime.strptime(invito.data_creazione, "%Y-%m-%d %H:%M:%S.%f") + timedelta(hours=2)):
            try:
                with GestisceDAO() as gestisceDAO:
                    gestisceDAO.insert(utente.id, invito.canale_id, "", False)
                text = "Sei stato inserito correttamente all'interno del canale!"
            except Exception as e:
                text = "Fai già parte di questo canale."
        else:
            text = "L'invito al canale è scaduto. Richiedine uno nuovo."
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