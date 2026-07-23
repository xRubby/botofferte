from models import Utente
from repositories.utente_repository import UtenteRepository
from sqlalchemy.orm import Session


class UtenteService:

    def __init__(self, session: Session):
        self.session = session
        self.utente_repository = UtenteRepository(session)


    def crea_utente(self, telegram_id: int, nome: str, is_admin: bool = False) -> Utente:

            utente = Utente(
                telegram_id=telegram_id,
                nome=nome,
                is_admin=is_admin
            )

            self.utente_repository.create(utente)

            return utente

    def ottieni_utente(self, telegram_id: int) -> Utente | None:

        return self.utente_repository.get_by_telegram_id(telegram_id)