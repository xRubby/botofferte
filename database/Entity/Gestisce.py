from dataclasses import dataclass

@dataclass
class Gestisce:
    telegram_id: int
    canale_id: str
    id_affiliato: str
    isCreator: bool
