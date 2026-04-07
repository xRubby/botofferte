from database.Connessione import Connessione
from database.Entity.Prodotto import Prodotto
from database.DAO.PrezziStoricoDAO import PrezziStoricoDAO

import re

class ProdottoDAO:
    def insert(self, asin: str, titolo: str, prezzo: float, old_prezzo: float, valuta: str, sconto: float, venditore: str, spedito_Amazon: bool, link: str, img_url: str, brand: str, preorder: bool, data_preordine: str, isPrime: bool, isWarehouse: bool, condizione: str, condizione_descrizione: str, offertaesclusiva: str) -> None:
        with Connessione() as con:
            con.execute('''INSERT INTO prodotti VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                            (asin, titolo, prezzo, old_prezzo, valuta, sconto, venditore, spedito_Amazon,
                             link, img_url, brand, preorder, data_preordine, isPrime, isWarehouse, condizione, condizione_descrizione, offertaesclusiva))
        PrezziStoricoDAO.insert(asin, prezzo, valuta, venditore)

    def insert_Prodotto(self, prodotto: Prodotto):
        with Connessione() as con:
            con.execute('''INSERT INTO prodotti VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (prodotto.asin, prodotto.titolo, prodotto.prezzo, prodotto.old_prezzo, prodotto.valuta, 
                         prodotto.sconto, prodotto.venditore, prodotto.spedito_Amazon, prodotto.link, prodotto.img_url, 
                         prodotto.brand, prodotto.preorder, prodotto.data_preordine, prodotto.isPrime, prodotto.isWarehouse, 
                         prodotto.condizione, prodotto.condizione_descrizione, prodotto.last_check, prodotto.priorita, prodotto.offertaesclusiva))
        PrezziStoricoDAO.insert(prodotto.asin, prodotto.prezzo, prodotto.valuta, prodotto.venditore)

    def update(self, asin: str, titolo: str, prezzo: float, old_prezzo: float, valuta: str, sconto: float, venditore: str, spedito_Amazon: bool, link: str, img_url: str, brand: str, preorder: bool, data_preordine: str, isPrime: bool, isWarehouse: bool, condizione: str, condizione_descrizione: str, last_check: int, offertaesclusiva: str) -> None:
        with Connessione() as con:
            con.execute('''UPDATE prodotti SET titolo = ?, prezzo = ?, old_prezzo = ?, valuta = ?, 
                            sconto = ?, venditore = ?, spedito_Amazon = ?, 
                            link = ?, img_url = ?, brand = ?, preorder = ?, data_preordine = ?, 
                            isPrime = ?, isWarehouse = ?, condizione = ?, condizione_descrizione = ?, last_check = ?, offertaesclusiva = ? 
                            WHERE asin = ?''', 
                            (titolo, prezzo, old_prezzo, valuta, sconto, venditore, spedito_Amazon,
                             link, img_url, brand, preorder, data_preordine, isPrime, isWarehouse, condizione, condizione_descrizione, last_check, offertaesclusiva, asin))

    def update_price(self, asin: str, prezzo: float, old_prezzo: float, valuta: str, sconto: float, venditore: str, spedito_Amazon: bool, offertaesclusiva: str) -> None:
        with Connessione() as con:
            con.execute('''UPDATE prodotti SET prezzo = ?, old_prezzo = ?, valuta = ?, 
                            sconto = ?, venditore = ?, spedito_Amazon = ?, offertaesclusiva = ? 
                            WHERE asin = ?''', 
                            (prezzo, old_prezzo, valuta, sconto, venditore, spedito_Amazon, offertaesclusiva, asin))
        PrezziStoricoDAO.insert(asin, prezzo, valuta, venditore)

    def delete(self, asin) -> None:
        with Connessione() as con:
            con.execute("DELETE FROM prodotti WHERE asin = ?", (asin,))

    def get_by_asin(self, asin) -> Prodotto | None:
        with Connessione() as con:
            row = con.execute("SELECT * FROM prodotti WHERE asin = ?", (asin,)).fetchone()
        return Prodotto(*row) if row else None
    
    def get_by_titolo(self, titolo) -> Prodotto | None:

        titolo_pulito  = re.sub(r'[^a-zA-Z0-9 ]', '', titolo)

        with Connessione() as con:
            row = con.execute("SELECT p.* FROM Prodotti_fts fts JOIN Prodotti p ON fts.asin = p.asin WHERE fts.titolo MATCH ?", (titolo_pulito,)).fetchone()
        return Prodotto(*row) if row else None

    def get_all(self) -> list[Prodotto]:
        with Connessione() as con:
            rows = con.execute("SELECT * FROM prodotti").fetchall()

        return [Prodotto(*row) for row in rows] 