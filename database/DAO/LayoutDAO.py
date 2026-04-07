from database.Connessione import Connessione
from database.Entity.Layout import Layout

class LayoutDAO:
    def insert(self, nome_layout: str, messaggio: str, in_uso: bool, canale_id: str) -> None:
        with Connessione() as con:
            con.execute("INSERT INTO Layout (nome_layout, messaggio, in_uso, canale_id) VALUES (?, ?, ?, ?)",
                            (nome_layout, messaggio, in_uso, canale_id))

    def update(self, layout_id: int, nome_layout: str, messaggio: str, in_uso: bool, canale_id: str) -> None:
        with Connessione() as con:
            con.execute("UPDATE Layout SET nome_layout = ?, messaggio = ?, in_uso = ?, canale_id = ? WHERE layout_id = ?",
                            (nome_layout, messaggio, in_uso, canale_id, layout_id))

    def delete(self, layout_id: int) -> None:
        with Connessione() as con:
            con.execute("DELETE FROM Layout WHERE layout_id = ?", (layout_id,))

    def get(self, layout_id: int) -> Layout | None:
        with Connessione() as con:
            row = con.execute("SELECT * FROM Layout WHERE layout_id = ?", (layout_id,)).fetchone()
            return Layout(*row) if row else None

    def get_all(self) -> list[Layout]:
        with Connessione() as con:
            rows = con.execute("SELECT * FROM Layout").fetchall()
            return [Layout(*row) for row in rows]