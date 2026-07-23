from enum import Enum


class EsitoInvito(Enum):
    OK = "ok"
    NON_TROVATO = "non_trovato"
    SCADUTO = "scaduto"
    GIA_MEMBRO = "gia_membro"