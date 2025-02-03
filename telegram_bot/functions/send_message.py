import os
import re
from APIs.amazon_api import search_amazon_offers
from dotenv import load_dotenv
#from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions
from telegram.ext import ContextTypes
import logging


from database.DAO.CanaliDAO import *


load_dotenv()

CHAT_ID = os.getenv('CHAT_ID')

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
                offers = search_amazon_offers(keyword)
            except Exception as e:
                logging.error(f"Errore durante la ricerca delle offerte: {e}")
                await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text="Errore durante la ricerca delle offerte. Riprova più tardi.",
                            parse_mode='HTML',
                            reply_markup=reply_markup_back
                        )
                return
            
            if offers:
                offer = offers[0]

                try:
                    context_dict = {
                        "titolo": offer['name'],
                        "prezzo_nuovo": offer['new_price'],
                        "prezzo_vecchio": offer['old_price'],
                        "sconto": offer['discount_percentage'],
                        "link": offer['url'],
                        "linkfull": offer['full_url'],
                        "valuta": offer['currency'],
                        "spedito": offer['spedito'],
                        "prime": offer['prime'],
                        "preorder": offer['preorder'],
                        "preorderdate": offer['preorderdate'],
                        "warehouse": offer['warehouse'],
                        "condition": offer['condition'],
                        "conditioncomm": offer['conditioncomm'],
                        "minimo": offer['minimo']
                    }

                    messaggio = (
                        "📦 <i>{_{preorder}:_}</i><i>{_{warehouse}:_}</i> <b>{titolo}</b> {_- <b>In uscita il {preorderdate}</b>_}\n"
                        "\n"
                        "💶 <b>{prezzo_nuovo}{valuta}</b> {_(invece di: {prezzo_vecchio}{valuta}, <i>{sconto}% di sconto</i>)_}\n"
                        "{_🔄 Condizione: {condition} ({conditioncomm})_}\n"
                        "\n"
                        "🚚  {spedito} {_| Spedizione gratuita e veloce con <b><a href='https://amzn.to/4eFvUvQ'>{prime}</a></b>_}\n"
                        "\n"
                        "📌 Scopri l'offerta qui: {link}"
                    )

                    message = processa_messaggio(messaggio, context_dict)

                    keyboard = [
                        [InlineKeyboardButton("🛒 Acquista su Amazon!", url=offer['url'])],
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
                            link_preview_options=LinkPreviewOptions(url=offer['image_url'])
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
                except Exception as e:
                    logging.error(f"Errore durante la costruzione del messaggio: {e}")
                    await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text="Errore durante la costruzione del messaggio. Riprova più tardi.",
                            parse_mode='HTML',
                            reply_markup=reply_markup_back
                        )
            else:
                await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text="Nessuna offerta trovata per questa parola chiave o URL.",
                            parse_mode='HTML',
                            reply_markup=reply_markup_back
                        )
        else:
            await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text="Per favore, fornisci una parola chiave o un URL per la ricerca.",
                            parse_mode='HTML',
                            reply_markup=reply_markup_back
                        )
    except Exception as e:
        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text="Si è verificato un errore imprevisto. Riprova più tardi.",
                            parse_mode='HTML',
                            reply_markup=reply_markup_back
                        )
        logging.error(f"Errore generale nella funzione: {e}")


async def search_offer(update: Update, context: ContextTypes.DEFAULT_TYPE, channel_id: str, keyword: str):

    try:
        template = get_message_template(channel_id)

        if not template:
            logging.error(f"Nessun template trovato per il canale {channel_id}.")
            return
    except Exception as e:
        logging.error(f"Errore durante il recupero del template: {e}")
        return
    
    user_id = update.effective_user.id
    message_id = context.user_data.get(user_id, {}).get('message_id')
    
    keyboard_back = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f"channel_listlinks_{channel_id}")]
    ]
    reply_markup_back = InlineKeyboardMarkup(keyboard_back)
        
    try:
        if keyword:
            try:
                offers = search_amazon_offers(keyword)
            except Exception as e:
                raise
            
            if offers:
                offer = offers[0]

                try:
                    context_dict = {
                        "titolo": offer['name'],
                        "prezzo_nuovo": offer['new_price'],
                        "prezzo_vecchio": offer['old_price'],
                        "sconto": offer['discount_percentage'],
                        "link": offer['url'],
                        "linkfull": offer['full_url'],
                        "valuta": offer['currency'],
                        "spedito": offer['spedito'],
                        "prime": offer['prime'],
                        "preorder": offer['preorder'],
                        "preorderdate": offer['preorderdate'],
                        "warehouse": offer['warehouse'],
                        "condition": offer['condition'],
                        "conditioncomm": offer['conditioncomm'],
                        "minimo": offer['minimo']
                    }

                    return processa_messaggio(template, context_dict)
                
                except Exception as e:
                    logging.error(f"Errore durante la costruzione del messaggio: {e}")
                    await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text="Errore durante la costruzione del messaggio. Riprova più tardi.",
                            parse_mode='HTML',
                            reply_markup=reply_markup_back
                        )
            else:
                await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text="Nessuna offerta trovata per questa parola chiave o URL.",
                            parse_mode='HTML',
                            reply_markup=reply_markup_back
                        )
        else:
            await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text="Per favore, fornisci una parola chiave o un URL per la ricerca.",
                            parse_mode='HTML',
                            reply_markup=reply_markup_back
                        )
    except Exception as e:
        await context.bot.edit_message_text(
                            chat_id=update.effective_chat.id,
                            message_id=message_id,
                            text="Si è verificato un errore imprevisto. Riprova più tardi.",
                            parse_mode='HTML',
                            reply_markup=reply_markup_back
                        )
        raise

    

                  


async def publish_offer(update: Update, context: ContextTypes.DEFAULT_TYPE, channel_id: str, message: str):

       
    user_id = update.effective_user.id
    message_id = context.user_data.get(user_id, {}).get('message_id')
    
    keyboard_back = [
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f"channel_listlinks_{channel_id}")]
    ]
    reply_markup_back = InlineKeyboardMarkup(keyboard_back)
        
                   
    try:
        await context.bot.send_message(
            chat_id=channel_id,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=False
        )

        
    except Exception as e:
        logging.error(f"Errore durante la modifica del messaggio: {e}")
        raise Exception("Il bot non è un admin del canale") 
        
        
                