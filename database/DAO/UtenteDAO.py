from database.Connessione import Connessione
from database.Entity.Utente import Utente

class UtenteDAO:
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
        raise RuntimeError("UtenteDAO deve essere usato dentro un blocco 'with'")

    def insert(self, telegram_id: int, nome: str, isAdmin: bool = False) -> None:
        self._get_con().execute(
            "INSERT INTO utenti (telegram_id, nome, isAdmin) VALUES (?, ?, ?)",
            (telegram_id, nome, isAdmin)
        )

    def update(self, telegram_id: int, nome: str, isAdmin: bool) -> None:
        self._get_con().execute(
            "UPDATE utenti SET nome = ?, isAdmin = ? WHERE telegram_id = ?",
            (nome, isAdmin, telegram_id)
        )

    def delete(self, telegram_id: int) -> None:
        self._get_con().execute(
            "DELETE FROM utenti WHERE telegram_id = ?", (telegram_id,)
        )

    def get(self, telegram_id: int) -> Utente | None:
        row = self._get_con().execute(
            "SELECT * FROM utenti WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        return Utente(*row) if row else None

    def get_all(self) -> list[Utente]:
        rows = self._get_con().execute("SELECT * FROM utenti").fetchall()
        return [Utente(*row) for row in rows]