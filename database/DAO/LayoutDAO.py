from database import Connessione
from database.Entity import Layout

class LayoutDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def insert(self, layout: Layout):
        self.cursor.execute("INSERT INTO Layout (nome_layout, messaggio) VALUES (?, ?)",
                            (layout.get_nome_layout(), layout.get_messaggio()))
        self.conn.commit()

    def update(self, layout: Layout):
        self.cursor.execute("UPDATE Layout SET nome_layout = ?, messaggio = ? WHERE layout_id = ?",
                            (layout.get_nome_layout(), layout.get_messaggio(), layout.get_layout_id()))
        self.conn.commit()

    def delete(self, layout_id):
        self.cursor.execute("DELETE FROM Layout WHERE layout_id = ?", (layout_id,))
        self.conn.commit()

    def get(self, layout_id):
        self.cursor.execute("SELECT * FROM Layout WHERE layout_id = ?", (layout_id,))
        row = self.cursor.fetchone()
        if row:
            return Layout(*row)
        return None

    def get_all(self):
        self.cursor.execute("SELECT * FROM Layout")
        rows = self.cursor.fetchall()
        return [Layout(*row) for row in rows]

    def close(self):
        self.conn.close()