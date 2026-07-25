from datetime import datetime, timedelta
from io import BytesIO
import re
import traceback

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions, Update, error
from telegram.ext import ContextTypes

from APIs.bitly_api import shorten_url
from DTO.ProductConfig import ProductConfig
from DTO.TextConfig import TextConfig
from database.session import SessionLocal
from models.canale import Canale
from models.pubblica import Pubblica
from scraper.amazon_scraper import scraping_product

from services.canale_service import CanaleService
from services.gestisce_service import GestisceService
from services.layout_immagine_service import LayoutImmagineService
from services.layout_service import LayoutService
from services.prodotto_service import ProdottoService

from models.prodotto import Prodotto

from services.pubblica_service import PubblicaService
from services.tastiera_service import TastieraService
from utils.amazon_utils import extract_asin_from_url, is_future_date, search_warehouse_seller_id_from_link
from utils.expand_link import expand_url

from dotenv import load_dotenv
import os

from sqlalchemy.orm import Session

from utils.formattazione_data import converti_data_preordine_da_db, converti_data_preordine_per_db

load_dotenv()
ASSOCIATE_TAG = os.getenv('ASSOCIATE_TAG')

TEXT_ERRORE_VALORE= ("❌ <b>Errore nell'elaborazione del prodotto</b>\n\n"
            "⚠️ Il link o i dati forniti non sono validi.\n"
            "Controlla il contenuto e riprova.")

TEXT_ERRORE_GENERICO = (
            "❌ <b>Errore imprevisto</b>\n\n"
            "Si è verificato un problema durante l'elaborazione del prodotto.\n"
            "Riprova più tardi."
        )

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
        "spedito_Amazon": prodotto.spedito_amazon,
        "link": prodotto.link,
        "img_url": prodotto.img_url,
        "brand": prodotto.brand,
        "data_preordine": converti_data_preordine_da_db(prodotto.data_preordine),
        "isWarehouse": prodotto.is_warehouse,
        "condizione": prodotto.condizione,
        "condizione_commento": prodotto.condizione_descrizione,
        "preorder": prodotto.preorder,
        "isPrime": prodotto.is_prime,
        "offertaexcl": prodotto.offertaesclusiva
    }

def creaDizionarioProdotto(risultato: dict, tag: str = None) -> dict | None:
    if (risultato):
        prodotto_dict = {
            "ASIN": risultato["ASIN"],
            "titolo": risultato["titolo"],
            "prezzo": risultato["prezzo"],
            "old_prezzo": risultato["old_prezzo"],
            "valuta": risultato["valuta"],
            "sconto": risultato["sconto"],
            "venditore": risultato["venditore"],
            "spedito_Amazon": risultato["spedito_Amazon"],
            "link": risultato["link"],
            "img_url": risultato["img_url"],
            "brand": risultato["brand"],
            "data_preordine": risultato["data_preordine"],
            "isWarehouse": risultato["isWarehouse"],
            "condizione": risultato["condizione"],
            "condizione_commento": risultato["condizione_descrizione"],
            "preorder": bool(risultato["preordine"]),
            "isPrime": bool(risultato["spedito_Amazon"]),
            "offertaexcl": bool(risultato["offertaesclusiva"])
            }
        
        if tag:
            prodotto_dict["link"]+= f"?tag={tag}"
        
        return prodotto_dict
    
    return None

def venduto_e_spedito(venditore: str, spedito_Amazon: bool, canale: Canale = None) -> str:
        if canale:
            if("Amazon" in venditore and spedito_Amazon):
                return canale.amazon_tag if canale.amazon_tag else ""
            elif("Amazon" not in venditore and spedito_Amazon):
                return canale.venditoreamazon_tag.replace("{venditore}", venditore) if canale.venditoreamazon_tag else f""
            return canale.venditore_tag.replace("{venditore}", venditore)  if canale.venditore_tag else f""
        else:
            if("Amazon" in venditore and spedito_Amazon):
                return "Venduto e spedito da Amazon"
            elif("Amazon" not in venditore and spedito_Amazon):
                return f"Venduto da {venditore} e spedito da Amazon"
            return f"Venduto e spedito da {venditore}"

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

