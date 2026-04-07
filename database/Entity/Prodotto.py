from dataclasses import dataclass

@dataclass
class Prodotto:
    asin: str
    titolo: str 
    prezzo: float 
    old_prezzo: float 
    valuta: str
    sconto: float 
    venditore: str
    spedito_Amazon: bool
    link: str
    img_url: str 
    brand: str
    preorder: bool
    data_preordine: str
    isPrime: bool
    isWarehouse: bool
    condizione: str
    condizione_descrizione: str
    last_check: int
    priorita: int
    offertaesclusiva: str
