from database.Connessione import Connessione
from database.Entity.Pubblica import Pubblica

from typing import List

class PubblicaDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self) -> 'PubblicaDAO':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.conn.close()

    def insert(self, id_canale: str, asin_prodotti: str, messaggio: str, is_pubblicato: bool = 0) -> None:

        id = self.__get_next_id()

        self.cursor.execute(
            "INSERT INTO Pubblica (id, id_canale, asin_prodotti, messaggio, isPubblicato) VALUES (?, ?, ?, ?, ?)", 
            (id, id_canale, asin_prodotti, messaggio, is_pubblicato)
        )
        self.conn.commit()

    def update(self, id: int, id_canale: str, asin_prodotti: str, messaggio: str, is_pubblicato: bool) -> None:
        self.cursor.execute(
            "UPDATE Pubblica SET messaggio = ?, isPubblicato = ? WHERE id = ? AND id_canale = ? AND asin_prodotti = ?", 
            (messaggio, is_pubblicato, id, id_canale, asin_prodotti)
        )
        self.conn.commit()

    def update_is_pubblicato(self, id: int, id_canale: str, asin_prodotti: str, is_pubblicato: bool) -> None:
        self.cursor.execute(
            "UPDATE Pubblica SET isPubblicato = ? WHERE id = ? AND id_canale = ? AND asin_prodotti = ?", 
            (is_pubblicato, id, id_canale, asin_prodotti)
        )
        self.conn.commit()

    def delete(self, id: int, id_canale: str, asin_prodotti: str) -> None:
        self.cursor.execute(
            "DELETE FROM Pubblica WHERE id = ? AND id_canale = ? AND asin_prodotti = ?", 
            (id, id_canale, asin_prodotti)
        )
        self.conn.commit()

    def get(self, id: int, id_canale: str, asin_prodotti: str) -> Pubblica:
        self.cursor.execute(
            "SELECT * FROM Pubblica WHERE id = ? AND id_canale = ? AND asin_prodotti = ?", 
            (id, id_canale, asin_prodotti)
        )
        row = self.cursor.fetchone()
        if row:
            return Pubblica(*row)
        return None
    
    def get_channel_link_non_pubblicati(self, id_canale: str) -> List[Pubblica]:
        self.cursor.execute(
            "SELECT * FROM Pubblica WHERE id_canale = ? AND isPubblicato = 0", 
            (id_canale,)
        )
        rows = self.cursor.fetchall()
        return [Pubblica(*row) for row in rows] 
    
    def get_channel_link_pubblicati(self, id_canale: str) -> List[Pubblica]:
        self.cursor.execute(
            "SELECT * FROM Pubblica WHERE id_canale = ? AND isPubblicato = 1", 
            (id_canale,)
        )
        rows = self.cursor.fetchall()
        return [Pubblica(*row) for row in rows]

    def get_all(self) -> List[Pubblica]:
        self.cursor.execute("SELECT * FROM Pubblica")
        rows = self.cursor.fetchall()
        return [Pubblica(*row) for row in rows] 

    def close(self) -> None:
        self.conn.close()

    def __get_next_id(self) -> int:
        self.cursor.execute("SELECT MAX(id) FROM Pubblica")
        result = self.cursor.fetchone()

        if result[0] is None:
            next_id = 1
        else:
            next_id = result[0] + 1

        return next_id