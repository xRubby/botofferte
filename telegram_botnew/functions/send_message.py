import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions, Update
from telegram.ext import ContextTypes

from APIs.bitly_api import shorten_url
from database.DAO.ProdottoDAO import ProdottoDAO
from database.DAO.PubblicaDAO import PubblicaDAO
from database.DAO.CanaleDAO import CanaleDAO
from database.DAO.GestisceDAO import GestisceDAO
from database.DAO.LayoutDAO import LayoutDAO
from database.Entity.Layout import Layout
from database.Entity.Prodotto import Prodotto
from database.Entity.Pubblica import Pubblica
from scraper.amazon_scraper import scraping_product

from utils.amazon_utils import extract_asin_from_url, is_future_date, search_warehouse_seller_id_from_link
from utils.expand_link import expand_url
from utils.send_message_utils import venduto_e_spedito

from dotenv import load_dotenv
import os

load_dotenv()
ASSOCIATE_TAG = os.getenv('ASSOCIATE_TAG')

def prodotto_to_dict(prodotto: Prodotto) -> dict | None:
    if not prodotto:
        return None
    return {
        "ASIN": prodotto.asin,
        "titolo": prodotto.titolo,
        "prezzo": prodotto.prezzo,
        "old_prezzo": prodotto.old_prezzo,
        "valuta": prodotto.valuta,
        "sconto": prodotto.sconto,
        "venditore": prodotto.venditore,
        "spedito_Amazon": prodotto.spedito_Amazon,
        "spedito": venduto_e_spedito(prodotto.venditore, prodotto.spedito_Amazon),
        "link": prodotto.link,
        "link_short": shorten_url(prodotto.link),
        "img_url": prodotto.img_url,
        "brand": prodotto.brand,
        "preorder": "Preordine" if prodotto.preorder else "",
        "data_preordine": prodotto.data_preordine,
        "prime": "Spedizione gratuita e veloce con <b><a href='https://amzn.to/4eFvUvQ'>Amazon Prime</a></b>" if prodotto.isPrime else "",
        "isWarehouse": prodotto.isWarehouse,
        "condizione": prodotto.condizione,
        "condizione_commento": prodotto.condizione_descrizione,
    }

def creaDizionarioProdotto(risultato: dict) -> dict | None:
    if (risultato):
        prodotto = Prodotto(risultato["ASIN"], risultato["titolo"], risultato["prezzo"], risultato["old_prezzo"], risultato["valuta"],
        risultato["sconto"], risultato["venditore"], risultato["spedito_Amazon"], risultato["link"], risultato["img_url"], risultato["brand"],
        risultato["preordine"], risultato["data_preordine"], risultato["isPrime"], risultato["isWarehouse"], risultato["condizione"],
        risultato["condizione_descrizione"], 0, 0, risultato["offertaesclusiva"])

        prodotto.link+= f"?tag={ASSOCIATE_TAG}"

        prodotto_dict = {
            "ASIN": prodotto.asin,
            "titolo": prodotto.titolo,
            "prezzo": prodotto.prezzo,
            "old_prezzo": prodotto.old_prezzo,
            "valuta": prodotto.valuta,
            "sconto": prodotto.sconto,
            "venditore": prodotto.venditore,
            "spedito_Amazon": prodotto.spedito_Amazon,
            "spedito": venduto_e_spedito(prodotto.venditore, prodotto.spedito_Amazon),
            "link": prodotto.link,
            "link_short": shorten_url(prodotto.link),
            "img_url": prodotto.img_url,
            "brand": prodotto.brand,
            "preorder": "Preordine" if prodotto.preorder else "",
            "data_preordine": prodotto.data_preordine,
            "prime": "Spedizione gratuita e veloce con <b><a href='https://amzn.to/4eFvUvQ'>Amazon Prime</a></b>" if prodotto.isPrime else "",
            "isWarehouse": prodotto.isWarehouse,
            "condizione": prodotto.condizione,
            "condizione_commento": prodotto.condizione_descrizione
            }
        
        return prodotto_dict
    
    return None

def clean_text(text):
    lines = text.split("\n")
    
    cleaned_lines = []
    previous_empty = False

    for line in lines:
        if line.strip():
            cleaned_lines.append(line)
            previous_empty = False
        elif not previous_empty:
            cleaned_lines.append("")
            previous_empty = True

    return "\n".join(cleaned_lines)

def processa_messaggio(template, context):
    
    def sostituisci_condizionale(match):
        contenuto = match.group(1)
        
        segnaposto_presenti = re.findall(r'\{(.*?)\}', contenuto)
        
        tutte_verificate = all(context.get(var.strip()) for var in segnaposto_presenti)
        
        return contenuto if tutte_verificate else ""

    messaggio = re.sub(r'\{_(.*?)_\}', lambda m: sostituisci_condizionale(m), template)
    
    for key, value in context.items():
        messaggio = messaggio.replace(f"{{{key}}}", str(value))
        

    messaggio_pulito = clean_text(messaggio).strip()

    return messaggio_pulito

def check_preorder(prodotto: Prodotto) -> Prodotto:
    if not prodotto:
        return None
    
    if prodotto.preorder and prodotto.data_preordine:
        if not is_future_date(prodotto.data_preordine):
            prodotto.preorder = False
            prodotto.data_preordine = None
    return prodotto


