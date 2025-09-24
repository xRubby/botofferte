class PrezziStorico:
    def __init__(self, id: int, asin: str, prezzo: float, valuta: str, venditore: str, rilevato: int):
        self.id = id
        self.asin = asin
        self.prezzo = prezzo
        self.valuta = valuta
        self.venditore = venditore
        self.rilevato = rilevato