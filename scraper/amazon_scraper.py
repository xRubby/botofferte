import re
import requests
from bs4 import BeautifulSoup

def format_price(price):
    return "{:.2f}".format(price).replace('.', ',')

def parse_price(price_str: str) -> float:
    return float(
        price_str.replace("€", "").replace(".", "").replace(",", ".").strip()
    )


def scraping_product(asin: str) -> dict | None:
    url = f"https://www.amazon.it/dp/{asin}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "it-IT,it;q=0.9",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # ── Titolo ────────────────────────────────────────────────
        title_span = soup.find("span", id="productTitle")
        if not title_span:
            raise RuntimeError("Titolo non trovato")
        title = title_span.get_text(strip=True)

        # ── Prezzo attuale ────────────────────────────────────────
        symbol   = soup.find("span", class_="a-price-symbol")
        whole    = soup.find("span", class_="a-price-whole")
        fraction = soup.find("span", class_="a-price-fraction")
        if not (symbol and whole and fraction):
            raise RuntimeError("Prezzo non trovato")

        currency  = symbol.get_text(strip=True)
        price_str = whole.text + fraction.text
        price_val = parse_price(price_str)

        # ── Prezzo consigliato ────────────────────────────────────
        old_price_val = price_val
        price_container = soup.find(
            "div", class_="a-section a-spacing-small aok-align-center"
        )
        if price_container:
            offscreen = price_container.find("span", class_="a-offscreen")
            if offscreen:
                old_price_str = offscreen.get_text(strip=True).replace("€", "")
                parsed = parse_price(old_price_str)
                if parsed > price_val:
                    old_price_val = parsed

        discount = (
            round((old_price_val - price_val) / old_price_val * 100)
            if old_price_val > price_val else 0
        )

        # ── Venditore ─────────────────────────────────────────────
        venditore = ""
        venditore_div = soup.find(
            "div",
            id="merchantInfoFeature_feature_div",
            attrs={"data-feature-name": "merchantInfoFeature"},
        )
        if venditore_div:
            span = (
                venditore_div.find("span", class_="a-size-small a-color-tertiary offer-display-feature-text-message")
                or venditore_div.find("span", class_="a-size-small offer-display-feature-text-message")
            )
            venditore = span.text.strip() if span else ""

        # ── Spedizione ────────────────────────────────────────────
        spedito        = ""
        spedito_amazon = False
        spedito_div    = soup.find("div", id="fulfillerInfoFeature_feature_div")
        if spedito_div:
            span = (
                spedito_div.find("span", class_="a-size-small a-color-tertiary offer-display-feature-text-message")
                or spedito_div.find("span", class_="a-size-small offer-display-feature-text-message")
            )
            if span:
                spedito        = span.text.strip()
                spedito_amazon = "Amazon" in spedito

        if not spedito and venditore:
            spedito = venditore
                
        if "Amazon" in venditore:
            spedito_amazon = True

        # ── Immagine ──────────────────────────────────────────────
        img_tag = soup.find("img", id="landingImage")
        if not img_tag:
            raise RuntimeError("Immagine non trovata")
        img_link = img_tag.get("data-old-hires", "")

        # ── Brand ─────────────────────────────────────────────────
        brand_tag = soup.find("a", id="bylineInfo")
        brand = brand_tag.get_text(strip=True).split()[-1] if brand_tag else ""

        # ── Preordine ─────────────────────────────────────────────
        preorder       = False
        data_preordine = None
        preorder_div   = soup.find("div", id="availability")
        if preorder_div:
            span = preorder_div.find("span", class_="a-size-medium a-color-success")
            if span:
                testo = span.get_text(strip=True)
                match = re.search(r"\b\d{1,2}\s+[a-zA-Zà-ù]+\s+\d{4}\b", testo)
                if match:
                    preorder       = True
                    data_preordine = match.group()

        # ── Offerta esclusiva ─────────────────────────────────────
        offerta_esclusiva = ""
        badge = soup.find("span", id="dealBadgeSupportingText")
        if badge and "aok-hidden" not in badge.get("class", []):
            offerta_esclusiva = badge.text.strip()

        return {
            "ASIN":                   asin,
            "titolo":                 title,
            "prezzo":                 format_price(price_val),
            "old_prezzo":             format_price(old_price_val),
            "valuta":                 currency,
            "sconto":                 discount,
            "venditore":              venditore,
            "spedito_Amazon":         spedito_amazon,
            "link":                   url,
            "img_url":                img_link,
            "brand":                  brand,
            "preordine":              preorder,
            "data_preordine":         data_preordine,
            "isPrime":                spedito_amazon,
            "isWarehouse":            False,
            "condizione":             "",
            "condizione_descrizione": "",
            "offertaesclusiva":       offerta_esclusiva,
        }

    except requests.exceptions.RequestException as e:
        print(f"Errore di rete per ASIN {asin}: {e}")
        return None
    except RuntimeError as e:
        print(f"Errore di parsing per ASIN {asin}: {e}")
        return None


if __name__ == "__main__":
    print(scraping_product("B095SP2CH7"))