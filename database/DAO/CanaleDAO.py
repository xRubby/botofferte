from database.Connessione import Connessione
from database.Entity.Canale import Canale

class CanaleDAO:
    def insert(self, canale_id: str, nome_canale: str, id_affiliato: str, codice_licenza: str) -> None:
        with Connessione() as con:
            con.execute(
                "INSERT INTO canali (canale_id, nome_canale, id_affiliato, codice_licenza) VALUES (?, ?, ?, ?)", 
                (canale_id, nome_canale, id_affiliato, codice_licenza)
            )

    def update(self, canale_id: str, nome_canale: str, id_affiliato: str, codice_licenza: str) -> None:
        with Connessione() as con:
            con.execute("UPDATE canali SET nome_canale = ?, id_affiliato = ?, codice_licenza = ? WHERE canale_id = ?", 
                            (canale_id, nome_canale, id_affiliato, codice_licenza))

    def delete(self, canale_id: str) -> None:
        with Connessione() as con:
            con.execute("DELETE FROM canali WHERE canale_id = ?", (canale_id,))

    def get(self, canale_id: str) -> Canale | None:
        with Connessione() as con:
            row = con.execute("SELECT * FROM canali WHERE canale_id = ?", (canale_id,)).fetchone()
            return Canale(*row) if row else None

    def get_all(self) -> list[Canale]:
        with Connessione() as con:
            rows = con.execute("SELECT * FROM canali").fetchall()
            return [Canale(*row) for row in rows]