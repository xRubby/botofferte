class Canale:
    def __init__(self, canale_id: str, nome_canale: str, id_affiliato: str, codice_licenza: str):
        self.canale_id = canale_id
        self.nome_canale = nome_canale
        self.id_affiliato = id_affiliato
        self.codice_licenza = codice_licenza

    def setCanaleId(self, new_id) -> None:
        self.canale_id = new_id

    def getCanaleId(self) -> str:
        return self.canale_id

    def setNomeCanale(self, new_nome) -> None:
        self.nome_canale = new_nome

    def getNomeCanale(self) -> str:
        return self.nome_canale

    def setIdAffiliato(self, new_id_affiliato) -> None:
        self.id_affiliato = new_id_affiliato

    def getIdAffiliato(self) -> str:
        return self.id_affiliato

    def setCodiceLicenza(self, new_codice_licenza) -> None:
        self.codice_licenza = new_codice_licenza

    def getCodiceLicenza(self) -> str:
        return self.codice_licenza