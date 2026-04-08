from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, User
from telegram.ext import ContextTypes

from database.Connessione import Connessione

import os

from database.DAO.UtenteDAO import UtenteDAO

TASTIERA_HOME = InlineKeyboardMarkup([
    [InlineKeyboardButton("🔍 Cerca prodotto", callback_data="cerca_prodotto")],
    [InlineKeyboardButton("🛒 Offerte Canale",  callback_data="offerte_canale")],
    [InlineKeyboardButton("⚙️ Impostazioni",    callback_data="settings")],
])

def get_benvenuto(utente: User) -> str:
    user_link = f"<a href='tg://user?id={utente.id}'>{utente.first_name}</a>"
    return (
        f"🔸 <b>Benvenuto</b> {user_link}\n\n"
        "Scegli ciò di cui hai bisogno dai tasti in basso ⤵️\n\n"
        "🔍 <b>Cerca prodotto</b> ti permette di ottenere il prodotto "
        "desiderato da Amazon e scoprire se è in sconto.\n\n"
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
    utente = update.effective_user

    aggiungiUtente(utente.id, utente.first_name)
    
    await update.message.reply_text(
            text=get_benvenuto(utente),
            parse_mode="HTML",
            reply_markup=TASTIERA_HOME,
        )
    
async def handler_menu_principale(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    utente = update.effective_user

    await query.edit_message_text(
        text=get_benvenuto(utente),
        parse_mode="HTML",
        reply_markup=TASTIERA_HOME,
    )