from database.Connessione import Connessione
from database.Entity.Canale import Canale

class CanaleDAO:
    def __init__(self):
        self._con = None

    def __enter__(self):
        self._con = Connessione().__enter__()  # apre la connessione
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._con.commit()
        else:
            self._con.rollback()
        self._con.close()
        return False

    def insert(self, canale_id: str, nome_canale: str, id_affiliato: str, codice_licenza: str) -> None:
        self._con.execute(
            "INSERT INTO canali (canale_id, nome_canale, id_affiliato, codice_licenza) VALUES (?, ?, ?, ?)",
            (canale_id, nome_canale, id_affiliato, codice_licenza)
        )

    def update(self, canale_id: str, nome_canale: str, id_affiliato: str, codice_licenza: str) -> None:
        self._con.execute(
            "UPDATE canali SET nome_canale = ?, id_affiliato = ?, codice_licenza = ? WHERE canale_id = ?",
            (nome_canale, id_affiliato, codice_licenza, canale_id)
        )

    def delete(self, canale_id: str) -> None:
        self._con.execute(
            "DELETE FROM canali WHERE canale_id = ?", (canale_id,)
        )

    def get(self, canale_id: str) -> Canale | None:
        row = self._con.execute(
            "SELECT * FROM canali WHERE canale_id = ?", (canale_id,)
        ).fetchone()
        return Canale(*row) if row else None

    def get_all(self) -> list[Canale]:
        rows = self._con.execute("SELECT * FROM canali").fetchall()
        return [Canale(*row) for row in rows]