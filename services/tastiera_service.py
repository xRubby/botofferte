from sqlalchemy.orm import Session

from models.tastiera import Tastiera
from repositories.tastiera_repository import TastieraRepository


class TastieraService:

    def __init__(self, session: Session):
        self.session = session
        self.tastiera_repository = TastieraRepository(session)


    def ottieni_tastiera_in_uso(self, canale_id: str) -> Tastiera | None:
        return self.tastiera_repository.get_in_uso(canale_id)