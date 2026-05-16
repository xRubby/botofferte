# database/DAO/LayoutImmagineDAO.py
from database.Connessione import Connessione
from database.Entity.LayoutImmagine import LayoutImmagine

class LayoutImmagineDAO:
    def __enter__(self):
        self._connessione = Connessione()
        self._con = self._connessione.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._connessione.__exit__(exc_type, exc_val, exc_tb)

    def _get_con(self):
        if self._con is not None:
            return self._con
        raise RuntimeError("Usare dentro un blocco 'with'")

    def insert(self, canale_id: str, nome: str, template_img: bytes,
            template_w: int, template_h: int,
            prod_x: int = 50, prod_y: int = 50,
            prod_w_pct: int = 50, prod_h_pct: int = 50) -> int:
        cur = self._get_con().execute(
            """INSERT INTO LayoutImmagini
            (canale_id, nome, template_img, template_w, template_h,
                prod_x, prod_y, prod_w_pct, prod_h_pct, in_uso)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (canale_id, nome, template_img, template_w, template_h,
            prod_x, prod_y, prod_w_pct, prod_h_pct)
        )
        return cur.lastrowid

    def set_in_uso(self, immagine_id: int, canale_id: str) -> None:
        """Disattiva tutte le immagini del canale, poi attiva quella scelta."""
        con = self._get_con()
        con.execute(
            "UPDATE LayoutImmagini SET in_uso = 0 WHERE canale_id = ?",
            (canale_id,)
        )
        con.execute(
            "UPDATE LayoutImmagini SET in_uso = 1 WHERE immagine_id = ?",
            (immagine_id,)
        )

    def disattiva(self, canale_id: str) -> None:
        """Rimuove l'immagine attiva senza attivarne un'altra."""
        self._get_con().execute(
            "UPDATE LayoutImmagini SET in_uso = 0 WHERE canale_id = ?",
            (canale_id,)
        )

    def attiva_prezzo(self, immagine_id: str) -> None:
        self._get_con().execute(
            "UPDATE LayoutImmagini SET prezzo_active = 1 WHERE immagine_id = ?",
            (immagine_id,)
        )

    def disattiva_prezzo(self, immagine_id: str) -> None:
        self._get_con().execute(
            "UPDATE LayoutImmagini SET prezzo_active = 0 WHERE immagine_id = ?",
            (immagine_id,)
        )

    def update_posizione_prodotto(self, immagine_id: int, prod_x: int, prod_y: int) -> None:
        self._get_con().execute(
            "UPDATE LayoutImmagini SET prod_x = ?, prod_y = ? WHERE immagine_id = ?",
            (prod_x, prod_y, immagine_id)
        )

    def update_posizione_prezzo(self, immagine_id: int, prezzo_x: int, prezzo_y: int) -> None:
        self._get_con().execute(
            "UPDATE LayoutImmagini SET prezzo_x = ?, prezzo_y = ? WHERE immagine_id = ?",
            (prezzo_x, prezzo_y, immagine_id)
        )

    def update_posizione_prezzoold(self, immagine_id: int, prezzoold_x: int, prezzoold_y: int) -> None:
        self._get_con().execute(
            "UPDATE LayoutImmagini SET prezzo_old_x = ?, prezzo_old_y = ? WHERE immagine_id = ?",
            (prezzoold_x, prezzoold_y, immagine_id)
        )

    def update_posizione_sconto(self, immagine_id: int, sconto_x: int, sconto_y: int) -> None:
        self._get_con().execute(
            "UPDATE LayoutImmagini SET sconto_x = ?, sconto_y = ? WHERE immagine_id = ?",
            (sconto_x, sconto_y, immagine_id)
        )

    def update_dimensioni_prodotto(self, immagine_id: int, prod_w_pct: int, prod_h_pct: int) -> None:
        self._get_con().execute(
            "UPDATE LayoutImmagini SET prod_w_pct = ?, prod_h_pct = ? WHERE immagine_id = ?",
            (prod_w_pct, prod_h_pct, immagine_id)
        )

    def update_dimensioni_prezzo(self, immagine_id: int, prezzo_w_pct: int, prezzo_h_pct: int) -> None:
        self._get_con().execute(
            "UPDATE LayoutImmagini SET prezzo_w_pct = ?, prezzo_h_pct = ? WHERE immagine_id = ?",
            (prezzo_w_pct, prezzo_h_pct, immagine_id)
        )

    def update_dimensioni_prezzoold(self, immagine_id: int, prezzoold_w_pct: int, prezzoold_h_pct: int) -> None:
        self._get_con().execute(
            "UPDATE LayoutImmagini SET prezzo_old_w_pct = ?, prezzo_old_h_pct = ? WHERE immagine_id = ?",
            (prezzoold_w_pct, prezzoold_h_pct, immagine_id)
        )

    def update_dimensioni_sconto(self, immagine_id: int, sconto_w_pct: int, sconto_h_pct: int) -> None:
        self._get_con().execute(
            "UPDATE LayoutImmagini SET sconto_w_pct = ?, sconto_h_pct = ? WHERE immagine_id = ?",
            (sconto_w_pct, sconto_h_pct, immagine_id)
        )

    def delete(self, immagine_id: int) -> None:
        self._get_con().execute(
            "DELETE FROM LayoutImmagini WHERE immagine_id = ?", (immagine_id,)
        )

    def get(self, immagine_id: int) -> LayoutImmagine | None:
        row = self._get_con().execute(
            "SELECT * FROM LayoutImmagini WHERE immagine_id = ?", (immagine_id,)
        ).fetchone()
        return LayoutImmagine(**dict(row)) if row else None

    def get_in_uso(self, canale_id: str) -> LayoutImmagine | None:
        row = self._get_con().execute(
            "SELECT * FROM LayoutImmagini WHERE in_uso = 1 AND canale_id = ?",
            (canale_id,)
        ).fetchone()
        return LayoutImmagine(**dict(row)) if row else None

    def get_by_canale(self, canale_id: str) -> list[LayoutImmagine]:
        rows = self._get_con().execute(
            "SELECT * FROM LayoutImmagini WHERE canale_id = ? ORDER BY immagine_id",
            (canale_id,)
        ).fetchall()
        return [LayoutImmagine(**dict(row)) for row in rows]