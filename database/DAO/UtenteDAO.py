from database.Connessione import Connessione
from database.Entity.Utente import Utente

class UtenteDAO:
    def insert(self, telegram_id: int, nome: str, isAdmin: bool = 0) -> None:
        with Connessione() as con:
            con.execute("INSERT INTO utenti (telegram_id, nome, isAdmin) VALUES (?, ?, ?)", 
                            (telegram_id, nome, isAdmin))

    def update(self, telegram_id: int, nome: str, isAdmin: bool) -> None:
        with Connessione() as con:
            con.execute("UPDATE utenti SET nome = ?, isAdmin = ? WHERE telegram_id = ?", 
                            (nome, isAdmin, telegram_id))

    def delete(self, telegram_id) -> None:
        with Connessione() as con:
            con.execute("DELETE FROM utenti WHERE telegram_id = ?", (telegram_id,))

    def get(self, telegram_id) -> Utente | None:
        with Connessione() as con:
            row = con.execute("SELECT * FROM utenti WHERE telegram_id = ?", (telegram_id,))
            return Utente(*row) if row else None

    def get_all(self) -> list[Utente]:
        with Connessione() as con:
            rows = con.execute("SELECT * FROM utenti").fetchall()
            return [Utente(*row) for row in rows] 
