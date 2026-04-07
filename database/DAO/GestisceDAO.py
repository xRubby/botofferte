from database.Connessione import Connessione
from database.Entity.Gestisce import Gestisce

class GestisceDAO:
    def insert(self, telegram_id: int, canale_id: str, id_affiliato: str, isCreator: bool = 0) -> None:
        with Connessione() as con:
            con.execute(
            "INSERT INTO Gestisce (telegram_id, canale_id, id_affiliato, isCreator) VALUES (?, ?, ?, ?)", 
            (telegram_id, canale_id, id_affiliato, isCreator)
        )

    def update(self, telegram_id: int, canale_id: str, id_affiliato: str, isCreator: bool) -> None:
        with Connessione() as con:
            con.execute("UPDATE Gestisce SET telegram_id = ?, canale_id = ?, id_affiliato = ?, isCreator = ? WHERE telegram_id = ? and canale_id = ?", 
                            (telegram_id, canale_id, id_affiliato, isCreator, telegram_id, canale_id,))

    def delete(self, telegram_id: int, canale_id: str) -> None:
        with Connessione() as con:
            con.execute("DELETE FROM Gestisce WHERE telegram_id = ? AND canale_id = ?", (telegram_id, canale_id,))

    def get(self, telegram_id: int, canale_id: str) -> Gestisce | None:
        with Connessione() as con:
            row = con.execute("SELECT * FROM Gestisce WHERE telegram_id = ? AND canale_id = ?", (telegram_id, canale_id,)).fetchone()
            return Gestisce(*row) if row else None

    def get_all(self) -> list[Gestisce]:
        with Connessione() as con:
            rows = con.execute("SELECT * FROM Gestisce").fetchall
            return [Gestisce(*row) for row in rows] 