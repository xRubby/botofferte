from sqlalchemy.orm import Session

from models.gestisce import Gestisce
from repositories.gestisce_repository import GestisceRepository


class GestisceService:

    def __init__(self, session: Session):
        self.session = session
        self.gestisce_repository = GestisceRepository(session)

    def aggiungi_gestione(self, gestione: Gestisce) -> Gestisce:

        return self.gestisce_repository.create(gestione)

    def ottieni_gestione(self, telegram_id: int, canale_id: str) -> Gestisce | None:

        return self.gestisce_repository.get(telegram_id, canale_id)