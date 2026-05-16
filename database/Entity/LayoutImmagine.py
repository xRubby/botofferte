from dataclasses import dataclass

@dataclass
class LayoutImmagine:
    immagine_id: int
    canale_id: str
    nome: str

    template_img: bytes
    template_w: int
    template_h: int

    # Prodotto
    prod_x: int = 50
    prod_y: int = 50
    prod_w_pct: int = 40
    prod_h_pct: int = 40

    # Prezzo corrente
    prezzo_x: int = 50
    prezzo_y: int = 50
    prezzo_w_pct: int = 40
    prezzo_h_pct: int = 40
    prezzo_active: bool = False

    # Prezzo precedente
    prezzo_old_x: int = 50
    prezzo_old_y: int = 50
    prezzo_old_w_pct: int = 40
    prezzo_old_h_pct: int = 40
    prezzo_old_active: bool = False

    # Sconto
    sconto_x: int = 50
    sconto_y: int = 50
    sconto_w_pct: int = 40
    sconto_h_pct: int = 40
    sconto_active: bool = False

    # Stato
    in_uso: bool = False