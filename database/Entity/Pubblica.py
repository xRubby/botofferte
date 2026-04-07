from dataclasses import dataclass

@dataclass
class Pubblica:
    id: int
    id_canale: str
    asin_prodotti: str
    messaggio: str
    isPubblicato: bool = 0
    data_pubblicazione: str = None