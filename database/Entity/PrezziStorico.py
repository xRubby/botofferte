from dataclasses import dataclass

@dataclass
class PrezziStorico:
    id: int
    asin: str
    prezzo: float 
    valuta: str
    venditore: str
    rilevato: int