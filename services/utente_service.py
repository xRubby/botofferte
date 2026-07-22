from models import Utente
from repositories.utente_repository import UtenteRepository


class UtenteService:

    def __init__(self, utente_repository: UtenteRepository):
        self.utente_repository = utente_repository


    def crea_utente(self, telegram_id: int, nome: str, is_admin: bool = False):

        utente = Utente(
            telegram_id=telegram_id,
            nome=nome,
            is_admin=is_admin
        )

        self.utente_repository.create(utente)

        return utente