async def search_and_send_offer(update: Update, ctx: ContextTypes.DEFAULT_TYPE, keyword: str):
    message_id = ctx.user_data.pop("msg_id", None)

    if not message_id:
        raise ValueError("ID del messaggio non trovato")

    if not keyword:
        raise ValueError("Errore nella keyword mandata")
    
    expanded_url = expand_url(keyword)
    asin = extract_asin_from_url(expanded_url)

    if not asin:
        raise ValueError("ASIN non trovato")
        
    risultato = scraping_product(asin)

    info_prodotto = creaDizionarioProdotto(risultato)

    if not info_prodotto:
        raise ValueError("Errore durante l'elaborazione delle informazioni del prodotto")

    messaggio = (
        "📦 <i>{_{preorder}:_}</i><i>{_{warehouse}:_}</i> <b>{titolo}</b> {_- <b>In uscita il {data_preordine}</b>_}\n"
        "\n"
        "💶 <b>{prezzo}{valuta}</b> {_(invece di: {old_prezzo}{valuta}, <i>{sconto}% di sconto</i>)_}\n"
        "{_🔄 Condizione: {condizione} ({condizione_commento})_}\n"
        "\n"
        "🚚 {spedito} {_| {prime}_}\n"
        "\n\n"
        "📌 Scopri l'offerta qui: {link_short}"
    )

    message = processa_messaggio(messaggio, info_prodotto)

    keyboard = [
                [InlineKeyboardButton("🛒 Acquista su Amazon!", url=info_prodotto["link"])],
                [InlineKeyboardButton("⬅️ Indietro", callback_data="back_to_main")]
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    

    await ctx.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=message_id,
        text=message,                        
        parse_mode='HTML',
        reply_markup=reply_markup,
        link_preview_options=LinkPreviewOptions(url=info_prodotto["img_url"])
    )


TEMPLATE_MESSAGE = (
    "📦 <b>{titolo}</b>\n"
    "💲 <i>Prezzo vecchio:</i> {old_prezzo}{valuta}\n"
    "💰 <i>Prezzo nuovo:</i> <b>{prezzo}{valuta}</b>\n"
    "📉 <i>Sconto:</i> {sconto}%\n\n"
    "🚚 {spedito}\n\n"
    "🔗 <b>Scopri l'offerta:</b> <a href=\"{link}\">Clicca qui!</a>"
)

async def search_offer(update: Update, ctx: ContextTypes.DEFAULT_TYPE, keyword: str):
    user_id = update.effective_user.id 
    channel_id = ctx.user_data.get("channel_id", None)

    if not channel_id:
        raise ValueError("Errore nel ritrovamento dell'id del canale")

    if not keyword:
        raise ValueError("Errore nella keyword mandata")
    
    with GestisceDAO() as gestisceDAO:
        gestisce = gestisceDAO.get(user_id, channel_id)
    
    expanded_url = expand_url(keyword)
    asin = extract_asin_from_url(expanded_url)

    if not asin:
        raise ValueError("ASIN non trovato")
    

    risultato = scraping_product(asin)
    info_prodotto = creaDizionarioProdotto(risultato)

    if not info_prodotto:
        raise ValueError("Errore durante l'elaborazione delle informazioni del prodotto")

    with ProdottoDAO() as prodottoDAO:
        prodotto_from_db = prodottoDAO.get_by_asin(asin)
        if not prodotto_from_db:
            prodottoDAO.insert(
                asin=info_prodotto["ASIN"],
                titolo=info_prodotto["titolo"],
                prezzo=info_prodotto["prezzo"],
                old_prezzo=info_prodotto["old_prezzo"],
                valuta=info_prodotto["valuta"],
                sconto=info_prodotto["sconto"],
                venditore=info_prodotto["venditore"],
                spedito_Amazon=info_prodotto["spedito_Amazon"],
                link=info_prodotto["link"],
                img_url=info_prodotto["img_url"],
                brand=info_prodotto["brand"],
                preorder=bool(info_prodotto["preorder"]),
                data_preordine=info_prodotto["data_preordine"],
                isPrime=bool(info_prodotto["prime"]),
                isWarehouse=info_prodotto["isWarehouse"],
                condizione=info_prodotto["condizione"],
                condizione_descrizione=info_prodotto["condizione_commento"],
                offertaesclusiva=info_prodotto.get("offertaesclusiva", None)
            )
        else:
            if prodotto_from_db.prezzo != info_prodotto["prezzo"]:
                prodottoDAO.update_price(info_prodotto["ASIN"], info_prodotto["prezzo"], info_prodotto["old_prezzo"], info_prodotto["valuta"],
                                    info_prodotto["sconto"], info_prodotto["venditore"], info_prodotto["spedito_Amazon"], info_prodotto.get("offertaesclusiva", None))

    if gestisce and gestisce.id_affiliato:
        info_prodotto.link+= f"?tag={gestisce.id_affiliato}"
    else:
        with CanaleDAO() as canaleDAO:
            canale = canaleDAO.get(channel_id)
        if canale and canale.id_affiliato:
            info_prodotto.link+= f"?tag={canale.id_affiliato}"

    with LayoutDAO() as layoutDAO:
        layout_in_uso = layoutDAO.get_in_uso(channel_id)

    layout_messaggio = layout_in_uso.messaggio if layout_in_uso else TEMPLATE_MESSAGE

    message = processa_messaggio(layout_messaggio, info_prodotto)

    with PubblicaDAO() as pubblicaDAO:
        pubblicaDAO.insert(channel_id, info_prodotto["ASIN"], message)

async def publish_offer(update: Update, context: ContextTypes.DEFAULT_TYPE, link: Pubblica):
    
    with ProdottoDAO() as prodotto_dao:
        prodotto = prodotto_dao.get_by_asin(link.asin_prodotti)
                   
    try:
        await context.bot.send_photo(
            chat_id=link.id_canale,
            photo=prodotto.img_url, 
            caption=link.messaggio,
            parse_mode='HTML'
        )
        
    except Exception as e:
        raise Exception("Il bot non è un admin del canale") 
        




