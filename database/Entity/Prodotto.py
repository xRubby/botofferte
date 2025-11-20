class Prodotto:
    def __init__(self, asin: str, titolo: str, prezzo: float, old_prezzo: float, valuta: str, sconto: float, venditore: str, spedito_Amazon: bool, link: str, img_url: str, brand: str, preorder: bool, data_preordine: str, isPrime: bool, isWarehouse: bool, condizione: str, condizione_descrizione: str, last_check: int, priorita: int, offertaesclusiva: str):
        self.asin = asin
        self.titolo = titolo
        self.prezzo = prezzo
        self.old_prezzo = old_prezzo
        self.valuta = valuta
        self.sconto = sconto
        self.venditore = venditore
        self.spedito_Amazon = spedito_Amazon
        self.link = link
        self.img_url = img_url
        self.brand = brand
        self.preorder = preorder
        self.data_preordine = data_preordine
        self.isPrime = isPrime
        self.isWarehouse = isWarehouse
        self.condizione = condizione
        self.condizione_descrizione = condizione_descrizione
        self.last_check = last_check
        self.priorita = priorita
        self.offertaesclusiva = offertaesclusiva