from sqlalchemy.orm import Session

from models.canale import Canale
from repositories.canale_repository import CanaleRepository


class CanaleService:

    def __init__(self, session: Session):
        self.session = session
        self.canale_repository = CanaleRepository(session)


    def aggiungi_canale(self, canale: Canale) -> Canale:

        return self.canale_repository.create(canale)

    def ottieni_canale(self, canale_id: str) -> Canale | None:

        return self.canale_repository.get_by_id(canale_id)

    def ottieni_canale_utente(self, telegram_id: int) -> list[Canale] | None:

        return self.canale_repository.get_user_channels(telegram_id)

    def rimuovi_canale(self, canale: Canale) -> None:

        return self.canale_repository.delete(canale)