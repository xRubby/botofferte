from database.Connessione import Connessione
from database.Entity.Licenza import Licenza

from database.DAO.CanaleDAO import CanaleDAO

from utils.generate_license import calcola_data_scadenza

from typing import List
from datetime import datetime

class LicenzaDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self) -> 'LicenzaDAO':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.conn.close()

    def insert(self, codice_licenza: str, tipo: str) -> None:
        self.cursor.execute("INSERT INTO licenze (codice_licenza, tipo) VALUES (?, ?)", 
                            (codice_licenza, tipo))
        self.conn.commit()

    def update(self, codice_licenza: str, tipo: str, data_attivazione: str, data_scadenza: str) -> None:
        self.cursor.execute("UPDATE licenze SET tipo = ?, data_attivazione = ?, data_scadenza = ? WHERE codice_licenza = ?", 
                            (tipo, data_attivazione, data_scadenza, codice_licenza))
        self.conn.commit()

    def activate_licenza(self, codice_licenza: str) -> bool:
        licenza = self.get(codice_licenza)

        if not licenza:
            return False

        if licenza.data_attivazione is not None:
            return False

        data_attivazione = datetime.now()
        data_scadenza = calcola_data_scadenza(licenza.tipo, data_attivazione)

        self.update(codice_licenza, licenza.tipo, data_attivazione.strftime("%Y-%m-%d %H:%M:%S"), data_scadenza)

        return True

    def delete(self, codice_licenza) -> None:

        with CanaleDAO() as canale_dao:
            canale = canale_dao.get_channel_by_licensecode(codice_licenza)
            if canale:
                canale_dao.update_codice_licenza(canale.canale_id, "")

        self.cursor.execute("DELETE FROM licenze WHERE codice_licenza = ?", (codice_licenza,))
        self.conn.commit()

    def get(self, codice_licenza) -> Licenza:
        self.cursor.execute("SELECT * FROM licenze WHERE codice_licenza = ?", (codice_licenza,))
        row = self.cursor.fetchone()
        if row:
            return Licenza(*row)
        return None
    
    def get_stato(self, codice_licenza: str) -> bool:
        self.cursor.execute("""
            SELECT data_attivazione, data_scadenza FROM Licenze WHERE codice_licenza = ?
            """, (codice_licenza,))
    
        result = self.cursor.fetchone()

        if result is None:
            return False

        data_attivazione, data_scadenza = result

        if data_attivazione is None:
            return False
        if data_scadenza is None or datetime.strptime(data_scadenza, "%Y-%m-%d %H:%M:%S") >= datetime.now():
            return True

        return False

    def get_all(self) -> List[Licenza]:
        self.cursor.execute("SELECT * FROM licenze")

        rows = self.cursor.fetchall()

        return [Licenza(*row) for row in rows] 
    
    def close(self) -> None:
        self.conn.close()