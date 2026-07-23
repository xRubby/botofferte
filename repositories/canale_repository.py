from sqlalchemy import select
from sqlalchemy.orm import Session

from models.canale import Canale
from models.gestisce import Gestisce


class CanaleRepository:

    def __init__(self, session: Session):
        self.session = session


    def get_by_id(self, canale_id: str) -> Canale | None:

        stmt = select(Canale).where(Canale.canale_id == canale_id)

        return self.session.scalars(stmt).first()


    def get_all(self) -> list[Canale]:

        stmt = select(Canale)

        return list(self.session.scalars(stmt))


    def get_by_codice_licenza(self, codice_licenza: str) -> Canale | None:

        stmt = select(Canale).where(Canale.codice_licenza == codice_licenza)

        return self.session.scalars(stmt).first()


    def get_user_channels(self, telegram_id: int) -> list[Canale]:

        stmt = (select(Canale).join(Gestisce).where(Gestisce.telegram_id == telegram_id))

        return list(self.session.scalars(stmt))


    def create(self, canale: Canale) -> Canale:

        self.session.add(canale)

        return canale


    def delete(self, canale: Canale) -> None:

        self.session.delete(canale)