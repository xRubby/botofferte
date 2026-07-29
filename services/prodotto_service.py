from datetime import datetime

from models.prodotto import Prodotto
from models.prezzo_storico import PrezzoStorico
from repositories.prezzo_storico_repository import PrezzoStoricoRepository
from repositories.prodotto_repository import ProdottoRepository

from sqlalchemy.orm import Session

from services.categoria_service import CategoriaService
from utils.formattazione_data import converti_data_preordine_per_db


class ProdottoService:

    def __init__(self, session: Session):
        self.session = session
        self.prodotto_repository = ProdottoRepository(session)
        self.prezzo_storico_repository = PrezzoStoricoRepository(session)
        self.categoria_service = CategoriaService(session)


    def aggiungi_prodotto(self, info_prodotto: dict) -> Prodotto | None:

        if not info_prodotto:
            return None

        categoria_root, categoria = self.categoria_service.aggiungi_o_ottieni_categorie_da_lista(info_prodotto["categorie"])

        prodotto = Prodotto(
            asin=info_prodotto["ASIN"],
            titolo=info_prodotto["titolo"],
            prezzo=info_prodotto["prezzo"],
            old_prezzo=info_prodotto["old_prezzo"],
            valuta=info_prodotto["valuta"],
            sconto=info_prodotto["sconto"],
            venditore=info_prodotto["venditore"],
            spedito_amazon=info_prodotto["spedito_Amazon"],
            link=info_prodotto["link"],
            img_url=info_prodotto["img_url"],
            brand=info_prodotto["brand"],
            preorder=bool(info_prodotto["preorder"]),
            data_preordine=converti_data_preordine_per_db(info_prodotto["data_preordine"]),
            is_prime=bool(info_prodotto["isPrime"]),
            is_warehouse=info_prodotto["isWarehouse"],
            condizione=info_prodotto["condizione"],
            condizione_descrizione=info_prodotto["condizione_commento"],
            offertaesclusiva=info_prodotto["offertaexcl"],
            root_categoria_id = categoria_root.id if categoria_root else None,
            categoria_id = categoria.id if categoria else None
        )

        prodotto = self.prodotto_repository.create(prodotto)

        storico = PrezzoStorico(
            asin=prodotto.asin,
            prezzo=prodotto.prezzo,
            valuta=prodotto.valuta,
            venditore=prodotto.venditore
        )

        self.prezzo_storico_repository.create(storico)

        return prodotto

    def aggiorna_prezzo_prodotto(self, prodotto: Prodotto, info_prodotto: dict) -> None:

        categoria_root, categoria = self.categoria_service.aggiungi_o_ottieni_categorie_da_lista(info_prodotto["categorie"])

        if info_prodotto and (prodotto.prezzo != info_prodotto["prezzo"]):
            prodotto.asin = info_prodotto["ASIN"]
            prodotto.prezzo = info_prodotto["prezzo"]
            prodotto.old_prezzo = info_prodotto["old_prezzo"]
            prodotto.valuta = info_prodotto["valuta"]
            prodotto.sconto = info_prodotto["sconto"]
            prodotto.venditore = info_prodotto["venditore"]
            prodotto.img_url = info_prodotto["img_url"]
            prodotto.spedito_amazon = info_prodotto["spedito_Amazon"]
            prodotto.offertaesclusiva = info_prodotto["offertaexcl"]
            prodotto.last_check = datetime.now()
            prodotto.preorder = bool(info_prodotto["preorder"]) 
            prodotto.data_preordine = converti_data_preordine_per_db(info_prodotto["data_preordine"])
            prodotto.root_categoria_id = categoria_root.id if categoria_root else None
            prodotto.categoria_id = categoria.id if categoria else None

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