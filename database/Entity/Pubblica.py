class Pubblica:
    def __init__(self, id: int, id_canale: str, asin_prodotti: str):
        self.id = id
        self.id_canale = id_canale
        self.asin_prodotti = asin_prodotti

    def get_id(self):
        return self.id

    def set_id(self, new_id: int):
        self.id = new_id

    def get_id_canale(self):
        return self.id_canale

    def set_id_canale(self, new_id_canale: str):
        self.id_canale = new_id_canale

    def get_asin_prodotti(self):
        return self.asin_prodotti

    def set_asin_prodotti(self, new_asin_prodotti: str):
        self.asin_prodotti = new_asin_prodotti