class Pubblica:
    def __init__(self, id: int, id_canale: str, asin_prodotti: str, messaggio: str, isPubblicato: bool = 0):
        self.id = id
        self.id_canale = id_canale
        self.asin_prodotti = asin_prodotti
        self.messaggio = messaggio
        self.isPubblicato = isPubblicato

    def get_id(self) -> int:
        return self.id

    def set_id(self, new_id: int) -> None:
        self.id = new_id

    def get_id_canale(self) -> str:
        return self.id_canale

    def set_id_canale(self, new_id_canale: str) -> None:
        self.id_canale = new_id_canale

    def get_asin_prodotti(self) -> str:
        return self.asin_prodotti

    def set_asin_prodotti(self, new_asin_prodotti: str) -> None:
        self.asin_prodotti = new_asin_prodotti

    def get_messaggio(self) -> str:
        return self.messaggio
    
    def set_messaggio(self, new_messaggio: str) -> None:
        self.messaggio = new_messaggio

    def get_isPubblicato(self) -> bool:
        return self.isPubblicato
    
    def set_isPubblicato(self, new_isPubblicato: bool) -> None:
        self.isPubblicato = new_isPubblicato