from database.Connessione import get_db_connection


def check_license(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT telegram_id FROM Utenti WHERE telegram_id = ?', (user_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute('''
            INSERT INTO Utenti (telegram_id) 
            VALUES (?)
        ''', (user_id,))
        conn.commit()

    cursor.execute('''
        SELECT U.telegram_id
        FROM Utenti U
        JOIN Licenze L ON U.licenza_codice = L.codice_licenza
        WHERE U.telegram_id = ? AND L.descrizione = 'Attiva'
    ''', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    
    return user is not None

def addLicense(license):
    conn=get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Licenze (codice_licenza, descrizione) VALUES (?, ?)', (license, 'Attiva'))
    conn.commit()
    conn.close()

def getLicenses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT codice_licenza FROM Licenze')
    licenses = cursor.fetchall()
    conn.close()

    return licenses

def deleteLicense(license):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Licenze WHERE codice_licenza = ?', (license,))
    conn.commit()
    conn.close()


def getLicenseDetails(license_code):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT codice_licenza, descrizione FROM licenze WHERE codice_licenza = ?", (license_code,))

        license_details = cursor.fetchone()

        if license_details:
            return {'codice_licenza': license_details['codice_licenza'], 'stato': license_details['descrizione']}
        else:
            return None

    finally:
        conn.close()

def updateUserLicense(license_code,user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
                UPDATE Utenti SET licenza_codice = ? WHERE telegram_id = ?
            ''', (license_code, user_id))
    conn.commit()
    conn.close()