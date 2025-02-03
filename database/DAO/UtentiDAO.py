from database.Connessione import get_db_connection


def isAdmin(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM Utenti WHERE telegram_id = ? and isAdmin = 1
    ''', (user_id,))

    admin = cursor.fetchone()

    conn.close()

    return admin is not None
