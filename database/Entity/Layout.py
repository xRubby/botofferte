from dataclasses import dataclass

@dataclass
class Layout:
    layout_id: int
    nome_layout: str
    messaggio: str
    in_uso: bool
    canale_id: str