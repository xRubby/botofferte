from sqlalchemy import select
from sqlalchemy.orm import Session

from models.prezzo_storico import PrezziStorico


class PrezziStoricoRepository:

    def __init__(self, session: Session):
        self.session = session


    def get(self, id: int) -> PrezziStorico | None:

        stmt = select(PrezziStorico).where(PrezziStorico.id == id)

        return self.session.scalars(stmt).first()


    def get_by_asin(self, asin: str) -> list[PrezziStorico] | None:

        stmt = (select(PrezziStorico).where(PrezziStorico.asin == asin).order_by(PrezziStorico.rilevato.desc()))

        return list(self.session.scalars(stmt))


    def get_last_by_asin(self, asin: str) -> PrezziStorico | None:

        stmt = (select(PrezziStorico).where(PrezziStorico.asin == asin).order_by(PrezziStorico.rilevato.desc()).limit(1))

        return self.session.scalars(stmt).first()


    def create(self, prezzo: PrezziStorico) -> PrezziStorico:

        self.session.add(prezzo)

        return prezzo


    def delete(self, prezzo: PrezziStorico) -> None:

        self.session.delete(prezzo)