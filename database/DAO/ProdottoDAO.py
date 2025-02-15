from database.Connessione import Connessione
from database.Entity.Prodotto import Prodotto

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
        self.cursor.execute('''INSERT INTO prodotti VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                        (prodotto.getAsin(), prodotto.getTitolo(), prodotto.getPrezzo(), prodotto.getOldPrezzo(), prodotto.getValuta(), 
                         prodotto.getSconto(), prodotto.getVenditore(), prodotto.getSpeditoAmazon(), prodotto.getLink(), prodotto.getImgUrl(), 
                         prodotto.getBrand(), prodotto.getPreorder(), prodotto.getDataPreordine(), prodotto.getIsPrime(), prodotto.getIsWarehouse(), 
                         prodotto.getCondizione(), prodotto.getCondizioneDescrizione()))
        self.conn.commit()

    def update(self, asin: str, titolo: str, prezzo: float, old_prezzo: float, valuta: str, sconto: float, venditore: str, spedito_Amazon: bool, link: str, img_url: str, brand: str, preorder: bool, data_preordine: str, isPrime: bool, isWarehouse: bool, condizione: str, condizione_descrizione: str) -> None:
        self.cursor.execute('''UPDATE prodotti SET titolo = ?, prezzo = ?, old_prezzo = ?, valuta = ?, 
                            sconto = ?, venditore = ?, spedito_da = ?, 
                            link = ?, img_url = ?, brand = ?, preorder = ?, data_preordine = ?, 
                            isPrime = ?, isWarehouse = ?, condizione = ?, condizione_descrizione = ? 
                            WHERE asin = ?''', 
                            (titolo, prezzo, old_prezzo, valuta, sconto, venditore, spedito_Amazon,
                             link, img_url, brand, preorder, data_preordine, isPrime, isWarehouse, condizione, condizione_descrizione, asin))
        self.conn.commit()

    def delete(self, asin) -> None:
        self.cursor.execute("DELETE FROM prodotti WHERE asin = ?", (asin,))
        self.conn.commit()

    def get_by_asin(self, asin) -> Prodotto:
        self.cursor.execute("SELECT * FROM prodotti WHERE asin = ?", (asin,))
        return self.cursor.fetchone()
    
    def get_by_titolo(self, titolo) -> Prodotto:
        self.cursor.execute("SELECT * FROM prodotti WHERE titolo LIKE ?", ('%' + titolo + '%',))
        return self.cursor.fetchone()

    def get_all(self) -> list:
        self.cursor.execute("SELECT * FROM prodotti")
        return self.cursor.fetchall()
    
    def close(self) -> None:
        self.conn.close()