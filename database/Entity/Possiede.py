class Possiede:
    def __init__(self, canale_id: str, layout_id: int, in_uso: bool = 0):
        self.canale_id = canale_id
        self.layout_id = layout_id
        self.in_uso = in_uso

    def get_canale_id(self) -> str:
        return self.canale_id

    def set_canale_id(self, new_canale_id: str) -> None:
        self.canale_id = new_canale_id

    def get_layout_id(self) -> int:
        return self.layout_id

    def set_layout_id(self, new_layout_id: int) -> None:
        self.layout_id = new_layout_id

    def get_in_uso(self) -> int:
        return self.in_uso

    def set_in_uso(self, new_in_uso: int) -> None:
        self.in_uso = new_in_uso