async def check_aggiornamento_prodotto(asin: str, prodotto: Prodotto, session: Session) -> dict | None:
    if datetime.now() > prodotto.last_check + timedelta(hours=1):
        risultato = await scraping_product(asin)
        info_prodotto = creaDizionarioProdotto(risultato)

        try:
            if info_prodotto and (prodotto.prezzo != info_prodotto["prezzo"]):
                prodotto.asin = info_prodotto["ASIN"]
                prodotto.prezzo = info_prodotto["prezzo"]
                prodotto.old_prezzo = info_prodotto["old_prezzo"]
                prodotto.valuta = info_prodotto["valuta"]
                prodotto.sconto = info_prodotto["sconto"]
                prodotto.venditore = info_prodotto["venditore"]
                prodotto.img_url = info_prodotto["img_url"]
                prodotto.spedito_amazon = info_prodotto["spedito_Amazon"]
                prodotto.offertaesclusiva = info_prodotto.get("offertaesclusiva", None)
                prodotto.last_check = datetime.now()
                prodotto.preorder=bool(info_prodotto["preorder"]),
                prodotto.data_preordine=info_prodotto["data_preordine"],

            elif info_prodotto:
                prodotto.last_check = datetime.now()

            session.commit()

        except Exception:
            session.rollback()
            traceback.print_exc()
            raise

        return info_prodotto

    return None

async def get_prodotto_dizionario(asin: str) -> dict | None:

    with SessionLocal() as session:
        prodotto_service = ProdottoService(session)

        prodotto = prodotto_service.ottieni_prodotto(asin)

        if not prodotto:
            risultato = await scraping_product(asin)
            info_prodotto = creaDizionarioProdotto(risultato)

            prodotto = Prodotto(
                asin=info_prodotto["ASIN"],
                titolo=info_prodotto["titolo"],
                prezzo=info_prodotto["prezzo"],
                old_prezzo=info_prodotto["old_prezzo"],
                valuta=info_prodotto["valuta"],
                sconto=info_prodotto["sconto"],
                venditore=info_prodotto["venditore"],
                spedito_amazon=info_prodotto["spedito_Amazon"],
                link=info_prodotto["link"],
                img_url=info_prodotto["img_url"],
                brand=info_prodotto["brand"],
                preorder=bool(info_prodotto["preorder"]),
                data_preordine=converti_data_preordine_per_db(info_prodotto["data_preordine"]),
                is_prime=bool(info_prodotto["isPrime"]),
                is_warehouse=info_prodotto["isWarehouse"],
                condizione=info_prodotto["condizione"],
                condizione_descrizione=info_prodotto["condizione_commento"],
                offertaesclusiva=info_prodotto["offertaexcl"]
            )

            try:
                prodotto_service.aggiungi_prodotto(prodotto)
                session.commit()
            except Exception:
                session.rollback()
                traceback.print_exc()
                raise

            return info_prodotto

        info_prodotto = await check_aggiornamento_prodotto(asin, prodotto, session)
        if info_prodotto:
            return info_prodotto

    
    return prodotto_to_dict(prodotto)

async def extract_asin(keyword: str):
    expanded_url = await expand_url(keyword)
    asin = extract_asin_from_url(expanded_url)

    if not asin:
        raise ValueError
    
    return asin


async def search_and_send_offer(update: Update, ctx: ContextTypes.DEFAULT_TYPE, keyword: str):
    message_id = ctx.user_data.pop("msg_id", None)

    if not message_id:
        raise ValueError("ID del messaggio non trovato")

    if not keyword:
        raise ValueError("Errore nella keyword mandata")
    
    try:
        asin = await extract_asin(keyword)
    except ValueError as ve:
        raise ValueError("ASIN non trovato") from ve

    try:
        info_prodotto = await get_prodotto_dizionario(asin)
        
    except Exception:
        raise ValueError("Errore nella ricerca del prodotto")

    if not info_prodotto:
        raise ValueError("Errore nella ricerca del prodotto. Prodotto non trovato.")
    
    info_prodotto["link"]+= f"?tag={ASSOCIATE_TAG}"
    info_prodotto["link_short"] = await shorten_url(info_prodotto["link"])
    info_prodotto["spedito"] = venduto_e_spedito(info_prodotto["venditore"], info_prodotto["spedito_Amazon"])
    info_prodotto["prime"], info_prodotto["preorder"] = get_prime_preorder_tags(info_prodotto)
    info_prodotto["prezzo"] = str(info_prodotto["prezzo"]).replace(".", ",")
    info_prodotto["old_prezzo"] = str(info_prodotto["old_prezzo"]).replace(".", ",")

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

