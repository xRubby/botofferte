from sqlalchemy import select
from sqlalchemy.orm import Session

from models.utente import Utente


class UtenteRepository:

    def __init__(self, session: Session):
        self.session = session


    def get_by_telegram_id(self, telegram_id: int) -> Utente | None:

        stmt = select(Utente).where(Utente.telegram_id == telegram_id)

        return self.session.scalars(stmt).first()


    def get_all(self) -> list[Utente]:

        stmt = select(Utente)

        return list(self.session.scalars(stmt))


    def create(self, utente: Utente) -> Utente:
        
        self.session.add(utente)

        return utente


    def delete(self, utente: Utente) -> None:

        self.session.delete(utente)