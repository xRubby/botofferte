from database.Connessione import get_db_connection
from database.Entity.Canale import Canale


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