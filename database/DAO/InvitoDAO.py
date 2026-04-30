from database.Connessione import Connessione
from database.Entity.Invito import Invito

class InvitoDAO:
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
        raise RuntimeError("InvitoDAO deve essere usato dentro un blocco 'with'")

    def insert(self, token: str, data_creazione: float, canale_id: str) -> None:
        self._get_con().execute(
            "INSERT INTO Inviti (token, data_creazione, canale_id) VALUES (?, ?, ?)",
            (token, data_creazione, canale_id)
        )

    def update(self, token: str, data_creazione: float, canale_id: str) -> None:
        self._get_con().execute(
            "UPDATE Inviti SET data_creazione = ?, canale_id = ? WHERE token = ?",
            (data_creazione, canale_id, token)
        )

    def delete(self, token: str) -> None:
        self._get_con().execute(
            "DELETE FROM Inviti WHERE token = ?", (token,)
        )

    def get(self, token: str) -> Invito:
        row = self._get_con().execute(
            "SELECT * FROM Inviti WHERE token = ?", (token,)
        ).fetchone()
        return Invito(*row) if row else None
    
    def get_by_canale(self, canale_id: str) -> Invito:
        row = self._get_con().execute(
            "SELECT * FROM Inviti WHERE canale_id = ?", (canale_id,)
        ).fetchone()
        return Invito(*row) if row else None