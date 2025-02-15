import sqlite3

class Connessione:
    def __init__(self, db_name='amazon_offers.db'):
        self.db_name = db_name
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        
        conn.row_factory = sqlite3.Row

        conn.execute("PRAGMA foreign_keys = ON;")

        return conn
    
    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Utenti (
            telegram_id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            isAdmin INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS Canali (
            canale_id TEXT PRIMARY KEY NOT NULL,
            nome_canale TEXT NOT NULL,
            id_affiliato TEXT,
            codice_licenza TEXT NOT NULL,
            FOREIGN KEY (codice_licenza) REFERENCES Licenze(codice_licenza) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS Gestisce (
            telegram_id INTEGER NOT NULL,
            canale_id TEXT NOT NULL,
            id_affiliato TEXT,
            isCreator INTEGER DEFAULT 0,
            FOREIGN KEY (telegram_id) REFERENCES Utenti(telegram_id),
            FOREIGN KEY (canale_id) REFERENCES Canali(canale_id) ON DELETE CASCADE,
            PRIMARY KEY (telegram_id, canale_id)
        );

        CREATE TABLE IF NOT EXISTS Possiede (
            canale_id TEXT NOT NULL,
            layout_id INTEGER NOT NULL,
            in_uso INTEGER DEFAULT 0,
            FOREIGN KEY (canale_id) REFERENCES Canali(canale_id) ON DELETE CASCADE,
            FOREIGN KEY (layout_id) REFERENCES Layout(layout_id) ON DELETE CASCADE,
            PRIMARY KEY (canale_id, layout_id)
        );

        CREATE TABLE IF NOT EXISTS Layout (
            layout_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_layout TEXT NOT NULL,
            messaggio TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Licenze (
            codice_licenza TEXT PRIMARY KEY,
            scadenza DATE NOT NULL,
            stato INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Link (
            link_id INTEGER PRIMARY KEY AUTOINCREMENT,
            messaggio TEXT NOT NULL,
            canale_id TEXT NOT NULL,
            FOREIGN KEY (canale_id) REFERENCES Canali(canale_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS Pubblica (
            id INTEGER,
            id_canale TEXT NOT NULL,
            asin_prodotti TEXT NOT NULL, 
            FOREIGN KEY (id_canale) REFERENCES Canali(canale_id) ON DELETE CASCADE,
            FOREIGN KEY (asin_prodotti) REFERENCES Prodotti(asin) ON DELETE CASCADE,
            PRIMARY KEY(id,id_canale,asin_prodotti)
        );

        CREATE TABLE IF NOT EXISTS Prodotti (
            asin TEXT PRIMARY KEY NOT NULL,
            titolo TEXT NOT NULL,
            prezzo REAL NOT NULL,
            old_prezzo REAL NOT NULL,
            valuta TEXT NOT NULL,
            sconto REAL NOT NULL,
            sconto_percentuale REAL NOT NULL,
            venditore TEXT NOT NULL,
            spedito_da TEXT NOT NULL,
            link TEXT NOT NULL,
            img_url TEXT NOT NULL,
            brand TEXT NOT NULL,
            preorder INTEGER NOT NULL,
            data_preordine DATE,
            isPrime INTEGER NOT NULL DEFAULT 0,
            isWarehouse INTEGER NOT NULL DEFAULT 0,
            condizione TEXT,
            condizione_descrizione TEXT
        );
        """)
        
        conn.commit()
        conn.close()