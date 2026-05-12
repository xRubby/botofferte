import sqlite3
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class Connessione:
    def __init__(self, db_name: str = './data/amazon_offers.db'):
        self.db_name = db_name

    # ------------------------------------------------------------------
    # Connessione base
    # ------------------------------------------------------------------

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    # ------------------------------------------------------------------
    # Context manager — uso: with Connessione() as conn:
    # ------------------------------------------------------------------

    def __enter__(self) -> sqlite3.Connection:
        self._conn = self.get_connection()
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            if exc_type:
                self._conn.rollback()
                logger.error("Rollback eseguito per eccezione: %s", exc_val)
            else:
                self._conn.commit()
            self._conn.close()
            self._conn = None
        return False

    # ------------------------------------------------------------------
    # Context manager alternativo per query singole (usa @contextmanager)
    # ------------------------------------------------------------------

    @contextmanager
    def sessione(self):
        """
        Alternativa leggera per blocchi brevi:

            with db.sessione() as conn:
                conn.execute(...)
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # Creazione tabelle e indici
    # ------------------------------------------------------------------

    def create_tables(self):
        with self as conn:
            conn.executescript("""
            -- --------------------------------------------------------
            -- Tabelle
            -- --------------------------------------------------------

            CREATE TABLE IF NOT EXISTS Utenti (
                telegram_id INTEGER PRIMARY KEY,
                nome        TEXT    NOT NULL,
                isAdmin     INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS Licenze (
                codice_licenza  TEXT     PRIMARY KEY,
                tipo            TEXT     NOT NULL,
                data_attivazione DATETIME,
                data_scadenza   DATETIME,
                attiva INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS Canali (
                canale_id           TEXT PRIMARY KEY NOT NULL,
                nome_canale         TEXT NOT NULL,
                id_affiliato        TEXT,
                codice_licenza      TEXT NOT NULL,
                amazon_tag          TEXT NOT NULL DEFAULT 'Venduto e spedito da Amazon',
                venditoreamazon_tag TEXT NOT NULL DEFAULT 'Venduto da {venditore} e spedito da Amazon',
                venditore_tag       TEXT NOT NULL DEFAULT 'Venduto e spedito da {venditore}',
                preorder_tag        TEXT NOT NULL DEFAULT 'Preordine:',
                prime_tag           TEXT NOT NULL DEFAULT 'Spedizione gratuita con Amazon Prime',
                FOREIGN KEY (codice_licenza) REFERENCES Licenze(codice_licenza) ON DELETE SET NULL
            );
                               
            CREATE TABLE IF NOT EXISTS Inviti (
                token               TEXT PRIMARY KEY NOT NULL,
                data_creazione      DATETIME NOT NULL,
                canale_id           TEXT NOT NULL UNIQUE,
                FOREIGN KEY (canale_id)   REFERENCES Canali(canale_id)   ON DELETE CASCADE                
            );

            CREATE TABLE IF NOT EXISTS Gestisce (
                telegram_id INTEGER NOT NULL,
                canale_id   TEXT    NOT NULL,
                id_affiliato TEXT,
                isCreator   INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (telegram_id, canale_id),
                FOREIGN KEY (telegram_id) REFERENCES Utenti(telegram_id) ON DELETE CASCADE,
                FOREIGN KEY (canale_id)   REFERENCES Canali(canale_id)   ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS Layout (
                layout_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_layout TEXT    NOT NULL,
                messaggio   TEXT    NOT NULL,
                in_uso      INTEGER NOT NULL DEFAULT 0,
                canale_id   TEXT    NOT NULL,
                FOREIGN KEY (canale_id) REFERENCES Canali(canale_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS LayoutImmagini (
                immagine_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                canale_id    TEXT    NOT NULL,
                nome         TEXT    NOT NULL,
                template_img BLOB    NOT NULL,
                template_w   INTEGER NOT NULL,
                template_h   INTEGER NOT NULL,
                prod_x       INTEGER NOT NULL DEFAULT 50,
                prod_y       INTEGER NOT NULL DEFAULT 50,
                prod_w_pct   INTEGER NOT NULL DEFAULT 40,
                prod_h_pct   INTEGER NOT NULL DEFAULT 40,
                in_uso       INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (canale_id) REFERENCES Canali(canale_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS Prodotti (
                asin                  TEXT    PRIMARY KEY NOT NULL,
                titolo                TEXT    NOT NULL,
                prezzo                REAL    NOT NULL,
                old_prezzo            REAL    NOT NULL,
                valuta                TEXT    NOT NULL,
                sconto                REAL    NOT NULL,
                venditore             TEXT    NOT NULL,
                spedito_Amazon        INTEGER NOT NULL DEFAULT 0,
                link                  TEXT    NOT NULL,
                img_url               TEXT    NOT NULL,
                brand                 TEXT    NOT NULL,
                preorder              INTEGER NOT NULL DEFAULT 0,
                data_preordine        DATE,
                isPrime               INTEGER NOT NULL DEFAULT 0,
                isWarehouse           INTEGER NOT NULL DEFAULT 0,
                condizione            TEXT,
                condizione_descrizione TEXT,
                last_check            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                priorita              INTEGER  NOT NULL DEFAULT 2,
                offertaesclusiva      TEXT
            );

            CREATE TABLE IF NOT EXISTS PrezziStorico (
                id        INTEGER  PRIMARY KEY AUTOINCREMENT,
                asin      TEXT     NOT NULL,
                prezzo    REAL     NOT NULL,
                valuta    TEXT     NOT NULL,
                venditore TEXT     NOT NULL,
                rilevato  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (asin) REFERENCES Prodotti(asin) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS Pubblica (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                id_canale           TEXT    NOT NULL,
                asin_prodotti       TEXT    NOT NULL,
                messaggio           TEXT    NOT NULL,
                isPubblicato        INTEGER NOT NULL DEFAULT 0,
                data_pubblicazione  TEXT,
                FOREIGN KEY (id_canale)     REFERENCES Canali(canale_id)  ON DELETE CASCADE,
                FOREIGN KEY (asin_prodotti) REFERENCES Prodotti(asin)     ON DELETE CASCADE
            );

            -- --------------------------------------------------------
            -- Indici (FK e colonne usate spesso in WHERE/JOIN)
            -- --------------------------------------------------------

            CREATE INDEX IF NOT EXISTS idx_gestisce_canale
                ON Gestisce(canale_id);

            CREATE INDEX IF NOT EXISTS idx_gestisce_utente
                ON Gestisce(telegram_id);

            CREATE INDEX IF NOT EXISTS idx_layout_canale
                ON Layout(canale_id);

            CREATE INDEX IF NOT EXISTS idx_pubblica_canale
                ON Pubblica(id_canale);

            CREATE INDEX IF NOT EXISTS idx_pubblica_asin
                ON Pubblica(asin_prodotti);

            CREATE INDEX IF NOT EXISTS idx_pubblica_pubblicato
                ON Pubblica(isPubblicato);

            CREATE INDEX IF NOT EXISTS idx_prezzi_asin
                ON PrezziStorico(asin);

            CREATE INDEX IF NOT EXISTS idx_prezzi_rilevato
                ON PrezziStorico(rilevato);

            CREATE INDEX IF NOT EXISTS idx_prodotti_last_check
                ON Prodotti(last_check);

            CREATE INDEX IF NOT EXISTS idx_prodotti_priorita
                ON Prodotti(priorita);
                               
            CREATE INDEX IF NOT EXISTS idx_licenze_attiva
                ON Licenze(attiva);

            -- --------------------------------------------------------
            -- FTS5 per ricerca full-text sui prodotti
            -- --------------------------------------------------------

            CREATE VIRTUAL TABLE IF NOT EXISTS Prodotti_fts USING FTS5(
                titolo,
                asin,
                content='Prodotti',
                content_rowid='rowid'
            );

            -- Trigger INSERT
            CREATE TRIGGER IF NOT EXISTS fts_prodotti_insert AFTER INSERT ON Prodotti
            BEGIN
                INSERT INTO Prodotti_fts(rowid, titolo, asin)
                VALUES (new.rowid, REPLACE(new.titolo, '-', ''), new.asin);
            END;

            -- Trigger UPDATE (ricostruisce la riga FTS)
            CREATE TRIGGER IF NOT EXISTS fts_prodotti_update AFTER UPDATE ON Prodotti
            BEGIN
                DELETE FROM Prodotti_fts WHERE rowid = old.rowid;
                INSERT INTO Prodotti_fts(rowid, titolo, asin)
                VALUES (new.rowid, REPLACE(new.titolo, '-', ''), new.asin);
            END;

            -- Trigger DELETE
            CREATE TRIGGER IF NOT EXISTS fts_prodotti_delete AFTER DELETE ON Prodotti
            BEGIN
                DELETE FROM Prodotti_fts WHERE rowid = old.rowid;
            END;
            """)

        logger.info("Tabelle, indici e trigger creati/verificati con successo.")