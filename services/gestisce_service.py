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

    def ottieni_lista_membri_canale(self, canale_id: str, limite: int, offset: int) -> list[Gestisce] | None:

        return self.gestisce_repository.get_member_list(canale_id, limite, offset)

    def conta_membri_canale(self, canale_id: str) -> int:

        return self.gestisce_repository.count_members(canale_id)

    def rimuovi_gestione(self, gestione: Gestisce) -> None:

        return self.gestisce_repository.delete(gestione)