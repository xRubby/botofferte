from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.gestisce import Gestisce


class GestisceRepository:

    def __init__(self, session: Session):
        self.session = session


    def get(self, telegram_id: int, canale_id: str) -> Gestisce | None:

        stmt = (select(Gestisce).where(Gestisce.telegram_id == telegram_id, Gestisce.canale_id == canale_id))

        return self.session.scalars(stmt).first()


    def get_all(self) -> list[Gestisce]:

        stmt = select(Gestisce)

        return list(self.session.scalars(stmt))


    def get_member_list(self, canale_id: str, limit: int, offset: int) -> list[Gestisce]:

        stmt = (select(Gestisce).where(Gestisce.canale_id == canale_id).order_by(Gestisce.telegram_id).limit(limit).offset(offset))

        return list(self.session.scalars(stmt))


    def count_members(self, canale_id: str) -> int:

        stmt = (select(func.count()).select_from(Gestisce).where(Gestisce.canale_id == canale_id))

        return self.session.scalar(stmt) or 0


    def create(self, gestione: Gestisce) -> Gestisce:

        self.session.add(gestione)

        return gestione


    def delete(self, gestione: Gestisce) -> None:

        self.session.delete(gestione)