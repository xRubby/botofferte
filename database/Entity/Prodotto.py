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

    def setAsin(self, new_asin):
        self.asin = new_asin

    def getAsin(self):
        return self.asin

    def setTitolo(self, new_titolo):
        self.titolo = new_titolo

    def getTitolo(self):
        return self.titolo

    def setPrezzo(self, new_prezzo):
        self.prezzo = new_prezzo

    def getPrezzo(self):
        return self.prezzo

    def setOldPrezzo(self, new_old_prezzo):
        self.old_prezzo = new_old_prezzo

    def getOldPrezzo(self):
        return self.old_prezzo

    def setValuta(self, new_valuta):
        self.valuta = new_valuta

    def getValuta(self):
        return self.valuta

    def setSconto(self, new_sconto):
        self.sconto = new_sconto

    def getSconto(self):
        return self.sconto

    def setScontoPercentuale(self, new_sconto_percentuale):
        self.sconto_percentuale = new_sconto_percentuale

    def getScontoPercentuale(self):
        return self.sconto_percentuale

    def setVenditore(self, new_venditore):
        self.venditore = new_venditore

    def getVenditore(self):
        return self.venditore

    def setSpeditoDa(self, new_spedito_da):
        self.spedito_da = new_spedito_da

    def getSpeditoDa(self):
        return self.spedito_da

    def setLink(self, new_link):
        self.link = new_link

    def getLink(self):
        return self.link

    def setImgUrl(self, new_img_url):
        self.img_url = new_img_url

    def getImgUrl(self):
        return self.img_url

    def setBrand(self, new_brand):
        self.brand = new_brand

    def getBrand(self):
        return self.brand

    def setPreorder(self, new_preorder):
        self.preorder = new_preorder

    def getPreorder(self):
        return self.preorder

    def setDataPreordine(self, new_data_preordine):
        self.data_preordine = new_data_preordine

    def getDataPreordine(self):
        return self.data_preordine

    def setIsPrime(self, new_isPrime):
        self.isPrime = new_isPrime

    def getIsPrime(self):
        return self.isPrime

    def setIsWarehouse(self, new_isWarehouse):
        self.isWarehouse = new_isWarehouse

    def getIsWarehouse(self):
        return self.isWarehouse

    def setCondizione(self, new_condizione):
        self.condizione = new_condizione

    def getCondizione(self):
        return self.condizione

    def setCondizioneDescrizione(self, new_condizione_descrizione):
        self.condizione_descrizione = new_condizione_descrizione

    def getCondizioneDescrizione(self):
        return self.condizione_descrizione