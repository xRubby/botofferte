from database.Connessione import Connessione
from database.Entity.Pubblica import Pubblica
from datetime import datetime
from typing import List

class PubblicaDAO:
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
        raise RuntimeError("PubblicaDAO deve essere usato dentro un blocco 'with'")

    def insert(self, id_canale: str, asin_prodotti: str, messaggio: str, link: str, link_short: str, img_bytes: bytes, is_pubblicato: bool = False) -> None:
        img_value = img_bytes.getvalue() if img_bytes is not None else None

        self._get_con().execute(
            "INSERT INTO Pubblica (id_canale, asin_prodotti, messaggio, isPubblicato, link, link_short, img_bytes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (id_canale, asin_prodotti, messaggio, is_pubblicato, link, link_short, img_value)
        )

    def update(self, id: int, id_canale: str, asin_prodotti: str, messaggio: str, is_pubblicato: bool) -> None:
        self._get_con().execute(
            "UPDATE Pubblica SET id_canale = ?, asin_prodotti = ?, messaggio = ?, isPubblicato = ? WHERE id = ?",
            (id_canale, asin_prodotti, messaggio, is_pubblicato, id)
        )

    def update_pubblicato(self, id: int, is_pubblicato: bool) -> None:
        self._get_con().execute(
            "UPDATE Pubblica SET isPubblicato = ?, data_pubblicazione = ? WHERE id = ?",
            (is_pubblicato, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id)
        )

    def delete(self, id: int, id_canale: str, asin_prodotti: str) -> None:
        self._get_con().execute(
            "DELETE FROM Pubblica WHERE id = ? AND id_canale = ? AND asin_prodotti = ?",
            (id, id_canale, asin_prodotti)
        )

    def get(self, id: int, id_canale: str, asin_prodotti: str) -> Pubblica | None:
        row = self._get_con().execute(
            "SELECT * FROM Pubblica WHERE id = ? AND id_canale = ? AND asin_prodotti = ?",
            (id, id_canale, asin_prodotti)
        ).fetchone()
        return Pubblica(*row) if row else None

    def get_all(self) -> List[Pubblica]:
        rows = self._get_con().execute("SELECT * FROM Pubblica").fetchall()
        return [Pubblica(*row) for row in rows]
    
    def get_channel_link_non_pubblicati(self, id_canale: str) -> List[Pubblica]:
        rows = self._get_con().execute(
            "SELECT * FROM Pubblica WHERE id_canale = ? AND isPubblicato = 0 ORDER BY id ASC",
            (id_canale,)
        ).fetchall()
        return [Pubblica(*row) for row in rows]
 
    def get_channel_link_by_id(self, id: int, id_canale: str) -> Pubblica | None:
        row = self._get_con().execute(
            "SELECT * FROM Pubblica WHERE id = ? AND id_canale = ?",
            (id, id_canale)
        ).fetchone()
        return Pubblica(*row) if row else None
    
    def get_pubblicato_ultime_24h(self, id_canale: str, asin: str) -> Pubblica | None:
        row = self._get_con().execute(
            """
            SELECT *
            FROM Pubblica
            WHERE id_canale = ?
            AND asin_prodotti = ?
            AND isPubblicato = 1
            AND data_pubblicazione >= datetime('now', '-24 hours')
            LIMIT 1
            """,
            (id_canale, asin)
        ).fetchone()

        return Pubblica(*row) if row else None