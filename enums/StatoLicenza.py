from enum import Enum

class StatoLicenza(Enum):
    NON_ATTIVATA = "non_attivata"       # attiva=1, data_attivazione=NULL
    ATTIVA = "attiva"                    # attiva=1, data valida
    SCADUTA = "scaduta"                  # attiva=1, data_scadenza nel passato
    DISATTIVATA = "disattivata"          # attiva=0, disattivata dall'admin