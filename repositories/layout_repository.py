from sqlalchemy import select
from sqlalchemy.orm import Session

from models.layout import Layout


class LayoutRepository:

    def __init__(self, session: Session):
        self.session = session


    def get(self, layout_id: int) -> Layout | None:

        stmt = select(Layout).where(Layout.layout_id == layout_id)

        return self.session.scalars(stmt).first()


    def get_all(self) -> list[Layout]:

        stmt = select(Layout)

        return list(self.session.scalars(stmt))

    def get_in_uso(self, canale_id: str) -> Layout | None:

        stmt = (select(Layout).where(Layout.canale_id == canale_id, Layout.in_uso.is_(True)))

        return self.session.scalars(stmt).first()


    def create(self, layout: Layout) -> Layout:

        self.session.add(layout)

        return layout


    def delete(self, layout: Layout) -> None:

        self.session.delete(layout)