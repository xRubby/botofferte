class Prodotto:
    def __init__(self, asin: str, titolo: str, prezzo: float, old_prezzo: float, valuta: str, sconto: float, sconto_percentuale: float, venditore: str, spedito_da: str, link: str, img_url: str, brand: str, preorder: bool, data_preordine: str, isPrime: bool, isWarehouse: bool, condizione: str, condizione_descrizione: str):
        self.asin = asin
        self.titolo = titolo
        self.prezzo = prezzo
        self.old_prezzo = old_prezzo
        self.valuta = valuta
        self.sconto = sconto
        self.sconto_percentuale = sconto_percentuale
        self.venditore = venditore
        self.spedito_da = spedito_da
        self.link = link
        self.img_url = img_url
        self.brand = brand
        self.preorder = preorder
        self.data_preordine = data_preordine
        self.isPrime = isPrime
        self.isWarehouse = isWarehouse
        self.condizione = condizione
        self.condizione_descrizione = condizione_descrizione

    def setAsin(self, new_asin: str) -> None:
        self.asin = new_asin

    def getAsin(self) -> str:
        return self.asin

    def setTitolo(self, new_titolo: str) -> None:
        self.titolo = new_titolo

    def getTitolo(self) -> str:
        return self.titolo

    def setPrezzo(self, new_prezzo: float) -> None:
        self.prezzo = new_prezzo

    def getPrezzo(self) -> float:
        return self.prezzo

    def setOldPrezzo(self, new_old_prezzo: float) -> None:
        self.old_prezzo = new_old_prezzo

    def getOldPrezzo(self) -> float:
        return self.old_prezzo

    def setValuta(self, new_valuta: str) -> None:
        self.valuta = new_valuta

    def getValuta(self) -> str:
        return self.valuta

    def setSconto(self, new_sconto: float) -> None:
        self.sconto = new_sconto

    def getSconto(self) -> float:
        return self.sconto

    def setScontoPercentuale(self, new_sconto_percentuale: float) -> None:
        self.sconto_percentuale = new_sconto_percentuale

    def getScontoPercentuale(self) -> float:
        return self.sconto_percentuale

    def setVenditore(self, new_venditore: str) -> None:
        self.venditore = new_venditore

    def getVenditore(self) -> str:
        return self.venditore

    def setSpeditoDa(self, new_spedito_da: str) -> None:
        self.spedito_da = new_spedito_da

    def getSpeditoDa(self) -> str:
        return self.spedito_da

    def setLink(self, new_link: str) -> None:
        self.link = new_link

    def getLink(self) -> str:
        return self.link

    def setImgUrl(self, new_img_url: str) -> None:
        self.img_url = new_img_url

    def getImgUrl(self) -> str:
        return self.img_url

    def setBrand(self, new_brand: str) -> None:
        self.brand = new_brand

    def getBrand(self) -> str:
        return self.brand

    def setPreorder(self, new_preorder: bool) -> None:
        self.preorder = new_preorder

    def getPreorder(self) -> bool:
        return self.preorder

    def setDataPreordine(self, new_data_preordine: str) -> None:
        self.data_preordine = new_data_preordine

    def getDataPreordine(self) -> str:
        return self.data_preordine

    def setIsPrime(self, new_isPrime: bool) -> None:
        self.isPrime = new_isPrime

    def getIsPrime(self) -> bool:
        return self.isPrime

    def setIsWarehouse(self, new_isWarehouse: bool) -> None:
        self.isWarehouse = new_isWarehouse

    def getIsWarehouse(self) -> bool:
        return self.isWarehouse

    def setCondizione(self, new_condizione: str) -> None:
        self.condizione = new_condizione

    def getCondizione(self) -> str:
        return self.condizione

    def setCondizioneDescrizione(self, new_condizione_descrizione: str) -> None:
        self.condizione_descrizione = new_condizione_descrizione

    def getCondizioneDescrizione(self) -> str:
        return self.condizione_descrizione