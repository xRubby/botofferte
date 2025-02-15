class Gestisce:
    def __init__(self, telegram_id: int, canale_id: str, id_affiliato: str, isCreator: bool):
        
        self.telegram_id = telegram_id
        self.canale_id = canale_id
        self.id_affiliato = id_affiliato
        self.isCreator = isCreator

    def get_telegram_id(self):
        return self.telegram_id

    def set_telegram_id(self, new_telegram_id: int):
        self.telegram_id = new_telegram_id

    def get_canale_id(self):
        return self.canale_id

    def set_canale_id(self, new_canale_id: str):
        self.canale_id = new_canale_id

    def get_id_affiliato(self):
        return self.id_affiliato

    def set_id_affiliato(self, new_id_affiliato: str):
        self.id_affiliato = new_id_affiliato

    def get_isCreator(self):
        return self.isCreator

    def set_isCreator(self, new_isCreator: bool):
        self.isCreator = new_isCreator

