from database.Connessione import Connessione
from database.Entity.Prodotto import Prodotto
from database.DAO.PrezziStoricoDAO import PrezziStoricoDAO
import re

class ProdottoDAO:
    def __init__(self):
        self._con = None

    def __enter__(self):
        self._connessione = Connessione()
        self._con = self._connessione.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._connessione.__exit__(exc_type, exc_val, exc_tb)

    def _get_con(self):
        if self._con is not None:
            return self._con
        raise RuntimeError("ProdottoDAO deve essere usato dentro un blocco 'with'")

    def insert(self, asin: str, titolo: str, prezzo: float, old_prezzo: float, valuta: str, sconto: float,
               venditore: str, spedito_Amazon: bool, link: str, img_url: str, brand: str, preorder: bool,
               data_preordine: str, isPrime: bool, isWarehouse: bool, condizione: str,
               condizione_descrizione: str, offertaesclusiva: str) -> None:
        self._get_con().execute(
             """
            INSERT INTO prodotti (
                asin, titolo, prezzo, old_prezzo, valuta, sconto,
                venditore, spedito_Amazon, link, img_url, brand,
                preorder, data_preordine, isPrime, isWarehouse,
                condizione, condizione_descrizione, offertaesclusiva
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (asin, titolo, prezzo, old_prezzo, valuta, sconto, venditore, spedito_Amazon,
            link, img_url, brand, preorder, data_preordine, isPrime, isWarehouse,
            condizione, condizione_descrizione, offertaesclusiva)
        )
        self._get_con().execute(
            "INSERT INTO PrezziStorico (asin, prezzo, valuta, venditore) VALUES (?, ?, ?, ?)",
            (asin, prezzo, valuta, venditore)
        )

    def insert_Prodotto(self, prodotto: Prodotto) -> None:
        self._get_con().execute(
            "INSERT INTO prodotti VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (prodotto.asin, prodotto.titolo, prodotto.prezzo, prodotto.old_prezzo, prodotto.valuta,
             prodotto.sconto, prodotto.venditore, prodotto.spedito_Amazon, prodotto.link, prodotto.img_url,
             prodotto.brand, prodotto.preorder, prodotto.data_preordine, prodotto.isPrime, prodotto.isWarehouse,
             prodotto.condizione, prodotto.condizione_descrizione, prodotto.last_check,
             prodotto.priorita, prodotto.offertaesclusiva)
        )
        with PrezziStoricoDAO() as ps_dao:
            ps_dao.insert(prodotto.asin, prodotto.prezzo, prodotto.valuta, prodotto.venditore)

    def update(self, asin: str, titolo: str, prezzo: float, old_prezzo: float, valuta: str, sconto: float,
               venditore: str, spedito_Amazon: bool, link: str, img_url: str, brand: str, preorder: bool,
               data_preordine: str, isPrime: bool, isWarehouse: bool, condizione: str,
               condizione_descrizione: str, last_check: int, offertaesclusiva: str) -> None:
        self._get_con().execute(
            '''UPDATE prodotti SET titolo = ?, prezzo = ?, old_prezzo = ?, valuta = ?,
               sconto = ?, venditore = ?, spedito_Amazon = ?,
               link = ?, img_url = ?, brand = ?, preorder = ?, data_preordine = ?,
               isPrime = ?, isWarehouse = ?, condizione = ?, condizione_descrizione = ?,
               last_check = ?, offertaesclusiva = ? WHERE asin = ?''',
            (titolo, prezzo, old_prezzo, valuta, sconto, venditore, spedito_Amazon,
             link, img_url, brand, preorder, data_preordine, isPrime, isWarehouse,
             condizione, condizione_descrizione, last_check, offertaesclusiva, asin)
        )

    def update_price(self, asin: str, prezzo: float, old_prezzo: float, valuta: str, sconto: float,
                     venditore: str, spedito_Amazon: bool, offertaesclusiva: str) -> None:
        self._get_con().execute(
            '''UPDATE prodotti SET prezzo = ?, old_prezzo = ?, valuta = ?,
               sconto = ?, venditore = ?, spedito_Amazon = ?, offertaesclusiva = ?
               WHERE asin = ?''',
            (prezzo, old_prezzo, valuta, sconto, venditore, spedito_Amazon, offertaesclusiva, asin)
        )
        with PrezziStoricoDAO() as ps_dao:
            ps_dao.insert(asin, prezzo, valuta, venditore)

    def delete(self, asin: str) -> None:
        self._get_con().execute("DELETE FROM prodotti WHERE asin = ?", (asin,))

    def get_by_asin(self, asin: str) -> Prodotto | None:
        row = self._get_con().execute(
            "SELECT * FROM prodotti WHERE asin = ?", (asin,)
        ).fetchone()
        return Prodotto(*row) if row else None

    def get_by_titolo(self, titolo: str) -> Prodotto | None:
        titolo_pulito = re.sub(r'[^a-zA-Z0-9 ]', '', titolo)
        row = self._get_con().execute(
            "SELECT p.* FROM Prodotti_fts fts JOIN Prodotti p ON fts.asin = p.asin WHERE fts.titolo MATCH ?",
            (titolo_pulito,)
        ).fetchone()
        return Prodotto(*row) if row else None

    def get_all(self) -> list[Prodotto]:
        rows = self._get_con().execute("SELECT * FROM prodotti").fetchall()
        return [Prodotto(*row) for row in rows]