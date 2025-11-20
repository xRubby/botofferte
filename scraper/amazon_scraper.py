import requests
from bs4 import BeautifulSoup

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.amazon_utils import *

def parse_price(price_str):
    return float(price_str.replace("€", "").replace(".", "").replace(",", "."))


def scraping_product(asin):
    url = f"https://www.amazon.it/dp/{asin}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "it-IT,it;q=0.9",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        print("Scraping URL")

        # Ricerca titolo
        title_span = soup.find("span", id="productTitle")
        if not title_span:
            raise RuntimeError("Errore titolo")
        title = title_span.get_text(strip=True)


        # Ricerca prezzo prodotto
        symbol = soup.find("span", class_="a-price-symbol")
        whole = soup.find("span", class_="a-price-whole")
        fraction = soup.find("span", class_="a-price-fraction")
        if not (whole and fraction and symbol):
            raise RuntimeError("Errore prezzo")

        price_str = whole.text + fraction.text
        currency = symbol.get_text(strip=True)

        # Ricerca prezzo consigliato prodotto
        old_price_str = price_str
        price_container = soup.find("div", class_="a-section a-spacing-small aok-align-center")
        if price_container:
            offscreen = price_container.find("span", class_="a-offscreen")
            if offscreen:
                old_price_str = offscreen.get_text(strip=True)
                old_price_str.replace("€","")


        # Converto i prezzi in float
        price_val = parse_price(price_str)
        old_price_val = parse_price(old_price_str)

        if old_price_val < price_val:
            old_price_val = price_val 

        # Calcolo sconto (se presente)
        discount_percentage = (
            round((old_price_val - price_val) / old_price_val * 100)
            if old_price_val > price_val else 0
        )

        # Ricerca venditore del prodotto
        venditore_div = soup.find("div", id="merchantInfoFeature_feature_div", attrs={"data-feature-name": "merchantInfoFeature","class": "celwidget"})

        if venditore_div:
            venditore_a = venditore_div.find("span", class_="a-size-small a-color-tertiary offer-display-feature-text-message")
            if venditore_a is None:
                venditore_a = venditore_div.find("span", class_="a-size-small offer-display-feature-text-message")

            if not venditore_a:
                raise RuntimeError("Errore venditore")
            
            venditore = venditore_a.text.strip()
        
        # Ricerca spedizione del prodotto
        spedito_div = soup.find("div", id="fulfillerInfoFeature_feature_div")
        if spedito_div:
            spedito_a = spedito_div.find("span", class_="a-size-small a-color-tertiary offer-display-feature-text-message")

            if spedito_a is None:
                spedito_a = spedito_div.find("span", class_="a-size-small offer-display-feature-text-message")

            if not spedito_a:
                raise RuntimeError("Errore spedizione")
            
            spedito = spedito_a.text.strip()

            spedito_Amazon = False
            if spedito in "Amazon":
                spedito_Amazon = True
            
        # Ricerca img
        img_tag = soup.find("img", id="landingImage")
        if img_tag:
            img_link = img_tag.get("data-old-hires")
        else:
            raise RuntimeError("Errore immagine")

        
        # Ricerca il brand del prodotto
        brand_tag = soup.find("a", id="bylineInfo")
        if brand_tag:
            testo_brand = brand_tag.get_text(strip=True)
            brand = testo_brand.split()[-1] 
        else:
            brand = ""

        # Ricerca se il prodotto è in preordine
        preorder_div = soup.find("div", id="availability")
        try:
            if preorder_div:
                preorder = True
                data_preordine_str = preorder_div.find("span", class_="a-size-medium a-color-success").get_text(strip=True)

                pattern = r"\b\d{1,2}\s+[a-zA-Zà-ù]+\s+\d{4}\b"

                data_preordine = re.search(pattern, data_preordine_str).group()
            else:
                preorder = False
                data_preordine = None
        except:
            preorder = False
            data_preordine = None

        # Verifico se la spedizione è con Amazon Prime
        prime = False

        if spedito_Amazon:
            prime = True

        is_warehouse = False
        cond = ""
        cond_comm = ""

        offertaesclusiva = ""
        badge_offerta = soup.find("span", id="dealBadgeSupportingText")
        if badge_offerta and "aok-hidden" not in badge_offerta.get("class", []):
            offertaesclusiva = badge_offerta.text.strip()

        offerta = {
            'ASIN': asin,
            'titolo': title,
            'prezzo': format_price(price_val),
            'old_prezzo': format_price(old_price_val),
            'valuta': currency,
            'sconto': discount_percentage,
            'venditore': venditore,
            'spedito_Amazon': spedito_Amazon,
            'link': url,
            'img_url': img_link,
            'brand': brand,
            'preordine': preorder,
            'data_preordine': data_preordine,
            'isPrime': prime,
            'isWarehouse': is_warehouse,
            'condizione': cond,
            'condizione_descrizione': cond_comm,
            'offertaesclusiva': offertaesclusiva
            
            
        }
        return offerta

    except requests.exceptions.RequestException as e:
        print(f"Errore durante il recupero del prezzo per {asin}: {e}")
        return None
    
if __name__ == "__main__":
    offerta = scraping_product("B0F2NF1MYG")
    print(offerta)