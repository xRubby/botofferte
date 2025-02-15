class Layout:
    def __init__(self, layout_id: int, nome_layout: str, messaggio: str):
        self.layout_id = layout_id
        self.nome_layout = nome_layout
        self.messaggio = messaggio

    def get_layout_id(self):
        return self.layout_id

    def set_layout_id(self, new_layout_id: int):
        self.layout_id = new_layout_id

    def get_nome_layout(self):
        return self.nome_layout

    def set_nome_layout(self, new_nome_layout: str):
        self.nome_layout = new_nome_layout

    def get_messaggio(self):
        return self.messaggio

    def set_messaggio(self, new_messaggio: str):
        self.messaggio = new_messaggio