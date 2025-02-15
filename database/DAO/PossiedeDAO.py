from database import Connessione
from database.Entity import Possiede

class PossiedeDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def insert(self, possiede: Possiede):
        self.cursor.execute("INSERT INTO Possiede (canale_id, layout_id, in_uso) VALUES (?, ?, ?)",
                            (possiede.get_canale_id(), possiede.get_layout_id(), possiede.get_in_uso()))
        self.conn.commit()

    def update(self, possiede: Possiede):
        self.cursor.execute("UPDATE Possiede SET in_uso = ? WHERE canale_id = ? AND layout_id = ?",
                            (possiede.get_in_uso(), possiede.get_canale_id(), possiede.get_layout_id()))
        self.conn.commit()

    def delete(self, canale_id, layout_id):
        self.cursor.execute("DELETE FROM Possiede WHERE canale_id = ? AND layout_id = ?", 
                            (canale_id, layout_id))
        self.conn.commit()

    def get(self, canale_id, layout_id):
        self.cursor.execute("SELECT * FROM Possiede WHERE canale_id = ? AND layout_id = ?", 
                            (canale_id, layout_id))
        row = self.cursor.fetchone()
        if row:
            return Possiede(*row)
        return None

    def get_all(self):
        self.cursor.execute("SELECT * FROM Possiede")
        rows = self.cursor.fetchall()
        return [Possiede(*row) for row in rows]

    def close(self):
        self.conn.close()