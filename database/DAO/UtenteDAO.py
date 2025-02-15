from database import Connessione
from database.Entity import Utente


class UtenteDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def insert(self, utente: Utente):
        self.cursor.execute("INSERT INTO utenti (telegram_id, nome, isAdmin) VALUES (?, ?, ?)", 
                            (utente.getTelegramId(), utente.getNome(), utente.getIsAdmin()))
        self.conn.commit()

    def update(self, utente: Utente):
        self.cursor.execute("UPDATE utenti SET nome = ?, isAdmin = ? WHERE telegram_id = ?", 
                            (utente.getNome(), utente.getIsAdmin(), utente.getTelegramId()))
        self.conn.commit()

    def delete(self, telegram_id):
        self.cursor.execute("DELETE FROM utenti WHERE telegram_id = ?", (telegram_id,))
        self.conn.commit()

    def get(self, telegram_id):
        self.cursor.execute("SELECT * FROM utenti WHERE telegram_id = ?", (telegram_id,))

        row = self.cursor.fetchone()

        if row:
            return Utente(*row)
        return None

    def get_all(self):
        self.cursor.execute("SELECT * FROM utenti")

        rows = self.cursor.fetchall()
        return [Utente(*row) for row in rows] 
    
    def close(self):
        self.conn.close()
