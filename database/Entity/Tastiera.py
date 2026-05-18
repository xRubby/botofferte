from dataclasses import dataclass

@dataclass
class Tastiera:
    tastiera_id: int
    nome_tastiera: str
    messaggio: str
    in_uso: bool
    canale_id: str