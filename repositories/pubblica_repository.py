from sqlalchemy import select, func, text
from sqlalchemy.orm import Session

from models.pubblica import Pubblica


class PubblicaRepository:

    def __init__(self, session: Session):
        self.session = session


    def get(self, id: int) -> Pubblica | None:

        stmt = select(Pubblica).where(Pubblica.id == id)

        return self.session.scalars(stmt).first()


    def get_all(self) -> list[Pubblica]:

        stmt = select(Pubblica)

        return list(self.session.scalars(stmt))

    
    def get_channel_non_pubblicati(self, id_canale: str) -> list[Pubblica]:

        stmt = (select(Pubblica).where(Pubblica.id_canale == id_canale, Pubblica.is_pubblicato.is_(False)).order_by(Pubblica.id.asc()))

        return list(self.session.scalars(stmt))


    def get_channel_link_by_id_canale(self, id: int, id_canale: str) -> Pubblica | None:

        stmt = (select(Pubblica).where(Pubblica.id == id, Pubblica.id_canale == id_canale))

        return self.session.scalars(stmt).first()


    def get_ultimo_pubblicato_by_asin(self, id_canale: str, asin: str) -> Pubblica | None:

        stmt = (select(Pubblica).where(Pubblica.id_canale == id_canale, Pubblica.asin_prodotti == asin, Pubblica.is_pubblicato.is_(True))
            .order_by(Pubblica.data_pubblicazione.desc()).limit(1))

        return self.session.scalars(stmt).first()


    def get_pubblicato_ultime_24h(self, id_canale: str, asin: str):

        stmt = (select(Pubblica).where(Pubblica.id_canale == id_canale, Pubblica.asin_prodotti == asin, Pubblica.is_pubblicato.is_(True),
                Pubblica.data_pubblicazione >= func.now() - text("INTERVAL '24 hours'")).limit(1))

        return self.session.scalars(stmt).first()


    def create(self, pubblicazione: Pubblica) -> Pubblica:

        self.session.add(pubblicazione)

        return pubblicazione


    def delete(self, pubblicazione: Pubblica) -> None:

        self.session.delete(pubblicazione)