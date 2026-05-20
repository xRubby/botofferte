import random
import re
import asyncio
import httpx
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

def get_headers():
    ua = random.choice(USER_AGENTS)
    is_firefox = "Firefox" in ua

    return {
        "User-Agent": ua,
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
            if is_firefox
            else "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
        ),
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


# ─────────────────────────────────────────────
# SESSION ASYNC SINGLETON
# ─────────────────────────────────────────────
_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    global _client

    if _client is None:
        _client = httpx.AsyncClient(
            timeout=15,
            follow_redirects=True,
            headers=get_headers()
        )

        # "warm-up" leggero (non blocca thread)
        try:
            await _client.get("https://www.amazon.it")
            await asyncio.sleep(random.uniform(1.5, 3.5))
        except Exception:
            pass

    return _client


async def human_delay(min_s=2.0, max_s=6.0):
    await asyncio.sleep(random.uniform(min_s, max_s))


def format_price(price):
    return "{:.2f}".format(price).replace(".", ",")


def parse_price(price_str: str) -> float:
    return float(
        price_str.replace("€", "").replace(".", "").replace(",", ".").strip()
    )


# ─────────────────────────────────────────────
# SCRAPING ASYNC
# ─────────────────────────────────────────────
async def scraping_product(asin: str) -> dict | None:
    url = f"https://www.amazon.it/dp/{asin}"
    client = await get_client()

    try:
        await human_delay()

        response = await client.get(url)
        response.raise_for_status()

        # CAPTCHA detection
        if "captcha" in response.url.path.lower() or "Type the characters" in response.text:
            print(f"CAPTCHA rilevato per ASIN {asin}")
            global _client
            _client = None
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # ── Titolo ─────────────────────────────
        title_span = soup.find("span", id="productTitle")
        if not title_span:
            raise RuntimeError("Titolo non trovato")
        title = title_span.get_text(strip=True)

        # ── Prezzo ─────────────────────────────
        symbol = soup.find("span", class_="a-price-symbol")
        whole = soup.find("span", class_="a-price-whole")
        fraction = soup.find("span", class_="a-price-fraction")

        if not (symbol and whole and fraction):
            raise RuntimeError("Prezzo non trovato")

        currency = symbol.get_text(strip=True)
        price_str = whole.text + fraction.text
        price_val = parse_price(price_str)

        # ── Prezzo vecchio ─────────────────────
        old_price_val = price_val
        container = soup.find("div", class_="a-section a-spacing-small aok-align-center")

        if container:
            offscreen = container.find("span", class_="a-offscreen")
            if offscreen:
                parsed = parse_price(offscreen.get_text(strip=True).replace("€", ""))
                if parsed > price_val:
                    old_price_val = parsed

        discount = (
            round((old_price_val - price_val) / old_price_val * 100)
            if old_price_val > price_val else 0
        )

        # ── Venditore ──────────────────────────
        venditore = ""
        venditore_div = soup.find("div", id="merchantInfoFeature_feature_div")

        if venditore_div:
            span = (
                venditore_div.find("span", class_="a-size-small a-color-tertiary offer-display-feature-text-message")
                or venditore_div.find("span", class_="a-size-small offer-display-feature-text-message")
            )
            if span:
                venditore = span.text.strip()

        # ── Spedizione ─────────────────────────
        spedito = ""
        spedito_amazon = False

        spedito_div = soup.find("div", id="fulfillerInfoFeature_feature_div")

        if spedito_div:
            span = (
                spedito_div.find("span", class_="a-size-small a-color-tertiary offer-display-feature-text-message")
                or spedito_div.find("span", class_="a-size-small offer-display-feature-text-message")
            )
            if span:
                spedito = span.text.strip()
                spedito_amazon = "Amazon" in spedito

        if not spedito and venditore:
            spedito = venditore

        if "Amazon" in venditore:
            spedito_amazon = True

        # ── Immagine ───────────────────────────
        img_tag = soup.find("img", id="landingImage")
        if not img_tag:
            raise RuntimeError("Immagine non trovata")

        img_link = img_tag.get("data-old-hires", "")

        # ── Brand ───────────────────────────────
        brand_tag = soup.find("a", id="bylineInfo")
        brand = brand_tag.get_text(strip=True).split()[-1] if brand_tag else ""

        # ── Preordine ───────────────────────────
        preorder = False
        data_preordine = ""

        preorder_div = soup.find("div", id="availability")

        if preorder_div:
            testo = preorder_div.get_text(strip=True)
            match = re.search(r"\b(\d{1,2}\s+[a-zA-Z]+\s+\d{4})\b", testo)

            if match:
                preorder = True
                data_preordine = match.group()

        # ── Offerta ─────────────────────────────
        offerta_esclusiva = ""
        badge = soup.find("span", id="dealBadgeSupportingText")

        if badge and "aok-hidden" not in (badge.get("class") or []):
            offerta_esclusiva = badge.text.strip()

        return {
            "ASIN": asin,
            "titolo": title,
            "prezzo": format_price(price_val),
            "old_prezzo": format_price(old_price_val),
            "valuta": currency,
            "sconto": round(discount),
            "venditore": venditore,
            "spedito_Amazon": spedito_amazon,
            "link": url,
            "img_url": img_link,
            "brand": brand,
            "preordine": preorder,
            "data_preordine": data_preordine,
            "isPrime": spedito_amazon,
            "isWarehouse": False,
            "condizione": "",
            "condizione_descrizione": "",
            "offertaesclusiva": offerta_esclusiva,
        }

    except httpx.RequestError as e:
        print(f"Errore rete ASIN {asin}: {e}")
        return None

    except RuntimeError as e:
        print(f"Errore parsing ASIN {asin}: {e}")
        return None


# ─────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import asyncio

    print(asyncio.run(scraping_product("B0GS6CXWS2")))