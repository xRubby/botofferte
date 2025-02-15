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

def add_link_to_channel(canale_id, url, messaggio):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM Links WHERE url = ? AND canale_id = ?', (url, canale_id))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO Links (url, canale_id, messaggio) VALUES (?, ?, ?)', (url, canale_id, messaggio))

    conn.commit()
    conn.close()

def remove_link_from_channel(link_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM Links WHERE id = ?
    ''', (link_id,))

    conn.commit()
    conn.close()

def get_channel_links(channel_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT *
    FROM Links
    WHERE canale_id = ?
    '''
    cursor.execute(query, (channel_id,))
    rows = cursor.fetchall()
    conn.close()

    return [Link(row['id'], row['url'], row['canale_id'], row['messaggio']) for row in rows]

def get_channel_links_by_id(channel_id: str, link_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT *
    FROM Links
    WHERE canale_id = ? AND id = ?
    '''
    cursor.execute(query, (channel_id, link_id,))
    row = cursor.fetchone()
    conn.close()

    return Link(row['id'], row['url'], row['canale_id'], row['messaggio'])