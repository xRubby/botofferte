from database.Connessione import Connessione
from database.Entity.Canale import Canale

class CanaleDAO:
    def __init__(self):
        self._con = None
        self._connessione = None

    def __enter__(self):
        self._connessione = Connessione()
        self._con = self._connessione.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._connessione.__exit__(exc_type, exc_val, exc_tb)

    def _get_con(self):
        if self._con is not None:
            return self._con
        raise RuntimeError("CanaleDAO deve essere usato dentro un blocco 'with'")

    def insert(self, canale_id: str, nome_canale: str, id_affiliato: str, codice_licenza: str) -> None:
        self._get_con().execute(
            "INSERT INTO canali (canale_id, nome_canale, id_affiliato, codice_licenza) VALUES (?, ?, ?, ?)",
            (canale_id, nome_canale, id_affiliato, codice_licenza)
        )

    def update(self, canale_id: str, nome_canale: str, id_affiliato: str, codice_licenza: str) -> None:
        self._get_con().execute(
            "UPDATE canali SET nome_canale = ?, id_affiliato = ?, codice_licenza = ? WHERE canale_id = ?",
            (nome_canale, id_affiliato, codice_licenza, canale_id)
        )

    def update_tags(self, canale_id: str, amazon_tag: str, venditoreamazon_tag: str, venditore_tag: str, preorder_tag: str, prime_tag: str) -> None:
        self._get_con().execute(
            """UPDATE Canali SET
                amazon_tag          = ?,
                venditoreamazon_tag = ?,
                venditore_tag       = ?,
                preorder_tag        = ?,
                prime_tag           = ?
            WHERE canale_id = ?""",
            (amazon_tag, venditoreamazon_tag, venditore_tag, preorder_tag, prime_tag, canale_id)
        )

    def update_id_affiliato(self, canale_id: str, id_affiliato: str) -> None:
        self._get_con().execute(
            "UPDATE canali SET id_affiliato = ? WHERE canale_id = ?",
            (id_affiliato, canale_id)
        )

    def delete(self, canale_id: str) -> None:
        self._get_con().execute(
            "DELETE FROM canali WHERE canale_id = ?", (canale_id,)
        )

    def get(self, canale_id: str) -> Canale | None:
        row = self._get_con().execute(
            "SELECT * FROM canali WHERE canale_id = ?", (canale_id,)
        ).fetchone()
        return Canale(*row) if row else None

    def get_all(self) -> list[Canale]:
        rows = self._get_con().execute("SELECT * FROM canali").fetchall()
        return [Canale(*row) for row in rows]

    def get_user_channels(self, telegram_id: int) -> list[Canale]:
        rows = self._get_con().execute("""
            SELECT c.* FROM canali c
            JOIN gestisce g ON g.canale_id = c.canale_id
            WHERE g.telegram_id = ?
        """, (telegram_id,)).fetchall()
        return [Canale(*row) for row in rows]

    def get_channel_by_licensecode(self, codice_licenza: str) -> Canale | None:
        row = self._get_con().execute(
            "SELECT * FROM canali WHERE codice_licenza = ?", (codice_licenza,)
        ).fetchone()
        return Canale(*row) if row else None

    def update_codice_licenza(self, canale_id: str, codice_licenza: str) -> None:
        self._get_con().execute(
            "UPDATE canali SET codice_licenza = ? WHERE canale_id = ?",
            (codice_licenza, canale_id)
        )