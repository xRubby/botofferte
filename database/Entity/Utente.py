class Utente:
    def __init__(self, telegram_id: int, nome: str, isAdmin: bool = False):
        self.telegram_id = telegram_id
        self.nome = nome
        self.isAdmin = isAdmin

    def setTelegramId(self, new_id) -> None:
        self.telegram_id = new_id

    def getTelegramId(self) -> int:
        return self.telegram_id

    def setNome(self, new_nome) -> None:
        self.nome = new_nome

    def getNome(self) -> str:
        return self.nome

    def setIsAdmin(self, new_isAdmin) -> None:
        self.isAdmin = new_isAdmin

    def getIsAdmin(self) -> bool:
        return self.isAdmin