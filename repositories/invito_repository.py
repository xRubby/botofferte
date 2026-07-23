from sqlalchemy import select
from sqlalchemy.orm import Session

from models.invito import Invito


class InvitoRepository:

    def __init__(self, session: Session):
        self.session = session


    def get(self, token: str) -> Invito | None:

        stmt = select(Invito).where(Invito.token == token)

        return self.session.scalars(stmt).first()


    def get_by_canale(self, canale_id: str) -> Invito | None:

        stmt = select(Invito).where(Invito.canale_id == str(canale_id))

        return self.session.scalars(stmt).first()


    def get_all(self) -> list[Invito]:

        stmt = select(Invito)

        return list(self.session.scalars(stmt))


    def create(self, invito: Invito) -> Invito:

        self.session.add(invito)

        return invito


    def delete(self, invito: Invito) -> None:

        self.session.delete(invito)