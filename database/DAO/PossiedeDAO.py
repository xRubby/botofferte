from database.Connessione import Connessione
from database.Entity.Possiede import Possiede

class PossiedeDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self) -> 'PossiedeDAO':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.conn.close()

    def insert(self, canale_id: int, layout_id: int, in_uso: bool = 0) -> None:
        self.cursor.execute("INSERT INTO Possiede (canale_id, layout_id, in_uso) VALUES (?, ?, ?)",
                            (canale_id, layout_id, in_uso))
        self.conn.commit()

    def update(self, canale_id: int, layout_id: int, in_uso: bool) -> None:
        self.cursor.execute("UPDATE Possiede SET in_uso = ? WHERE canale_id = ? AND layout_id = ?",
                            (in_uso, canale_id, layout_id))
        self.conn.commit()

    def delete(self, canale_id, layout_id) -> None:
        self.cursor.execute("DELETE FROM Possiede WHERE canale_id = ? AND layout_id = ?", 
                            (canale_id, layout_id))
        self.conn.commit()

    def get(self, canale_id, layout_id) -> Possiede:
        self.cursor.execute("SELECT * FROM Possiede WHERE canale_id = ? AND layout_id = ?", 
                            (canale_id, layout_id))
        row = self.cursor.fetchone()
        if row:
            return Possiede(*row)
        return None

    def get_all(self) -> list:
        self.cursor.execute("SELECT * FROM Possiede")
        rows = self.cursor.fetchall()
        return [Possiede(*row) for row in rows]

    def close(self) -> None:
        self.conn.close()