def get_prime_preorder_tags(info_prodotto: dict, canale: Canale = None):
    if canale:
        prime = canale.prime_tag if info_prodotto["isPrime"] else ""
        preorder = canale.preorder_tag if info_prodotto["preorder"] else ""
    else:
        prime = "Spedizione gratuita e veloce con <b><a href='https://amzn.to/4eFvUvQ'>Amazon Prime</a></b>" if info_prodotto["isPrime"] else ""
        preorder = "Preordine" if info_prodotto["preorder"] else ""

    return prime, preorder


TEMPLATE_MESSAGE = (
    "📦 <b>{titolo}</b>\n"
    "💲 <i>Prezzo vecchio:</i> {old_prezzo}{valuta}\n"
    "💰 <i>Prezzo nuovo:</i> <b>{prezzo}{valuta}</b>\n"
    "📉 <i>Sconto:</i> {sconto}%\n\n"
    "🚚 {spedito}\n\n"
    "🔗 <b>Scopri l'offerta:</b> <a href=\"{link}\">Clicca qui!</a>"
)

async def update_step(context, chat_id, message_id, text, reply_markup = None):
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def search_offer(user_id, ctx: ContextTypes.DEFAULT_TYPE, keyword: str, chat_id: int, msg_id: int): 
    channel_id = ctx.user_data.get("channel_id", None)

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Indietro", callback_data=f"channeloffers_info_{channel_id}")]
    ])

    if not channel_id:
        await update_step(ctx, chat_id, msg_id, TEXT_ERRORE_GENERICO, reply_markup)

        raise ValueError("Errore nel ritrovamento dell'id del canale")

    if not keyword:
        await update_step(ctx, chat_id, msg_id, TEXT_ERRORE_VALORE, reply_markup)

        raise ValueError("Errore nella keyword mandata")
    
    try:
        asin = await extract_asin(keyword)
    except ValueError as ve:
        await update_step(ctx, chat_id, msg_id, TEXT_ERRORE_VALORE, reply_markup)

        raise ValueError("ASIN non trovato") from ve
    
    info_prodotto = await get_prodotto_dizionario(asin)

    if not info_prodotto:
        await update_step(ctx, chat_id, msg_id, TEXT_ERRORE_VALORE, reply_markup)

        raise ValueError("Errore nella ricerca del prodotto")
    
    await update_step(ctx, chat_id, msg_id, "📦 <b>Prodotto trovato</b>\n\nSto elaborando le informazioni del prodotto.")


    with SessionLocal() as session:
        gestisce_service = GestisceService(session)
        canale_service = CanaleService(session)
        layout_service = LayoutService(session)
        layout_immagine_service = LayoutImmagineService(session)

        gestisce = gestisce_service.ottieni_gestione(user_id, channel_id)
        canale = canale_service.ottieni_canale(channel_id)
        layout_in_uso = layout_service.ottieni_layout_in_uso(channel_id)
        layout_img = layout_immagine_service.ottieni_layout_immagine_in_uso(channel_id)

    if gestisce and gestisce.id_affiliato:
        info_prodotto["link"]+= f"?tag={gestisce.id_affiliato}"
    else:
        if canale and canale.id_affiliato:
            info_prodotto["link"]+= f"?tag={canale.id_affiliato}"

    info_prodotto["link_short"] = await shorten_url(info_prodotto["link"])

    layout_messaggio = layout_in_uso.messaggio if layout_in_uso else TEMPLATE_MESSAGE

    info_prodotto["spedito"] = venduto_e_spedito(info_prodotto["venditore"], info_prodotto["spedito_Amazon"], canale)

    info_prodotto["prime"], info_prodotto["preorder"] = get_prime_preorder_tags(info_prodotto, canale)

    info_prodotto["offertaexcl"] = canale.offertaexcl_tag if bool(info_prodotto["offertaexcl"]) else None

    info_prodotto["prezzo"] = str(info_prodotto["prezzo"]).replace(".", ",")
    
    info_prodotto["old_prezzo"] = str(info_prodotto["old_prezzo"]).replace(".", ",")

    message = processa_messaggio(layout_messaggio, info_prodotto)

    foto = None

    if layout_img:
        await update_step(ctx, chat_id, msg_id, "🖼️ <b>Elaborazione immagine</b>\n\nSto elaborando l’immagine del prodotto.")
        from utils.image_composer import componi_immagine
        try:
            prodotto_img = ProductConfig(info_prodotto["img_url"], layout_img.prod_x, layout_img.prod_y, layout_img.prod_w_pct, layout_img.prod_h_pct)
            prezzo_img = TextConfig(str(info_prodotto["prezzo"]) + info_prodotto["valuta"], layout_img.prezzo_x, layout_img.prezzo_y, layout_img.prezzo_w_pct, layout_img.prezzo_h_pct, layout_img.prezzo_active)
            prezzo_old_img = None
            sconto_img = None

            if(info_prodotto["prezzo"] < info_prodotto["old_prezzo"]):
                prezzo_old_img = TextConfig(str(info_prodotto["old_prezzo"]) + info_prodotto["valuta"], layout_img.prezzo_old_x, layout_img.prezzo_old_y, layout_img.prezzo_old_w_pct, layout_img.prezzo_old_h_pct, layout_img.prezzo_old_active)
                sconto_img = TextConfig("-" + str(round(info_prodotto["sconto"]))+"%", layout_img.sconto_x, layout_img.sconto_y, layout_img.sconto_w_pct, layout_img.sconto_h_pct, layout_img.sconto_active)
            foto = componi_immagine(layout_img.template_img, prodotto_img, prezzo_img, prezzo_old_img, sconto_img)
        except Exception:
            foto = None

    with SessionLocal() as session:
        pubblica_service = PubblicaService(session)

        pubblicazione = Pubblica(
            id_canale = channel_id,
            asin_prodotti = info_prodotto["ASIN"],
            messaggio = message,
            link = info_prodotto["link"],
            link_short = info_prodotto["link_short"],
            img_bytes = foto         
        )
        try:
            pubblica_service.aggiungi_link(pubblicazione)

            session.commit()
        except Exception:
            session.rollback()
            raise ValueError("Errore nell'elaborazione dell'immagine")
    await update_step(ctx, chat_id, msg_id, "✅ <b>Operazione completata</b>\n\n🔗 Il link è stato aggiunto correttamente nella lista.", reply_markup)

