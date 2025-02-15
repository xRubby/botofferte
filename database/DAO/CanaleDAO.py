from database.Connessione import Connessione
from database.Entity.Canale import Canale



class CanaleDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def insert(self, canale_id, nome_canale, id_affiliato, codice_licenza):
        self.cursor.execute(
            "INSERT INTO canali (canale_id, nome_canale, id_affiliato, codice_licenza) VALUES (?, ?, ?, ?)", 
            (canale_id, nome_canale, id_affiliato, codice_licenza)
        )

        self.conn.commit()

    def update(self, canale_id, nome_canale, id_affiliato, codice_licenza):
        self.cursor.execute("UPDATE canali SET nome_canale = ?, id_affiliato = ?, codice_licenza = ? WHERE canale_id = ?", 
                            (canale_id, nome_canale, id_affiliato, codice_licenza))
        self.conn.commit()

    def delete(self, canale_id):
        self.cursor.execute("DELETE FROM canali WHERE canale_id = ?", (canale_id,))
        self.conn.commit()

    def get(self, canale_id):
        self.cursor.execute("SELECT * FROM canali WHERE canale_id = ?", (canale_id,))
        row = self.cursor.fetchone()
        if row:
            return Canale(*row)
        return None
    
    def get_user_channels(self, user_id):
        self.cursor.execute("""SELECT c.* FROM Canali c JOIN Gestisce g ON c.canale_id = g.canale_id
        WHERE g.telegram_id = ?""", (user_id,))
        rows = self.cursor.fetchall()

        return [Canale(*row) for row in rows] 
    
    def is_license_used(self, license_code):
        self.cursor.execute("SELECT * FROM canali WHERE codice_licenza = ? LIMIT 1", (license_code,))
        return self.cursor.fetchone() is not None

    def get_all(self):
        self.cursor.execute("SELECT * FROM canali")
        rows = self.cursor.fetchall()

        return [Canale(*row) for row in rows] 
    
    
    def close(self):
        self.conn.close()