from database.Connessione import Connessione
from database.Entity.Canale import Canale

from typing import List


class CanaleDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self) -> 'CanaleDAO':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.conn.close()

    def insert(self, canale_id: str, nome_canale: str, id_affiliato: str, codice_licenza: str) -> None:
        self.cursor.execute(
            "INSERT INTO canali (canale_id, nome_canale, id_affiliato, codice_licenza) VALUES (?, ?, ?, ?)", 
            (canale_id, nome_canale, id_affiliato, codice_licenza)
        )

        self.conn.commit()

    def update(self, canale_id: str, nome_canale: str, id_affiliato: str, codice_licenza: str) -> None:
        self.cursor.execute("UPDATE canali SET nome_canale = ?, id_affiliato = ?, codice_licenza = ? WHERE canale_id = ?", 
                            (canale_id, nome_canale, id_affiliato, codice_licenza))
        self.conn.commit()

    def update_id_affiliato(self, canale_id: str, new_id_affiliato: str) -> None:
        self.cursor.execute("UPDATE canali SET id_affiliato = ? WHERE canale_id = ?", 
                            (new_id_affiliato, canale_id))
        self.conn.commit()

    def update_codice_licenza(self, canale_id: str, new_codice_licenza: str) -> None:
        self.cursor.execute("UPDATE canali SET codice_licenza = ? WHERE canale_id = ?", 
                            (new_codice_licenza, canale_id))
        self.conn.commit()

    def delete(self, canale_id: str) -> None:
        self.cursor.execute("DELETE FROM canali WHERE canale_id = ?", (canale_id,))
        self.conn.commit()

    def get(self, canale_id: str) -> Canale:
        self.cursor.execute("SELECT * FROM canali WHERE canale_id = ?", (canale_id,))
        row = self.cursor.fetchone()
        if row:
            return Canale(*row)
        return None
    
    def get_user_channels(self, user_id: int) -> List[Canale]:
        self.cursor.execute("""SELECT c.* FROM Canali c JOIN Gestisce g ON c.canale_id = g.canale_id
        WHERE g.telegram_id = ?""", (user_id,))
        rows = self.cursor.fetchall()

        return [Canale(*row) for row in rows] 
    
    def get_channel_by_licensecode(self, license_code) -> Canale:
        self.cursor.execute("SELECT * FROM canali WHERE codice_licenza = ? LIMIT 1", (license_code,))
        row = self.cursor.fetchone()
        if row:
            return Canale(*row)
        return None
    
    def is_license_used(self, license_code: str) -> bool:
        self.cursor.execute("SELECT * FROM canali WHERE codice_licenza = ? LIMIT 1", (license_code,))
        return self.cursor.fetchone() is not None

    def get_all(self) -> List[Canale]:
        self.cursor.execute("SELECT * FROM canali")
        rows = self.cursor.fetchall()

        return [Canale(*row) for row in rows] 
    
    
    def close(self) -> None:
        self.conn.close()