from dataclasses import dataclass

@dataclass
class Utente:
    telegram_id: int
    nome: str
    isAdmin: bool = False