from database.Connessione import Connessione
from database.Entity.Layout import Layout

class LayoutDAO:
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
        raise RuntimeError("LayoutDAO deve essere usato dentro un blocco 'with'")

    def insert(self, nome_layout: str, messaggio: str, in_uso: bool, canale_id: str) -> None:
        self._get_con().execute(
            "INSERT INTO Layout (nome_layout, messaggio, in_uso, canale_id) VALUES (?, ?, ?, ?)",
            (nome_layout, messaggio, in_uso, canale_id)
        )

    def update(self, layout_id: int, nome_layout: str, messaggio: str, in_uso: bool, canale_id: str) -> None:
        self._get_con().execute(
            "UPDATE Layout SET nome_layout = ?, messaggio = ?, in_uso = ?, canale_id = ? WHERE layout_id = ?",
            (nome_layout, messaggio, in_uso, canale_id, layout_id)
        )

    def delete(self, layout_id: int) -> None:
        self._get_con().execute(
            "DELETE FROM Layout WHERE layout_id = ?", (layout_id,)
        )

    def get(self, layout_id: int) -> Layout | None:
        row = self._get_con().execute(
            "SELECT * FROM Layout WHERE layout_id = ?", (layout_id,)
        ).fetchone()
        return Layout(*row) if row else None

    def get_all(self) -> list[Layout]:
        rows = self._get_con().execute("SELECT * FROM Layout").fetchall()
        return [Layout(*row) for row in rows]
    
    def get_in_uso(self, canale_id: str) -> Layout | None:
        row = self._get_con().execute(
            "SELECT * FROM Layout WHERE in_uso = 1 AND canale_id = ?", (canale_id,)
        ).fetchone()
        return Layout(*row) if row else None