from datetime import datetime

from models.prodotto import Prodotto
from models.prezzo_storico import PrezzoStorico
from repositories.prezzo_storico_repository import PrezziStoricoRepository
from repositories.prodotto_repository import ProdottoRepository

from sqlalchemy.orm import Session


class ProdottoService:

    def __init__(self, session: Session):
        self.session = session
        self.prodotto_repository = ProdottoRepository(session)
        self.prezzo_storico_repository = PrezziStoricoRepository(session)


    def aggiungi_prodotto(self, prodotto: Prodotto):

        self.prodotto_repository.create(prodotto)

        storico = PrezzoStorico(
            asin=prodotto.asin,
            prezzo=prodotto.prezzo,
            valuta=prodotto.valuta,
            venditore=prodotto.venditore
        )

        self.prezzo_storico_repository.create(storico)

    def aggiorna_prezzo(self, asin: str, nuovo_prezzo: float, valuta: str, venditore: str):

        prodotto = self.prodotto_repository.get_by_asin(asin)

        if not prodotto:
            return False

        prodotto.prezzo = nuovo_prezzo
        prodotto.valuta = valuta
        prodotto.venditore = venditore
        prodotto.last_check = datetime.now()

        storico = PrezzoStorico(
            asin=prodotto.asin,
            prezzo=prodotto.prezzo,
            valuta=prodotto.valuta,
            venditore=prodotto.venditore
        )

        self.prezzo_storico_repository.create(storico)

        return True

    def ottieni_prodotto(self, asin: str) -> Prodotto | None:
        return self.prodotto_repository.get_by_asin(asin)