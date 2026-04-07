from database.Connessione import Connessione
from database.Entity.Licenza import Licenza

from database.DAO.CanaleDAO import CanaleDAO

from utils.generate_license import calcola_data_scadenza

from datetime import datetime

class LicenzaDAO:
    def insert(self, codice_licenza: str, tipo: str) -> None:
        with Connessione() as con:
            con.execute("INSERT INTO licenze (codice_licenza, tipo) VALUES (?, ?)", 
                            (codice_licenza, tipo))

    def update(self, codice_licenza: str, tipo: str, data_attivazione: str, data_scadenza: str) -> None:
        with Connessione() as con:
            con.execute("UPDATE licenze SET tipo = ?, data_attivazione = ?, data_scadenza = ? WHERE codice_licenza = ?", 
                            (tipo, data_attivazione, data_scadenza, codice_licenza))

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

        with Connessione() as con:
            con.execute("DELETE FROM licenze WHERE codice_licenza = ?", (codice_licenza,))

    def get(self, codice_licenza) -> Licenza | None:
        with Connessione() as con:
            row = con.execute("SELECT * FROM licenze WHERE codice_licenza = ?", (codice_licenza,)).fetchone()
            return Licenza(*row) if row else None
    
    def get_stato(self, codice_licenza: str) -> bool:
        with Connessione() as con:
            row = con.execute("""
            SELECT data_attivazione, data_scadenza FROM Licenze WHERE codice_licenza = ?
            """, (codice_licenza,)).fetchone()

        if row is None:
            return False

        data_attivazione, data_scadenza = row

        if data_attivazione is None:
            return False
        if data_scadenza is None or datetime.strptime(data_scadenza, "%Y-%m-%d %H:%M:%S") >= datetime.now():
            return True

        return False

    def get_all(self) -> list[Licenza]:
        with Connessione() as con:
            rows = con.execute("SELECT * FROM licenze").fetchall()
            return [Licenza(*row) for row in rows] 