def parse_keyboard(text):
    result = []

    for line in text.strip().splitlines():

        parts = line.split("||")

        row = []

        for part in parts:
            match = re.findall(r'(.*?)\s*-\s*(\{.*?\}|.+)', part)

            for msg, cmd in match:
                msg = msg.strip()
                cmd = cmd.strip()

                if cmd.startswith("{") and cmd.endswith("}"):
                    cmd = cmd[1:-1].strip()

                row.append({
                    "messaggio": msg,
                    "comando": cmd
                })

        if row:
            result.append(row)

    return result

def normalize_url(url: str) -> str:
    url = url.strip()

    if url.startswith("http://") or url.startswith("https://"):
        return url

    return "https://" + url

def generate_keyboard(text, link: Pubblica):
    parsed = parse_keyboard(text)
    keyboard = []

    for row in parsed:

        buttons_data = row if isinstance(row, list) else [row]
        row_buttons = []

        for btn in buttons_data:
            msg = btn["messaggio"]
            cmd = btn["comando"]

            if cmd == "url" and link.link:
                row_buttons.append(
                    InlineKeyboardButton(
                        text=msg,
                        url=link.link
                    )
                )
            elif cmd: 
                row_buttons.append(
                    InlineKeyboardButton(
                        text=msg,
                        url=normalize_url(cmd)
                    )
                )

        keyboard.append(row_buttons)

    return InlineKeyboardMarkup(keyboard)
    
async def publish_offer(update: Update, context: ContextTypes.DEFAULT_TYPE, link: Pubblica):

    if link.is_pubblicato:
        raise Exception("L'offerta è già stata pubblicata sul canale")

    with SessionLocal() as session:
        prodotto_service = ProdottoService(session)
        tastiera_service = TastieraService(session)

        prodotto = prodotto_service.ottieni_prodotto(link.asin_prodotti)
        tastiera = tastiera_service.ottieni_tastiera_in_uso(link.id_canale)

    if link.img_bytes:
        foto = BytesIO(link.img_bytes)
    else:
        foto = prodotto.img_url

    reply_markup = None
    if tastiera:
        reply_markup = generate_keyboard(tastiera.messaggio, link)

    try:
        await context.bot.send_photo(
            chat_id=link.id_canale,
            photo=foto,
            caption=link.messaggio,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    except error.BadRequest:
        raise error.BadRequest("Il bot non ha i permessi di amministratore nel canale")
    except Exception as e:
        raise Exception("Il bot non è un admin del canale")