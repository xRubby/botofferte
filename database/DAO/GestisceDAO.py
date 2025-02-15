from database import Connessione
from database.Entity import Gestisce



class GestisceDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def insert(self, telegram_id: int, canale_id: str, id_affiliato: str, isCreator: bool = 0):
        self.cursor.execute(
            "INSERT INTO Gestisce (telegram_id, canale_id, id_affiliato, isCreator) VALUES (?, ?, ?, ?)", 
            (telegram_id, canale_id, id_affiliato, isCreator)
        )
    
        self.conn.commit()

    def update(self, telegram_id: int, canale_id: str, id_affiliato: str, isCreator: bool):
        self.cursor.execute("UPDATE Gestisce SET telegram_id = ?, canale_id = ?, id_affiliato = ?, isCreator = ? WHERE telegram_id = ? and canale_id = ?", 
                            (telegram_id, canale_id, id_affiliato, isCreator, telegram_id, canale_id,))
        self.conn.commit()

    def update_id_affiliato(self, telegram_id: int, canale_id: str, new_id_affiliato: str):
        self.cursor.execute("UPDATE Gestisce SET id_affiliato = ? WHERE telegram_id = ? and canale_id = ?", 
                            (new_id_affiliato, telegram_id, canale_id,))
        self.conn.commit()

    def delete(self, telegram_id: int, canale_id: str):
        self.cursor.execute("DELETE FROM Gestisce WHERE telegram_id = ? AND canale_id = ?", (telegram_id, canale_id,))
        self.conn.commit()

    def get(self, telegram_id: int, canale_id: str):
        self.cursor.execute("SELECT * FROM Gestisce WHERE telegram_id = ? AND canale_id = ?", (telegram_id, canale_id,))
        row = self.cursor.fetchone()
        if row:
            return Gestisce(*row)
        return None

    def get_all(self):
        self.cursor.execute("SELECT * FROM Gestisce")
        rows = self.cursor.fetchall()

        return [Gestisce(*row) for row in rows] 
    
    
    def close(self):
        self.conn.close()