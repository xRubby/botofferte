from dataclasses import dataclass

@dataclass
class LayoutImmagine:
    immagine_id: int
    canale_id: str
    nome: str
    template_img: bytes
    template_w: int
    template_h: int
    prod_x: int = 50
    prod_y: int = 50
    prod_w_pct: int = 40
    prod_h_pct: int = 40
    in_uso: bool = False