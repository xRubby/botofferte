from database.Connessione import Connessione
from database.Entity.Pubblica import Pubblica

from datetime import datetime
from typing import List

class PubblicaDAO:
    def insert(self, id_canale: str, asin_prodotti: str, messaggio: str, is_pubblicato: bool = 0) -> None:
        with Connessione() as con:
            con.execute(
            "INSERT INTO Pubblica (id, id_canale, asin_prodotti, messaggio, isPubblicato) VALUES (?, ?, ?, ?, ?)", 
            (id, id_canale, asin_prodotti, messaggio, is_pubblicato)
        )

    def update(self, id: int, id_canale: str, asin_prodotti: str, messaggio: str, is_pubblicato: bool) -> None:
        with Connessione() as con:
            con.execute(
            "UPDATE Pubblica SET id_canale = ?, asin_prodotti = ?, messaggio = ?, isPubblicato = ? WHERE id = ?", 
            (id_canale, asin_prodotti ,messaggio, is_pubblicato, id, id_canale, asin_prodotti)
        )

    def update_pubblicato(self, id: int, is_pubblicato: bool) -> None:
        with Connessione() as con:
            con.execute(
            "UPDATE Pubblica SET isPubblicato = ?, data_pubblicazione = ? WHERE id = ?", 
            (is_pubblicato, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id,)
        )

    def delete(self, id: int, id_canale: str, asin_prodotti: str) -> None:
        with Connessione() as con:
            con.execute(
            "DELETE FROM Pubblica WHERE id = ? AND id_canale = ? AND asin_prodotti = ?", 
            (id, id_canale, asin_prodotti)
        )

    def get(self, id: int, id_canale: str, asin_prodotti: str) -> Pubblica | None:
        with Connessione() as con:
            row = con.execute("SELECT * FROM Pubblica WHERE id = ? AND id_canale = ? AND asin_prodotti = ?",(id, id_canale, asin_prodotti)).fetchone()
            return Pubblica(*row) if row else None

    def get_all(self) -> List[Pubblica]:
        with Connessione() as con:
            rows = con.execute("SELECT * FROM Pubblica").fetchall()
            return [Pubblica(*row) for row in rows] 