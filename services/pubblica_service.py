from datetime import datetime

from repositories.pubblica_repository import PubblicaRepository


class PubblicaService:

    def __init__(self, pubblica_repository: PubblicaRepository):
        self.pubblica_repository = pubblica_repository

    def segna_pubblicato(self, id: int) -> bool:

        pubblicazione = self.repository.get(id)

        if not pubblicazione:
            return False


        pubblicazione.is_pubblicato = True
        pubblicazione.data_pubblicazione = datetime.now()


        self.session.commit()

        return True