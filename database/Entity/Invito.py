from dataclasses import dataclass

@dataclass
class Invito:
    token: str
    data_creazione: str
    canale_id: str
