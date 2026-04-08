from database.Connessione import Connessione
from database.Entity.PrezziStorico import PrezziStorico

class PrezziStoricoDAO:
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
        raise RuntimeError("PrezziStoricoDAO deve essere usato dentro un blocco 'with'")

    def insert(self, asin: str, prezzo: float, valuta: str, venditore: str) -> None:
        self._get_con().execute(
            "INSERT INTO PrezziStorico (asin, prezzo, valuta, venditore) VALUES (?, ?, ?, ?)",
            (asin, prezzo, valuta, venditore)
        )

    def update(self, id: int, asin: str, prezzo: float, valuta: str, venditore: str, rilevato: int) -> None:
        self._get_con().execute(
            "UPDATE PrezziStorico SET asin = ?, prezzo = ?, valuta = ?, venditore = ?, rilevato = ? WHERE id = ?",
            (asin, prezzo, valuta, venditore, rilevato, id)
        )

    def delete(self, id: int) -> None:
        self._get_con().execute(
            "DELETE FROM PrezziStorico WHERE id = ?", (id,)
        )

    def get_by_asin(self, asin: str) -> list[PrezziStorico]:
        rows = self._get_con().execute(
            "SELECT * FROM PrezziStorico WHERE asin = ? ORDER BY rilevato DESC", (asin,)
        ).fetchall()
        return [PrezziStorico(*row) for row in rows]