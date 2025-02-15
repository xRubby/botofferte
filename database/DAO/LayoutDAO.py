from database.Connessione import Connessione
from database.Entity.Layout import Layout

class LayoutDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self) -> 'LayoutDAO':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.conn.close()

    def insert(self, nome_layout: str, messaggio: str) -> None:
        self.cursor.execute("INSERT INTO Layout (nome_layout, messaggio) VALUES (?, ?)",
                            (nome_layout, messaggio))
        self.conn.commit()

    def update(self, layout_id: int, nome_layout: str, messaggio: str) -> None:
        self.cursor.execute("UPDATE Layout SET nome_layout = ?, messaggio = ? WHERE layout_id = ?",
                            (nome_layout, messaggio, layout_id))
        self.conn.commit()

    def delete(self, layout_id: int) -> None:
        self.cursor.execute("DELETE FROM Layout WHERE layout_id = ?", (layout_id,))
        self.conn.commit()

    def get(self, layout_id: int) -> Layout:
        self.cursor.execute("SELECT * FROM Layout WHERE layout_id = ?", (layout_id,))
        row = self.cursor.fetchone()
        if row:
            return Layout(*row)
        return None

    def get_all(self) -> list:
        self.cursor.execute("SELECT * FROM Layout")
        rows = self.cursor.fetchall()
        return [Layout(*row) for row in rows]

    def close(self) -> None:
        self.conn.close()