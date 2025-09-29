import re
from APIs.amazon_api import search_amazon_offers
from dotenv import load_dotenv
import os
#from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions
from telegram.ext import ContextTypes
import logging

import traceback

from database.Entity.Prodotto import Prodotto
from database.Entity.Pubblica import Pubblica
from database.Entity.Gestisce import Gestisce

from database.DAO.CanaleDAO import CanaleDAO
from database.DAO.ProdottoDAO import ProdottoDAO
from database.DAO.PubblicaDAO import PubblicaDAO
from database.DAO.LayoutDAO import LayoutDAO
from database.DAO.GestisceDAO import GestisceDAO

from utils.amazon_utils import extract_asin_from_url, search_warehouse_seller_id_from_link, is_future_date
from utils.expand_link import expand_url
from utils.send_message_utils import venduto_e_spedito
from telegram_bot.messages.messages_it import getTemplateMessage

from scraper.amazon_scraper import scraping_product

from APIs.bitly_api import shorten_url

from telegram_bot.functions.update_prices import aggiorna_prezzo
import time

load_dotenv()
ASSOCIATE_TAG = os.getenv('ASSOCIATE_TAG')

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
        

    messaggio = clean_text(messaggio)

    return messaggio

def check_preorder(prodotto: Prodotto) -> Prodotto:
    if prodotto:
        if prodotto.preorder and prodotto.data_preordine:
            if not is_future_date(prodotto.data_preordine):
                with ProdottoDAO() as dao:
                    dao.update_preorder(prodotto.asin, False, None)
                
                prodotto.preorder = False
                prodotto.data_preordine = None
        return prodotto


async def search_and_send_offer(update: Update, context: ContextTypes.DEFAULT_TYPE, keyword: str):


    user_id = update.effective_user.id 
    message_id = context.user_data.get(user_id, {}).get('message_id')


    keyboard_back = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data="back_to_main")]
    ]
    reply_markup_back = InlineKeyboardMarkup(keyboard_back)
    
    try:
        if keyword:
            try:
                expanded_url = expand_url(keyword)

                asin = extract_asin_from_url(expanded_url)
                
                if asin:
                    keyword = asin
                    warehouse_seller_id = search_warehouse_seller_id_from_link(expanded_url)
                    is_warehouse = warehouse_seller_id == "A1HO9729ND375Y"

                with ProdottoDAO() as prodotto_dao:
                    prodotto = None

                    prodotto = prodotto_dao.get_by_asin(keyword)

                    if not prodotto:
                        prodotto = prodotto_dao.get_by_titolo(keyword)

                    #if is_warehouse:
                            
                    #    offers = search_amazon_offers(keyword, warehouse_seller_id)

                    #    offer = offers[0]

                    #    prodotto = Prodotto(offer["ASIN"], offer["titolo"], offer["prezzo"], offer["old_prezzo"], offer["valuta"], offer["sconto"],
                    #                        offer["venditore"], offer["spedito_Amazon"], offer["link"], offer["img_url"], offer["brand"], offer["preordine"], offer["data_preordine"],
                    #                        offer["isPrime"], offer["isWarehouse"], offer["condizione"], offer["condizione_descrizione"])
                
                    if not prodotto :
                        try:
                            offer = scraping_product(asin)

                            prodotto = Prodotto(offer["ASIN"], offer["titolo"], offer["prezzo"], offer["old_prezzo"], offer["valuta"], offer["sconto"],
                                                offer["venditore"], offer["spedito_Amazon"], offer["link"], offer["img_url"], offer["brand"], offer["preordine"], offer["data_preordine"],
                                                offer["isPrime"], offer["isWarehouse"], offer["condizione"], offer["condizione_descrizione"], int(time.time()), 1)
                            
                            
                            prodotto_dao.insert_Prodotto(prodotto)

                        except Exception as e:
                            traceback.print_exc()
                            prodotto = prodotto_dao.get_by_asin(offer["ASIN"])
                            
                    if prodotto:

                        prodotto = aggiorna_prezzo(prodotto)

                        prodotto= check_preorder(prodotto)

                        prodotto.link+= f"?tag={ASSOCIATE_TAG}"

                        prodotto_dict={
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
            except Exception as e:
                traceback.print_exc()
    except Exception as e:
        logging.error("ERRORE")

 
    messaggio = (
    """📦 <i>{_{preorder}:_}</i><i>{_{warehouse}:_}</i> <b>{titolo}</b> {_- <b>In uscita il {data_preordine}</b>_}
    
💶 <b>{prezzo}{valuta}</b> {_(invece di: {old_prezzo}{valuta}, <i>{sconto}% di sconto</i>)_}
{_🔄 Condizione: {condizione} ({condizione_commento})_}
                        
🚚 {spedito} {_| {prime}_}
                        
📌 Scopri l'offerta qui: {link_short}"""
    )

    try:
        message = processa_messaggio(messaggio, prodotto_dict)
    except Exception as e:
        logging.error(f"Errore durante la costruzione del messaggio: {e}")
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=message_id,
            text="Errore durante la costruzione del messaggio. Riprova più tardi.",
            parse_mode='HTML',
            reply_markup=reply_markup_back
        )

    keyboard = [
                [InlineKeyboardButton("🛒 Acquista su Amazon!", url=prodotto.link)],
                [InlineKeyboardButton("⬅️ Indietro", callback_data="back_to_main")]
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=message_id,
                    text=message,                        
                    parse_mode='HTML',
                    reply_markup=reply_markup,
                    link_preview_options=LinkPreviewOptions(url=prodotto.img_url)
                    )
    except Exception as e:
                logging.error(f"Errore durante la modifica del messaggio: {e}")
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=message_id,
                    text="Errore durante la modifica del messaggio. Riprova più tardi.",
                    parse_mode='HTML',
                    reply_markup=reply_markup_back
                )


