from sqlalchemy.orm import Session

from models.layout_immagine import LayoutImmagine
from repositories.layout_immagine_repository import LayoutImmagineRepository

class LayoutImmagineService:

    def __init__(self, session: Session):
        self.session = session
        self.layout_immagine_repository = LayoutImmagineRepository(session)


    def ottieni_layout_immagine_in_uso(self, canale_id) -> LayoutImmagine | None:

        return self.layout_immagine_repository.get_in_uso(canale_id)

