from database.Connessione import Connessione
from database.Entity.Prodotto import Prodotto

class ProdottoDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def insert(self, prodotto):
        self.cursor.execute('''INSERT INTO prodotti VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                            (prodotto.getAsin(), prodotto.getTitolo(), prodotto.getPrezzo(), prodotto.getOldPrezzo(), 
                             prodotto.getValuta(), prodotto.getSconto(), prodotto.getScontoPercentuale(), prodotto.getVenditore(), 
                             prodotto.getSpeditoDa(), prodotto.getLink(), prodotto.getImgUrl(), prodotto.getBrand(), 
                             prodotto.getPreorder(), prodotto.getDataPreordine(), prodotto.getIsPrime(), 
                             prodotto.getIsWarehouse(), prodotto.getCondizione(), prodotto.getCondizioneDescrizione()))
        self.conn.commit()

    def update(self, prodotto: Prodotto):
        self.cursor.execute('''UPDATE prodotti SET titolo = ?, prezzo = ?, old_prezzo = ?, valuta = ?, 
                            sconto = ?, sconto_percentuale = ?, venditore = ?, spedito_da = ?, 
                            link = ?, img_url = ?, brand = ?, preorder = ?, data_preordine = ?, 
                            isPrime = ?, isWarehouse = ?, condizione = ?, condizione_descrizione = ? 
                            WHERE asin = ?''', 
                            (prodotto.getTitolo(), prodotto.getPrezzo(), prodotto.getOldPrezzo(), prodotto.getValuta(),
                             prodotto.getSconto(), prodotto.getScontoPercentuale(), prodotto.getVenditore(), prodotto.getSpeditoDa(),
                             prodotto.getLink(), prodotto.getImgUrl(), prodotto.getBrand(), prodotto.getPreorder(),
                             prodotto.getDataPreordine(), prodotto.getIsPrime(), prodotto.getIsWarehouse(),
                             prodotto.getCondizione(), prodotto.getCondizioneDescrizione(), prodotto.getAsin()))
        self.conn.commit()

    def delete(self, asin):
        self.cursor.execute("DELETE FROM prodotti WHERE asin = ?", (asin,))
        self.conn.commit()

    def get(self, asin):
        self.cursor.execute("SELECT * FROM prodotti WHERE asin = ?", (asin,))
        return self.cursor.fetchone()

    def get_all(self):
        self.cursor.execute("SELECT * FROM prodotti")
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()