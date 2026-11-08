# telegram_bot/functions/worker_prezzi.py
import asyncio, logging
from telegram.ext import ContextTypes

from database.session import SessionLocal
from services.prodotto_service import ProdottoService
from scraper.amazon_scraper import scraping_product, human_delay
from services.prodotto_service import ProdottoService
from telegram_bot.functions.send_message import creaDizionarioProdotto

MAX_BLOCCHI = 3
BATCH = 200

async def worker_aggiorna_prezzi(context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
        asins = ProdottoService(session).ottieni_prodotti_da_aggiornare(BATCH)

    blocchi = 0
    for asin in asins:
        try:
            risultato = await scraping_product(asin)
        except Exception:
            blocchi += 1
            logging.warning("Possibile blocco Amazon (%s/%s)", blocchi, MAX_BLOCCHI)
            if blocchi >= MAX_BLOCCHI:
                logging.error("Worker interrotto, riprovo al prossimo giro")
                break
            await asyncio.sleep(60 * blocchi)   # backoff crescente
            continue

        blocchi = 0
        info = creaDizionarioProdotto(risultato)

        with SessionLocal() as session:
            service = ProdottoService(session)
            prodotto = service.ottieni_prodotto(asin)
            try:
                print(f"Aggiorno prezzo {prodotto.titolo}")
                service.aggiorna_prezzo_prodotto(prodotto, info)   # info può essere None
                print(f"Prezzo aggiornato {prodotto.prezzo}")
                session.commit()
            except Exception:
                session.rollback()
                logging.exception("Errore aggiornamento %s", asin)

        await human_delay(3, 8)