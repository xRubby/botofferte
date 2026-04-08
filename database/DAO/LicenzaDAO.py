from database.Connessione import Connessione
from database.Entity.Licenza import Licenza
from database.DAO.CanaleDAO import CanaleDAO
from utils.StatoLicenza import StatoLicenza
from utils.generate_license import calcola_data_scadenza
from datetime import datetime

class LicenzaDAO:
    def __init__(self):
        self._con = None

    def __enter__(self):
        self._connessione = Connessione()
        self._con = self._connessione.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._connessione.__exit__(exc_type, exc_val, exc_tb)

    def _get_con(self):
        if self._con is not None:
            return self._con
        raise RuntimeError("LicenzaDAO deve essere usato dentro un blocco 'with'")

    def insert(self, codice_licenza: str, tipo: str) -> None:
        self._get_con().execute(
            "INSERT INTO licenze (codice_licenza, tipo) VALUES (?, ?)",
            (codice_licenza, tipo)
        )

    def update(self, codice_licenza: str, tipo: str, data_attivazione: str, data_scadenza: str) -> None:
        self._get_con().execute(
            "UPDATE licenze SET tipo = ?, data_attivazione = ?, data_scadenza = ? WHERE codice_licenza = ?",
            (tipo, data_attivazione, data_scadenza, codice_licenza)
        )

    def activate_licenza(self, codice_licenza: str) -> bool:
        licenza = self.get(codice_licenza)
        if not licenza:
            return False
        if not licenza.attiva:
            return False
        if licenza.data_attivazione is not None:
            return False
        data_attivazione = datetime.now()
        data_scadenza = calcola_data_scadenza(licenza.tipo, data_attivazione)
        self.update(codice_licenza, licenza.tipo, data_attivazione.strftime("%Y-%m-%d %H:%M:%S"), data_scadenza)
        return True
    
    def attiva(self, codice_licenza: str) -> bool:
        affected = self._get_con().execute(
            "UPDATE licenze SET attiva = 1 WHERE codice_licenza = ?",
            (codice_licenza,)
        ).rowcount
        return affected > 0
    
    def disattiva(self, codice_licenza: str) -> bool:
        affected = self._get_con().execute(
            "UPDATE licenze SET attiva = 0 WHERE codice_licenza = ?",
            (codice_licenza,)
        ).rowcount
        return affected > 0

    def get(self, codice_licenza: str) -> Licenza | None:
        row = self._get_con().execute(
            "SELECT * FROM licenze WHERE codice_licenza = ?", (codice_licenza,)
        ).fetchone()
        return Licenza(*row) if row else None

    def get_stato(self, codice_licenza: str) -> bool:
        row = self._get_con().execute(
            "SELECT attiva, data_attivazione, data_scadenza FROM licenze WHERE codice_licenza = ?",
            (codice_licenza,)
        ).fetchone()
        if not row:
            return False
        attiva, data_attivazione, data_scadenza = row
        if not attiva or data_attivazione is None:
            return False
        if data_scadenza is None or datetime.strptime(data_scadenza, "%Y-%m-%d %H:%M:%S") >= datetime.now():
            return True
        return False

    def get_all(self) -> list[Licenza]:
        rows = self._get_con().execute("SELECT * FROM licenze").fetchall()
        return [Licenza(*row) for row in rows]
    
    def get_paginated(self, page: int, per_page: int) -> tuple[list[Licenza], int]:
        offset = page * per_page

        rows = self._get_con().execute("SELECT * FROM licenze LIMIT ? OFFSET ?",(per_page, offset)).fetchall()
        total = self._get_con().execute("SELECT COUNT(*) FROM licenze").fetchone()[0]

        return [Licenza(*row) for row in rows], total
    
    def get_dettagli(self, codice_licenza: str) -> tuple[Licenza | None, StatoLicenza | None, str | None, str | None]:
        row = self._get_con().execute("""
            SELECT l.codice_licenza, l.tipo, l.data_attivazione, l.data_scadenza, l.attiva,
                c.canale_id, c.nome_canale
            FROM licenze l
            LEFT JOIN canali c ON c.codice_licenza = l.codice_licenza
            WHERE l.codice_licenza = ?
        """, (codice_licenza,)).fetchone()

        if not row:
            return None, None, None, None

        licenza = Licenza(row[0], row[1], row[2], row[3], row[4])
        canale_id, nome_canale = row[5], row[6]

        if not licenza.attiva:
            stato = StatoLicenza.DISATTIVATA
        elif licenza.data_attivazione is None:
            stato = StatoLicenza.NON_ATTIVATA
        elif licenza.data_scadenza and datetime.strptime(licenza.data_scadenza, "%Y-%m-%d %H:%M:%S") < datetime.now():
            stato = StatoLicenza.SCADUTA
        else:
            stato = StatoLicenza.ATTIVA

        return licenza, stato, canale_id, nome_canale
    
    def release_licenza(self, codice_licenza: str) -> None:
        licenza = self.get(codice_licenza)
        if not licenza or licenza.data_scadenza is None:
            return

        now = datetime.now()
        scadenza = datetime.strptime(licenza.data_scadenza, "%Y-%m-%d %H:%M:%S")
    
        giorni_rimanenti = (scadenza - now).days
        if giorni_rimanenti <= 0:
            return

        nuovo_tipo = f"{giorni_rimanenti} giorni"
        self._get_con().execute(
            "UPDATE licenze SET tipo = ?, data_attivazione = NULL, data_scadenza = NULL WHERE codice_licenza = ?",
            (nuovo_tipo, codice_licenza)
    )