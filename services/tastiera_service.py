from sqlalchemy.orm import Session

from models.tastiera import Tastiera
from repositories.tastiera_repository import TastieraRepository


class TastieraService:

    def __init__(self, session: Session):
        self.session = session
        self.tastiera_repository = TastieraRepository(session)


    def ottieni_tastiera_in_uso(self, canale_id: str) -> Tastiera | None:
        return self.tastiera_repository.get_in_uso(canale_id)

    def crea_tastiera(self, tastiera: Tastiera) -> Tastiera:

        return self.tastiera_repository.create(tastiera)

    def rimuovi_tastiera(self, tastiera: Tastiera) -> None:

        self.tastiera_repository.delete(tastiera)

    def ottieni_tastiera(self, tastiera_id: int) -> Tastiera:

        return self.tastiera_repository.get(tastiera_id)

    def ottieni_tastiere_canale(self, canale_id: str) -> list[Tastiera]:

        return self.tastiera_repository.get_by_channel(canale_id)