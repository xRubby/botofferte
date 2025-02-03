class Canale:
    def __init__(self, id, nome_canale, messaggio, id_affiliato):
        self.id = id
        self.nome_canale = nome_canale
        self.message = messaggio
        self.id_affiliato = id_affiliato


    def get_id(self):
        return self.id

    def set_id(self, value):
        self.id = value

    def get_nome_canale(self):
        return self.nome_canale

    def set_nome_canale(self, value):
        self.nome_canale = value

    def get_message(self):
        return self.message

    def set_message(self, value):
        self.message = value

    def set_id_affiliato(self, value):
        self.id_affiliato = value

    def get_id_affiliato(self):
        return self.id_affiliato

    
    