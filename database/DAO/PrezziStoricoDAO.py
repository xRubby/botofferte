from database.Connessione import Connessione
from database.Entity.PrezziStorico import PrezziStorico

from typing import List

class PrezziStoricoDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self) -> 'PrezziStoricoDAO':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.conn.close()

    def close(self) -> None:
        self.conn.close()

    def insert(self, asin: str, prezzo: float, valuta: str, venditore: str) -> None:
        self.cursor.execute('''INSERT INTO PrezziStorico (asin, prezzo, valuta, venditore) VALUES (?, ?, ?, ?)''', 
                            (asin, prezzo, valuta, venditore))
        self.conn.commit()
    
    def get_by_asin(self, asin: str) -> List[PrezziStorico]:
        self.cursor.execute("SELECT * FROM PrezziStorico WHERE asin = ? ORDER BY rilevato DESC", (asin,))
        rows = self.cursor.fetchall()
        return [PrezziStorico(*row) for row in rows] 

    def update(self, id: int, asin: str, prezzo: float, valuta: str, venditore: str, rilevato: int) -> None:
        self.cursor.execute('''UPDATE PrezziStorico SET asin = ?, prezzo = ?, valuta = ?, venditore = ?, rilevato = ? WHERE id = ?''', 
                            (asin, prezzo, valuta, rilevato, venditore, id))
        self.conn.commit()

    def delete(self, id: int) -> None:
        self.cursor.execute("DELETE FROM PrezziStorico WHERE id = ?", (id,))
        self.conn.commit()

    