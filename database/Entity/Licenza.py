class Licenza:
    def __init__(self, codice_licenza: str, scadenza: str, stato: bool):
        self.codice_licenza = codice_licenza
        self.scadenza = scadenza
        self.stato = stato

    def setCodiceLicenza(self, new_codice):
        self.codice_licenza = new_codice

    def getCodiceLicenza(self):
        return self.codice_licenza

    def setScadenza(self, new_scadenza):
        self.scadenza = new_scadenza

    def getScadenza(self):
        return self.scadenza

    def setStato(self, new_stato):
        self.stato = new_stato

    def getStato(self):
        return self.stato