from database.Connessione import Connessione
from database.Entity.Utente import Utente


class UtenteDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self) -> 'UtenteDAO':
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.conn.close()

    def insert(self, telegram_id: int, nome: str, isAdmin: bool = 0) -> None:
        self.cursor.execute("INSERT INTO utenti (telegram_id, nome, isAdmin) VALUES (?, ?, ?)", 
                            (telegram_id, nome, isAdmin))
        self.conn.commit()

    def update(self, telegram_id: int, nome: str, isAdmin: bool) -> None:
        self.cursor.execute("UPDATE utenti SET nome = ?, isAdmin = ? WHERE telegram_id = ?", 
                            (nome, isAdmin, telegram_id))
        self.conn.commit()

    def delete(self, telegram_id) -> None:
        self.cursor.execute("DELETE FROM utenti WHERE telegram_id = ?", (telegram_id,))
        self.conn.commit()

    def get(self, telegram_id) -> Utente:
        self.cursor.execute("SELECT * FROM utenti WHERE telegram_id = ?", (telegram_id,))

        row = self.cursor.fetchone()

        if row:
            return Utente(*row)
        return None

    def get_all(self) -> list:
        self.cursor.execute("SELECT * FROM utenti")

        rows = self.cursor.fetchall()
        return [Utente(*row) for row in rows] 
    
    def close(self) -> None:
        self.conn.close()
