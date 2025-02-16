class Layout:
    def __init__(self, layout_id: int, nome_layout: str, messaggio: str, in_uso: bool, canale_id: str):
        self.layout_id = layout_id
        self.nome_layout = nome_layout
        self.messaggio = messaggio
        self.in_uso = in_uso
        self.canale_id = canale_id