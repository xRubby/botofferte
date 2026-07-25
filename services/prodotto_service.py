from datetime import datetime

from models.prodotto import Prodotto
from models.prezzo_storico import PrezzoStorico
from repositories.prezzo_storico_repository import PrezzoStoricoRepository
from repositories.prodotto_repository import ProdottoRepository

from sqlalchemy.orm import Session


class ProdottoService:

    def __init__(self, session: Session):
        self.session = session
        self.prodotto_repository = ProdottoRepository(session)
        self.prezzo_storico_repository = PrezzoStoricoRepository(session)


    def aggiungi_prodotto(self, prodotto: Prodotto):

        self.prodotto_repository.create(prodotto)

        storico = PrezzoStorico(
            asin=prodotto.asin,
            prezzo=prodotto.prezzo,
            valuta=prodotto.valuta,
            venditore=prodotto.venditore
        )

        self.prezzo_storico_repository.create(storico)

    def aggiorna_prezzo_prodotto(self, prodotto: Prodotto, info_prodotto: dict) -> None:

        if info_prodotto and (prodotto.prezzo != info_prodotto["prezzo"]):
            prodotto.asin = info_prodotto["ASIN"]
            prodotto.prezzo = info_prodotto["prezzo"]
            prodotto.old_prezzo = info_prodotto["old_prezzo"]
            prodotto.valuta = info_prodotto["valuta"]
            prodotto.sconto = info_prodotto["sconto"]
            prodotto.venditore = info_prodotto["venditore"]
            prodotto.img_url = info_prodotto["img_url"]
            prodotto.spedito_amazon = info_prodotto["spedito_Amazon"]
            prodotto.offertaesclusiva = info_prodotto.get("offertaesclusiva", None)
            prodotto.last_check = datetime.now()
            prodotto.preorder=bool(info_prodotto["preorder"])
            prodotto.data_preordine=info_prodotto["data_preordine"]

            storico = PrezzoStorico(
                asin=prodotto.asin,
                prezzo=prodotto.prezzo,
                valuta=prodotto.valuta,
                venditore=prodotto.venditore
            )

            self.prezzo_storico_repository.create(storico)

        elif info_prodotto:
            prodotto.last_check = datetime.now()

    def ottieni_prodotto(self, asin: str) -> Prodotto | None:
        return self.prodotto_repository.get_by_asin(asin)