class Layout:
    def __init__(self, layout_id: int, nome_layout: str, messaggio: str, in_uso: bool, canale_id: str):
        self.layout_id = layout_id
        self.nome_layout = nome_layout
        self.messaggio = messaggio
        self.in_uso = in_uso
        self.canale_id = canale_id

    def get_layout_id(self) -> int:
        return self.layout_id

    def set_layout_id(self, new_layout_id: int) -> None:
        self.layout_id = new_layout_id

    def get_nome_layout(self) -> str:
        return self.nome_layout

    def set_nome_layout(self, new_nome_layout: str) -> None:
        self.nome_layout = new_nome_layout

    def get_messaggio(self) -> str:
        return self.messaggio

    def set_messaggio(self, new_messaggio: str) -> None:
        self.messaggio = new_messaggio

    def get_in_uso(self) -> bool:
        return self.in_uso
    
    def set_in_uso(self, new_in_uso: bool) -> None:
        self.in_uso = new_in_uso

    def get_canale_id(self) -> str:
        return self.canale_id
    
    def set_canale_id(self, new_canale_id) -> None:
        self.canale_id = new_canale_id