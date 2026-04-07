from database.Connessione import Connessione
from database.Entity.PrezziStorico import PrezziStorico

class PrezziStoricoDAO:
    def insert(self, asin: str, prezzo: float, valuta: str, venditore: str) -> None:
        with Connessione() as con:
            con.execute('''INSERT INTO PrezziStorico (asin, prezzo, valuta, venditore) VALUES (?, ?, ?, ?)''', 
                            (asin, prezzo, valuta, venditore))
    
    def get_by_asin(self, asin: str) -> list[PrezziStorico]:
        with Connessione() as con:
            rows = con.execute("SELECT * FROM PrezziStorico WHERE asin = ? ORDER BY rilevato DESC", (asin,)).fetchall()
        return [PrezziStorico(*row) for row in rows] 

    def update(self, id: int, asin: str, prezzo: float, valuta: str, venditore: str, rilevato: int) -> None:
        with Connessione() as con:
            con.execute('''UPDATE PrezziStorico SET asin = ?, prezzo = ?, valuta = ?, venditore = ?, rilevato = ? WHERE id = ?''', 
                            (asin, prezzo, valuta, rilevato, venditore, id))

    def delete(self, id: int) -> None:
        with Connessione() as con:
            con.execute("DELETE FROM PrezziStorico WHERE id = ?", (id,))

    