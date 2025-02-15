class Licenza:
    def __init__(self, codice_licenza: str, scadenza: str, stato: bool):
        self.codice_licenza = codice_licenza
        self.scadenza = scadenza
        self.stato = stato

    def setCodiceLicenza(self, new_codice) -> None:
        self.codice_licenza = new_codice

    def getCodiceLicenza(self) -> str:
        return self.codice_licenza

    def setScadenza(self, new_scadenza) -> None:
        self.scadenza = new_scadenza

    def getScadenza(self) -> str:
        return self.scadenza

    def setStato(self, new_stato) -> None:
        self.stato = new_stato

    def getStato(self) -> bool:
        return self.stato