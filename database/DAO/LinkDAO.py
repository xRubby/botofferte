from database.Connessione import Connessione
from database.Entity.Link import Link


class LinkDAO:
    def __init__(self):
        self.conn = Connessione.get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def insert(self, link: Link):
        self.cursor.execute("INSERT INTO links (url, id_canale) VALUES (?, ?)", 
                            (link.getUrl(), link.getIdCanale()))
        self.conn.close()

    def update(self, link: Link):
        self.cursor.execute("UPDATE links SET url = ?, id_canale = ? WHERE id = ?", 
                            (link.getUrl(), link.getIdCanale(), link.getId()))
        self.conn.close()

    def delete(self, link_id):
        self.cursor.execute("DELETE FROM links WHERE id = ?", (link_id,))
        self.conn.close()

    def get(self, link_id):
        self.cursor.execute("SELECT * FROM links WHERE id = ?", (link_id,))
        row = self.cursor.fetchone()
        if row:
            return Link(*row)
        return None

    def get_all(self):
        self.cursor.execute("SELECT * FROM links")
        rows = self.cursor.fetchall()

        return [Link(*row) for row in rows] 
    
    def close(self):
        self.conn.close()