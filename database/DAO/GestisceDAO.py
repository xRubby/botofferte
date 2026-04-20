from database.Connessione import Connessione
from database.Entity.Gestisce import Gestisce

class GestisceDAO:
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
        raise RuntimeError("GestisceDAO deve essere usato dentro un blocco 'with'")

    def insert(self, telegram_id: int, canale_id: str, id_affiliato: str, isCreator: bool = False) -> None:
        self._get_con().execute(
            "INSERT INTO Gestisce (telegram_id, canale_id, id_affiliato, isCreator) VALUES (?, ?, ?, ?)",
            (telegram_id, canale_id, id_affiliato, isCreator)
        )

    def update(self, telegram_id: int, canale_id: str, id_affiliato: str, isCreator: bool) -> None:
        self._get_con().execute(
            "UPDATE Gestisce SET id_affiliato = ?, isCreator = ? WHERE telegram_id = ? AND canale_id = ?",
            (id_affiliato, isCreator, telegram_id, canale_id)
        )

    def update_idaffiliato(self, telegram_id: int, canale_id: str, id_affiliato: str,) -> None:
        self._get_con().execute(
            "UPDATE Gestisce SET id_affiliato = ? WHERE telegram_id = ? AND canale_id = ?",
            (id_affiliato, telegram_id, canale_id)
        )

    def delete(self, telegram_id: int, canale_id: str) -> None:
        self._get_con().execute(
            "DELETE FROM Gestisce WHERE telegram_id = ? AND canale_id = ?",
            (telegram_id, canale_id)
        )

    def get(self, telegram_id: int, canale_id: str) -> Gestisce | None:
        row = self._get_con().execute(
            "SELECT * FROM Gestisce WHERE telegram_id = ? AND canale_id = ?",
            (telegram_id, canale_id)
        ).fetchone()
        return Gestisce(*row) if row else None

    def get_all(self) -> list[Gestisce]:
        rows = self._get_con().execute(
            "SELECT * FROM Gestisce"
        ).fetchall()
        return [Gestisce(*row) for row in rows]