async def search_offer(update: Update, context: ContextTypes.DEFAULT_TYPE, channel_id: str, keyword: str):

    user_id = update.effective_user.id 
    message_id = context.user_data.get(user_id, {}).get('message_id')

    try:
        if keyword:
            try:
                expanded_url = expand_url(keyword)

                asin = extract_asin_from_url(expanded_url)
                
                if asin:
                    keyword = asin

                with ProdottoDAO() as prodotto_dao:
                    prodotto = None

                    prodotto = prodotto_dao.get_by_asin(keyword)

                    if not prodotto:
                        prodotto = prodotto_dao.get_by_titolo(keyword)

                    #if is_warehouse:
                            
                    #    offers = search_amazon_offers(keyword, warehouse_seller_id)

                    #    offer = offers[0]

                    #    prodotto = Prodotto(offer["ASIN"], offer["titolo"], offer["prezzo"], offer["old_prezzo"], offer["valuta"], offer["sconto"],
                    #                        offer["venditore"], offer["spedito_Amazon"], offer["link"], offer["img_url"], offer["brand"], offer["preordine"], offer["data_preordine"],
                    #                        offer["isPrime"], offer["isWarehouse"], offer["condizione"], offer["condizione_descrizione"])
                
                    if not prodotto :
                        try:
                            offer = scraping_product(asin)

                            prodotto = Prodotto(offer["ASIN"], offer["titolo"], offer["prezzo"], offer["old_prezzo"], offer["valuta"], offer["sconto"],
                                                offer["venditore"], offer["spedito_Amazon"], offer["link"], offer["img_url"], offer["brand"], offer["preordine"], offer["data_preordine"],
                                                offer["isPrime"], offer["isWarehouse"], offer["condizione"], offer["condizione_descrizione"], int(time.time()), 1)
                            
                            
                            prodotto_dao.insert_Prodotto(prodotto)

                        except Exception as e:
                            traceback.print_exc()
                            prodotto = prodotto_dao.get_by_asin(offer["ASIN"])
                            
                    if prodotto:

                        prodotto = aggiorna_prezzo(prodotto)

                        prodotto = check_preorder(prodotto)

                        with GestisceDAO() as gestisce_dao:
                            gestisce = gestisce_dao.get(user_id, channel_id)
                        if gestisce and gestisce.id_affiliato:
                            prodotto.link+= f"?tag={gestisce.id_affiliato}"
                        else:
                            with CanaleDAO() as canale_dao:
                                canale = canale_dao.get(channel_id)
                                if canale and canale.id_affiliato:
                                    prodotto.link+= f"?tag={canale.id_affiliato}"

                        prodotto_dict={
                            "ASIN": prodotto.asin,
                            "titolo": prodotto.titolo,
                            "prezzo": prodotto.prezzo,
                            "old_prezzo": prodotto.old_prezzo,
                            "valuta": prodotto.valuta,
                            "sconto": prodotto.sconto,
                            "venditore": prodotto.venditore,
                            "spedito_Amazon": prodotto.spedito_Amazon,
                            "spedito": venduto_e_spedito(prodotto.venditore, prodotto.spedito_Amazon, channel_id),
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
            except Exception as e:
                traceback.print_exc()
    except Exception as e:
        logging.error("ERRORE")

            
    with LayoutDAO() as layout_dao:
        layout_in_uso = layout_dao.get_channel_layout_activated(channel_id)

        if(layout_in_uso):
            messaggio_layout = layout_in_uso.messaggio
        else:
            messaggio_layout = getTemplateMessage()

    message = processa_messaggio(messaggio_layout, prodotto_dict)

    with PubblicaDAO() as pubblica_dao:
        pubblica_dao.insert(channel_id, prodotto.asin, message)
    

async def publish_offer(update: Update, context: ContextTypes.DEFAULT_TYPE, link: Pubblica):

       
   
    keyboard_back = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f"channel_listlinks_{link.id_canale}")]
    ]
    reply_markup_back = InlineKeyboardMarkup(keyboard_back)
        
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
        logging.error(f"Errore durante la modifica del messaggio: {e}")
        raise Exception("Il bot non è un admin del canale") 
        
        
                