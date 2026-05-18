from database.Connessione import Connessione
from database.Entity.Tastiera import Tastiera

class TastieraDAO:
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
        raise RuntimeError("TastieraDAO deve essere usato dentro un blocco 'with'")

    def insert(self, nome_tastiera: str, messaggio: str, in_uso: bool, canale_id: str) -> None:
        self._get_con().execute(
            "INSERT INTO Tastiere (nome_tastiera, messaggio, in_uso, canale_id) VALUES (?, ?, ?, ?)",
            (nome_tastiera, messaggio, in_uso, canale_id)
        )

    def update(self, layout_id: int, nome_tastiera: str, messaggio: str, in_uso: bool, canale_id: str) -> None:
        self._get_con().execute(
            "UPDATE Tastiere SET nome_tastiera = ?, messaggio = ?, in_uso = ?, canale_id = ? WHERE layout_id = ?",
            (nome_tastiera, messaggio, in_uso, canale_id, layout_id)
        )

    def update_stato(self, tastiera_id: int, in_uso: bool) -> None:
        self._get_con().execute(
            "UPDATE Tastiere SET in_uso = ? WHERE tastiera_id = ?",
            (in_uso, tastiera_id,)
        )

    def update_messaggio(self, tastiera_id: int, messaggio: str) -> None:
        self._get_con().execute(
            "UPDATE Tastiere SET messaggio = ? WHERE tastiera_id = ?",
            (messaggio, tastiera_id,)
        )

    def delete(self, tastiera_id: int) -> None:
        self._get_con().execute(
            "DELETE FROM Tastiere WHERE tastiera_id = ?", (tastiera_id,)
        )

    def get(self, tastiera_id: int) -> Tastiera | None:
        row = self._get_con().execute(
            "SELECT * FROM Tastiere WHERE tastiera_id = ?", (tastiera_id,)
        ).fetchone()
        return Tastiera(*row) if row else None
    
    def get_channel_keyboards(self, canale_id: str) -> Tastiera | None:
        rows = self._get_con().execute(
            "SELECT * FROM Tastiere WHERE canale_id = ?", (canale_id,)
        ).fetchall()
        return [Tastiera(*row) for row in rows]

    def get_all(self) -> list[Tastiera]:
        rows = self._get_con().execute("SELECT * FROM Tastiere").fetchall()
        return [Tastiera(*row) for row in rows]
    
    def get_in_uso(self, canale_id: str) ->Tastiera | None:
        row = self._get_con().execute(
            "SELECT * FROM Tastiere WHERE in_uso = 1 AND canale_id = ?", (canale_id,)
        ).fetchone()
        return Tastiera(*row) if row else None