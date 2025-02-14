class Utente:
    def __init__(self, telegram_id: int, nome: str, isAdmin: bool = False):
        self.telegram_id = telegram_id
        self.nome = nome
        self.isAdmin = isAdmin

    def setTelegramId(self, new_id):
        self.telegram_id = new_id

    def getTelegramId(self):
        return self.telegram_id

    def setNome(self, new_nome):
        self.nome = new_nome

    def getNome(self):
        return self.nome

    def setIsAdmin(self, new_isAdmin):
        self.isAdmin = new_isAdmin

    def getIsAdmin(self):
        return self.isAdmin