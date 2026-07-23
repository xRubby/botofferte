from sqlalchemy.orm import Session

from models.layout import Layout
from repositories.layout_repository import LayoutRepository

class LayoutService:

    def __init__(self, session: Session):
        self.session = session
        self.layout_repository = LayoutRepository(session)


    def ottieni_layout_in_uso(self, canale_id) -> Layout | None:

        return self.layout_repository.get_in_uso(canale_id)

