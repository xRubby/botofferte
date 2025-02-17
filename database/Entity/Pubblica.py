class Pubblica:
    def __init__(self, id: int, id_canale: str, asin_prodotti: str, messaggio: str, isPubblicato: bool = 0):
        self.id = id
        self.id_canale = id_canale
        self.asin_prodotti = asin_prodotti
        self.messaggio = messaggio
        self.isPubblicato = isPubblicato