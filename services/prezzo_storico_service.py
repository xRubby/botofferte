from models.prezzo_storico import PrezzoStorico
from repositories.prezzo_storico_repository import PrezzoStoricoRepository

from sqlalchemy.orm import Session


class PrezzoStoricoService:

    def __init__(self, session: Session):
        self.session = session
        self.prezzo_storico_repository = PrezzoStoricoRepository(session)

    def ottieni_ultimo_prezzo_storico(self, asin: str) -> PrezzoStorico | None:

        return self.prezzo_storico_repository.get_last_by_asin(asin)
