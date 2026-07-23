from sqlalchemy import select
from sqlalchemy.orm import Session

from models.tastiera import Tastiera


class TastieraRepository:

    def __init__(self, session: Session):
        self.session = session


    def get(self, tastiera_id: int) -> Tastiera | None:

        stmt = select(Tastiera).where(Tastiera.tastiera_id == tastiera_id)

        return self.session.scalars(stmt).first()


    def get_all(self) -> list[Tastiera]:

        stmt = select(Tastiera)

        return list(self.session.scalars(stmt))


    def get_in_uso(self, canale_id: str) -> Tastiera | None:

        stmt = (select(Tastiera).where(Tastiera.canale_id == canale_id, Tastiera.in_uso.is_(True)))

        return self.session.scalars(stmt).first()


    def create(self, tastiera: Tastiera) -> Tastiera:

        self.session.add(tastiera)

        return tastiera


    def delete(self, tastiera: Tastiera) -> None:

        self.session.delete(tastiera)