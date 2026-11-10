import asyncio
from datetime import datetime, timedelta
from telegram.ext import ContextTypes

from sqlalchemy import select

from database.session import SessionLocal
from models.canale import Canale
from services.canale_service import CanaleService
from services.pubblica_service import PubblicaService
from telegram_bot.functions.send_message import publish_offer

sem = asyncio.Semaphore(5)

async def autopost_tick(context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
        ids = [c.canale_id for c in CanaleService(session).ottieni_canali_autopost_scaduti()]
    await asyncio.gather(*(_autopost_canale(context, cid) for cid in ids),
                         return_exceptions=True)

async def _autopost_canale(context, canale_id: str):
    async with sem:
        with SessionLocal() as session:
            canale = session.scalars(
                select(Canale).where(Canale.canale_id == canale_id)
                .with_for_update(skip_locked=True)
            ).first()
            if not canale or not canale.autopost_attivo:
                return

            # 1) sposto SUBITO la prossima esecuzione: se qualcosa fallisce non martello il canale
            canale.autopost_prossimo_invio = datetime.now() + timedelta(minutes=canale.autopost_intervallo_min)
            session.commit()

            link = PubblicaService(session).ottieni_prossimo_da_pubblicare(canale_id)
            if not link:
                return  # coda vuota

            try:
                await publish_offer(None, context, link)   # `update` in publish_offer non viene usato
                PubblicaService(session).segna_pubblicato(link)
                session.commit()
            except Exception:
                session.rollback()
                