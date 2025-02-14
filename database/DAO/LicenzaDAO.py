from database.Connessione import Connessione
from database.Entity.Licenza import Licenza


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

class LicenzaDAO:
    def __init__(self):
        self.conn = Connessione().get_connection()
        self.cursor = self.conn.cursor()

    def insert(self, licenza: Licenza):
        self.cursor.execute("INSERT INTO licenze (codice_licenza, scadenza, stato) VALUES (?, ?, ?)", 
                            (licenza.getCodiceLicenza(), licenza.getScadenza(), licenza.getStato()))
        self.conn.commit()

    def update(self, licenza: Licenza):
        self.cursor.execute("UPDATE licenze SET scadenza = ?, stato = ? WHERE codice_licenza = ?", 
                            (licenza.getScadenza(), licenza.getStato(), licenza.getCodiceLicenza()))
        self.conn.commit()

    def delete(self, codice_licenza):
        self.cursor.execute("DELETE FROM licenze WHERE codice_licenza = ?", (codice_licenza,))
        self.conn.commit()

    def get(self, codice_licenza):
        self.cursor.execute("SELECT * FROM licenze WHERE codice_licenza = ?", (codice_licenza,))
        row = self.cursor.fetchone()
        if row:
            return Licenza(*row)
        return None

    def get_all(self):
        self.cursor.execute("SELECT * FROM licenze")

        rows = self.cursor.fetchall()

        return [Licenza(*row) for row in rows] 
    
    def close(self):
        self.conn.close()