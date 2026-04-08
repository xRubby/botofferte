from dataclasses import dataclass

@dataclass
class Licenza:
    codice_licenza: str
    tipo: str
    data_attivazione: str
    data_scadenza: str
    attiva: bool