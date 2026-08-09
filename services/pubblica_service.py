from datetime import datetime

from models.pubblica import Pubblica
from repositories.pubblica_repository import PubblicaRepository
from sqlalchemy.orm import Session


class PubblicaService:

    def __init__(self, session: Session):
        self.session = session
        self.pubblica_repository = PubblicaRepository(session)

    def segna_pubblicato(self, pubblicazione: Pubblica) -> None:

        if not pubblicazione:
            return

        pubblicazione.is_pubblicato = True
        pubblicazione.data_pubblicazione = datetime.now().replace(microsecond=0)


    def ottieni_link_da_id_canale(self, link_id: int, canale_id: str) -> Pubblica | None:

        return self.pubblica_repository.get_channel_link_by_id_canale(link_id, canale_id)


    def ottieni_link_non_pubblicati_per_canale(self, canale_id: str) -> list[Pubblica] | None:

        return self.pubblica_repository.get_channel_link_non_pubblicati(canale_id)


    def ottieni_link_pubblicato_ultime_24h(self, canale_id: str, asin: str) -> Pubblica | None:

        return self.pubblica_repository.get_pubblicato_ultime_24h(canale_id, asin)

    def ottieni_ultimo_pubblicato_da_canale_e_asin(self, canale_id: str, asin: str) -> Pubblica | None:

        return self.pubblica_repository.get_ultimo_pubblicato_da_canale_e_asin(canale_id, asin)

    def confronta_prezzo_ultimo_pubblicato(self, link: Pubblica) -> tuple[Pubblica | None, bool]:

        if not link or not link.storico_prezzo:
            return None, False

        link_per_confronto = self.ottieni_ultimo_pubblicato_da_canale_e_asin(link.id_canale, link.asin_prodotti)

        if not link_per_confronto or not link_per_confronto.storico_prezzo:
            return None, False

        return link_per_confronto, link_per_confronto.storico_prezzo.prezzo == link.storico_prezzo.prezzo

    def ottieni_prodotti_non_pubblicati_da_tanto_tempo(self, id_canale: str, page: int = 0, page_size: int = 10) -> tuple[list[Pubblica], int]:

        return self.pubblica_repository.get_non_pubblicati_da_tanto_tempo(id_canale, page, page_size)


    def aggiungi_link(self, link: Pubblica) -> Pubblica:

        return self.pubblica_repository.create(link)


    def rimuovi_link(self, link: Pubblica) -> None:

        self.pubblica_repository.delete(link)