from database.Connessione import Connessione
from database.Entity.Canale import Canale



class CanaleDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def insert(self, canale_id, nome_canale, id_affiliato, codice_licenza, telegram_id):
        self.cursor.execute(
            "INSERT INTO canali (canale_id, nome_canale, id_affiliato, codice_licenza) VALUES (?, ?, ?, ?)", 
            (canale_id, nome_canale, id_affiliato, codice_licenza)
        )
    
        self.cursor.execute(
            "INSERT INTO Gestisce (telegram_id, canale_id) VALUES (?, ?)", 
            (telegram_id, canale_id)
        )

        self.conn.commit()

    def update(self, canale_id, nome_canale, id_affiliato, codice_licenza):
        self.cursor.execute("UPDATE canali SET nome_canale = ?, id_affiliato = ?, codice_licenza = ? WHERE canale_id = ?", 
                            (canale_id, nome_canale, id_affiliato, codice_licenza))
        self.conn.commit()

    def delete(self, canale_id):
        self.cursor.execute("DELETE FROM canali WHERE canale_id = ?", (canale_id,))
        self.conn.commit()

    def get(self, canale_id):
        self.cursor.execute("SELECT * FROM canali WHERE canale_id = ?", (canale_id,))
        row = self.cursor.fetchone()
        if row:
            return Canale(*row)
        return None
    
    def get_user_channels(self, user_id):
        self.cursor.execute("""SELECT c.* FROM Canali c JOIN Gestisce g ON c.canale_id = g.canale_id
        WHERE g.telegram_id = ?""", (user_id,))
        rows = self.cursor.fetchall()
        print(rows) 

        return [Canale(*row) for row in rows] 
    
    def is_license_used(self, license_code):
        self.cursor.execute("SELECT * FROM canali WHERE codice_licenza = ? LIMIT 1", (license_code,))
        return self.cursor.fetchone() is not None

    def get_all(self):
        self.cursor.execute("SELECT * FROM canali")
        rows = self.cursor.fetchall()

        return [Canale(*row) for row in rows] 
    
    
    def close(self):
        self.conn.close()


def get_user_channels(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    SELECT *
    FROM Canali AS C
    INNER JOIN Utenti_Canali AS UC ON C.id = UC.canale_id
    WHERE UC.telegram_id = ?
    '''
    cursor.execute(query, (user_id,))
    channels = cursor.fetchall()
    conn.close()

    return [Canale(row['id'],row['nome_canale'], row['messaggio'], row['id_affiliato']) for row in channels]

def add_channel_to_db(user_id, channel_id, channel_name, message):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM Canali WHERE id = ?
    ''', (channel_id,))
    existing_channel = cursor.fetchone()

    if not existing_channel:
        cursor.execute('''
            INSERT INTO Canali (id, nome_canale, messaggio) VALUES (?, ?, ?)
        ''', (channel_id, channel_name, message))

    cursor.execute('''
        INSERT OR IGNORE INTO Utenti_Canali (telegram_id, canale_id)
        VALUES (?, ?)
    ''', (user_id, channel_id))

    conn.commit()
    conn.close()

def remove_channel_from_user(user_id, channel_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM Utenti_Canali WHERE telegram_id = ? AND canale_id = ?
    ''', (user_id, channel_id))

    conn.commit()
    conn.close()

def remove_channel_from_db(channel_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Canali WHERE id = ?", (channel_id,))
    connection.commit()
    connection.close()

def set_message_template(channel_id, message):
    conn = get_db_connection()
    cursor = conn.cursor()

    print(channel_id)
    print(message)

    cursor.execute('''
        UPDATE Canali SET messaggio = ? WHERE id = ?
    ''', (message,channel_id,))

    conn.commit()
    conn.close()

def get_message_template(channel_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT messaggio FROM Canali WHERE id = ?
    ''', (channel_id,))
    message = cursor.fetchone()

    conn.close()

    return message['messaggio'] if message else None

def set_affiliate_id(channel_id, affiliate_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE Canali SET id_affiliato = ? WHERE id = ?
    ''', (affiliate_id, channel_id))

    conn.commit()
    conn.close()

def get_affiliate_id(channel_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id_affiliato FROM Canali WHERE id = ?
    ''', (channel_id,))
    affiliate_id = cursor.fetchone()

    conn.close()

    return affiliate_id['id_affiliato'] if affiliate_id else None

def get_channel(channel_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM Canali WHERE id = ?
    ''', (channel_id,))
    channel = cursor.fetchone()

    conn.close()

    if(channel):
        return Canale(channel['id'], channel['nome_canale'], channel['messaggio'], channel['id_affiliato'])

    return None