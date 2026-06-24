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


class ScraperLimiter:
    def __init__(self, limit=3):
        self.semaphore = asyncio.Semaphore(limit)

limiter = ScraperLimiter(3)
_client: httpx.AsyncClient | None = None
_client_lock = asyncio.Lock()


async def get_client() -> httpx.AsyncClient:
    """
    Client singleton MA creato in modo thread-safe e senza warm-up globale bloccante.
    """
    global _client

    if _client is None:
        async with _client_lock:
            if _client is None:
                _client = httpx.AsyncClient(
                    timeout=15,
                    follow_redirects=True,
                    limits=httpx.Limits(
                        max_connections=10,
                        max_keepalive_connections=5
                    )
                )

    return _client

async def warmup_client(client: httpx.AsyncClient):
    try:
        await client.get("https://www.amazon.it")
    except Exception:
        pass


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
    await warmup_client(client)

    async with limiter.semaphore:
        try:
            response = await client.get(url, headers=get_headers())
            response.raise_for_status()
            await asyncio.sleep(random.uniform(0.3, 1.2))

            if "captcha" in response.url.path.lower() or "Type the characters" in response.text:
                global _client
                if _client:
                    await _client.aclose()
                _client = None
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # ── TITLO ──
            title_span = soup.find("span", id="productTitle")
            if not title_span:
                return None
            title = title_span.get_text(strip=True)

            # ── PREZZO ──
            symbol = soup.find("span", class_="a-price-symbol")
            whole = soup.find("span", class_="a-price-whole")
            fraction = soup.find("span", class_="a-price-fraction")

            if not (symbol and whole and fraction):
                return None

            currency = symbol.get_text(strip=True)
            price_str = whole.text + fraction.text
            price_val = parse_price(price_str)

            old_price_val = price_val


            #Prende il prezzo consigliato, altrimenti quello più basso negli ultimi 30 giorni
            container = soup.find("div", class_="a-section a-spacing-none aok-align-center")

            if not container:
                container = soup.find("div", class_="a-section a-spacing-small aok-align-center")

            if container:
                offscreen = container.find("span", class_="a-offscreen")
                if offscreen:
                    parsed = parse_price(offscreen.get_text(strip=True))
                    if parsed > price_val:
                        old_price_val = parsed

            discount = round((old_price_val - price_val) / old_price_val * 100) if old_price_val > price_val else 0

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

            if not venditore:
                return None

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

            # ── IMG ──
            img_tag = soup.find("img", id="landingImage")
            if not img_tag:
                return None

            img_link = img_tag.get("data-old-hires", "")

            # ── BRAND ──
            brand_tag = soup.find("a", id="bylineInfo")
            brand = brand_tag.get_text(strip=True).split()[-1] if brand_tag else ""

            # ── PREORDER ──
            preorder = False
            data_preordine = ""

            preorder_div = soup.find("div", id="availability")
            if preorder_div:
                match = re.search(r"\b(\d{1,2}\s+[a-zA-Z]+\s+\d{4})\b", preorder_div.get_text())
                if match:
                    preorder = True
                    data_preordine = match.group()

            # -- OFFERTA ESCLUSIVA --
            offertaesclusiva = False
            offertaesclusiva_span = soup.find("span", id="dealBadgeSupportingText")
            if offertaesclusiva_span:
                offertaesclusiva = True

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
                "offertaesclusiva": offertaesclusiva,
            }

        except httpx.RequestError:
            return None


async def main():
    asins = ["B0F3P3X5P2"]

    results = await asyncio.gather(
        scraping_product(asins[0])
    )

    print(results)

if __name__ == "__main__":
    asyncio.run(main())
