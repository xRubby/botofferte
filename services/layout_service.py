from sqlalchemy.orm import Session

from models.layout import Layout
from repositories.layout_repository import LayoutRepository

class LayoutService:

    def __init__(self, session: Session):
        self.session = session
        self.layout_repository = LayoutRepository(session)

    def ottieni_layout(self, layout_id: int) -> Layout:

        return self.layout_repository.get(layout_id)

    def ottieni_layout_in_uso(self, canale_id: str) -> Layout | None:

        return self.layout_repository.get_in_uso(canale_id)

    def ottieni_canale_layout(self, canale_id: str) -> list[Layout] | None:

        return self.layout_repository.get_by_canale(canale_id)

    def crea_layout(self, layout: Layout) -> Layout:

        return self.layout_repository.create(layout)

    def rimuovi_layout(self, layout: Layout) -> None:

        self.layout_repository.delete(layout)

