class Link:
    def __init__(self, id: int, url: str, id_canale: str):
        self.id = id
        self.url = url
        self.id_canale = id_canale

    def setId(self, new_id):
        self.id = new_id

    def getId(self):
        return self.id

    def setUrl(self, new_url):
        self.url = new_url

    def getUrl(self):
        return self.url

    def setIdCanale(self, new_idcanale):
        self.id_canale = new_idcanale

    def getIdCanale(self):
        return self.id_canale