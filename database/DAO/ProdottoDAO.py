from database.Connessione import Connessione
from database.Entity.Prodotto import Prodotto

from typing import List

import re

class ProdottoDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self) -> 'ProdottoDAO':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.conn.close()

    def insert(self, asin: str, titolo: str, prezzo: float, old_prezzo: float, valuta: str, sconto: float, venditore: str, spedito_Amazon: bool, link: str, img_url: str, brand: str, preorder: bool, data_preordine: str, isPrime: bool, isWarehouse: bool, condizione: str, condizione_descrizione: str) -> None:
        self.cursor.execute('''INSERT INTO prodotti VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                            (asin, titolo, prezzo, old_prezzo, valuta, sconto, venditore, spedito_Amazon,
                             link, img_url, brand, preorder, data_preordine, isPrime, isWarehouse, condizione, condizione_descrizione))
        self.conn.commit()

    def insert_Prodotto(self, prodotto: Prodotto):
        self.cursor.execute('''INSERT INTO prodotti VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (prodotto.asin, prodotto.titolo, prodotto.prezzo, prodotto.old_prezzo, prodotto.valuta, 
                         prodotto.sconto, prodotto.venditore, prodotto.spedito_Amazon, prodotto.link, prodotto.img_url, 
                         prodotto.brand, prodotto.preorder, prodotto.data_preordine, prodotto.isPrime, prodotto.isWarehouse, 
                         prodotto.condizione, prodotto.condizione_descrizione, prodotto.last_check, prodotto.priorita))
        self.conn.commit()

    def update(self, asin: str, titolo: str, prezzo: float, old_prezzo: float, valuta: str, sconto: float, venditore: str, spedito_Amazon: bool, link: str, img_url: str, brand: str, preorder: bool, data_preordine: str, isPrime: bool, isWarehouse: bool, condizione: str, condizione_descrizione: str, last_check: int) -> None:
        self.cursor.execute('''UPDATE prodotti SET titolo = ?, prezzo = ?, old_prezzo = ?, valuta = ?, 
                            sconto = ?, venditore = ?, spedito_Amazon = ?, 
                            link = ?, img_url = ?, brand = ?, preorder = ?, data_preordine = ?, 
                            isPrime = ?, isWarehouse = ?, condizione = ?, condizione_descrizione = ?, last_check = ? 
                            WHERE asin = ?''', 
                            (titolo, prezzo, old_prezzo, valuta, sconto, venditore, spedito_Amazon,
                             link, img_url, brand, preorder, data_preordine, isPrime, isWarehouse, condizione, condizione_descrizione, last_check, asin))
        self.conn.commit()

    def update_price(self, asin: str, prezzo: float, old_prezzo: float, valuta: str, sconto: float, venditore: str, spedito_Amazon: bool, last_check: int) -> None:
        self.cursor.execute('''UPDATE prodotti SET prezzo = ?, old_prezzo = ?, valuta = ?, 
                            sconto = ?, venditore = ?, spedito_Amazon = ?, last_check = ? 
                            WHERE asin = ?''', 
                            (prezzo, old_prezzo, valuta, sconto, venditore, spedito_Amazon, last_check, asin))
        self.conn.commit()

    def delete(self, asin) -> None:
        self.cursor.execute("DELETE FROM prodotti WHERE asin = ?", (asin,))
        self.conn.commit()

    def get_by_asin(self, asin) -> Prodotto:
        self.cursor.execute("SELECT * FROM prodotti WHERE asin = ?", (asin,))
        row = self.cursor.fetchone()
        if row:
            return Prodotto(*row)
        return None
    
    def get_by_titolo(self, titolo) -> Prodotto:

        titolo_pulito  = re.sub(r'[^a-zA-Z0-9 ]', '', titolo)

        self.cursor.execute("SELECT p.* FROM Prodotti_fts fts JOIN Prodotti p ON fts.asin = p.asin WHERE fts.titolo MATCH ?", (titolo_pulito,))
        row = self.cursor.fetchone()
        if row:
            return Prodotto(*row)
        return None

    def get_all(self) -> List[Prodotto]:
        self.cursor.execute("SELECT * FROM prodotti")
        rows = self.cursor.fetchall()

        return [Prodotto(*row) for row in rows] 
    
    def close(self) -> None:
        self.conn.close()