from datetime import datetime

from models.prodotto import Prodotto
from models.prezzo_storico import PrezziStorico
from repositories.prodotto_repository import ProdottoRepository


class ProdottoService:

    def __init__(self, prodotto_repository: ProdottoRepository):
        self.repository = prodotto_repository


    def crea_prodotto(self, prodotto: Prodotto):

        self.repository.create(prodotto)

        storico = PrezziStorico(
            asin=prodotto.asin,
            prezzo=prodotto.prezzo,
            valuta=prodotto.valuta,
            venditore=prodotto.venditore
        )

        self.session.add(storico)

        self.session.commit()

    def aggiorna_prezzo(self, asin: str, nuovo_prezzo: float, valuta: str, venditore: str):

        prodotto = self.repository.get_by_asin(asin)

        if not prodotto:
            return False

        prodotto.prezzo = nuovo_prezzo
        prodotto.valuta = valuta
        prodotto.venditore = venditore
        prodotto.last_check = datetime.now()

        storico = PrezziStorico(
            asin=asin,
            prezzo=nuovo_prezzo,
            valuta=valuta,
            venditore=venditore
        )

        self.session.add(storico)

        self.session.commit()

        return True