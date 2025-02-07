import sqlite3

def get_db_connection():
    conn = sqlite3.connect('amazon_offers.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Licenze (
        codice_licenza TEXT PRIMARY KEY,
        descrizione TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Canali (
        id TEXT PRIMARY KEY,
        nome_canale TEXT NOT NULL,
        messaggio TEXT,
        id_affiliato VARCHAR(300)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Utenti (
        telegram_id INTEGER PRIMARY KEY,
        licenza_codice TEXT,
        isAdmin BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (licenza_codice) REFERENCES Licenze(codice_licenza)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Utenti_Canali (
        telegram_id INTEGER,
        canale_id TEXT,
        PRIMARY KEY (telegram_id, canale_id),
        FOREIGN KEY (telegram_id) REFERENCES Utenti(telegram_id),
        FOREIGN KEY (canale_id) REFERENCES Canali(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    canale_id INTEGER NOT NULL,
    messaggio VARCHAR(500),
    FOREIGN KEY (canale_id) REFERENCES Canali(id)
    )
    ''')

    conn.commit()
    conn.close()