from database.Connessione import get_db_connection
from database.Entity.Link import *


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