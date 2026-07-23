from sqlalchemy import select, func
from sqlalchemy.orm import Session

from models.licenza import Licenza


class LicenzaRepository:

    def __init__(self, session: Session):
        self.session = session


    def get(self, codice_licenza: str) -> Licenza | None:

        stmt = select(Licenza).where(Licenza.codice_licenza == codice_licenza)

        return self.session.scalars(stmt).first()


    def get_all(self) -> list[Licenza]:

        stmt = select(Licenza)

        return list(self.session.scalars(stmt))


    def get_paginated(self, page: int, per_page: int) -> tuple[list[Licenza], int]:

        offset = page * per_page

        stmt = (select(Licenza).offset(offset).limit(per_page))

        licenze = list(self.session.scalars(stmt))

        count_stmt = select(func.count()).select_from(Licenza)

        total = self.session.scalar(count_stmt)


        return licenze, total or 0


    def create(self, licenza: Licenza) -> Licenza:

        self.session.add(licenza)

        return licenza


    def delete(self, licenza: Licenza) -> None:

        self.session.delete(licenza)