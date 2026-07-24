from sqlalchemy import select
from sqlalchemy.orm import Session

from models.layout_immagine import LayoutImmagine


class LayoutImmagineRepository:

    def __init__(self, session: Session):
        self.session = session


    def get(self, immagine_id: int) -> LayoutImmagine | None:

        stmt = select(LayoutImmagine).where(LayoutImmagine.immagine_id == immagine_id)

        return self.session.scalars(stmt).first()


    def get_in_uso(self, canale_id: str) -> LayoutImmagine | None:

        stmt = (select(LayoutImmagine).where(LayoutImmagine.canale_id == str(canale_id), LayoutImmagine.in_uso.is_(True)))

        return self.session.scalars(stmt).first()

    def get_all(self) -> list[LayoutImmagine]:

        stmt = select(LayoutImmagine)

        return list(self.session.scalars(stmt))

    def get_by_channel_id(self, canale_id: str) -> list[LayoutImmagine] | None:

        stmt = (select(LayoutImmagine).where(LayoutImmagine.canale_id == str(canale_id)).order_by(LayoutImmagine.immagine_id))

        return list(self.session.scalars(stmt))


    def create(self, immagine: LayoutImmagine) -> LayoutImmagine:

        self.session.add(immagine)

        return immagine


    def delete(self, immagine: LayoutImmagine) -> None:

        self.session.delete(immagine)