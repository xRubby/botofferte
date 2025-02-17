class Utente:
    def __init__(self, telegram_id: int, nome: str, isAdmin: bool = False):
        self.telegram_id = telegram_id
        self.nome = nome
        self.isAdmin = isAdmin