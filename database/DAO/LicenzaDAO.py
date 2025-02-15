from database.Connessione import Connessione
from database.Entity.Licenza import Licenza

class LicenzaDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self) -> 'LicenzaDAO':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.conn.close()

    def insert(self, codice_licenza: str, scadenza: str, stato: bool = 1) -> None:
        self.cursor.execute("INSERT INTO licenze (codice_licenza, scadenza, stato) VALUES (?, ?, ?)", 
                            (codice_licenza, scadenza, stato))
        self.conn.commit()

    def update(self, codice_licenza: str, scadenza: str, stato: bool) -> None:
        self.cursor.execute("UPDATE licenze SET scadenza = ?, stato = ? WHERE codice_licenza = ?", 
                            (scadenza, stato, codice_licenza))
        self.conn.commit()

    def delete(self, codice_licenza) -> None:
        self.cursor.execute("DELETE FROM licenze WHERE codice_licenza = ?", (codice_licenza,))
        self.conn.commit()

    def get(self, codice_licenza) -> Licenza:
        self.cursor.execute("SELECT * FROM licenze WHERE codice_licenza = ?", (codice_licenza,))
        row = self.cursor.fetchone()
        if row:
            return Licenza(*row)
        return None

    def get_all(self) -> list:
        self.cursor.execute("SELECT * FROM licenze")

        rows = self.cursor.fetchall()

        return [Licenza(*row) for row in rows] 
    
    def close(self) -> None:
        self.conn.close()