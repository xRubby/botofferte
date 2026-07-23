from sqlalchemy import select
from sqlalchemy.orm import Session

from models.prezzo_storico import PrezzoStorico


class PrezziStoricoRepository:

    def __init__(self, session: Session):
        self.session = session


    def get(self, id: int) -> PrezzoStorico | None:

        stmt = select(PrezzoStorico).where(PrezzoStorico.id == id)

        return self.session.scalars(stmt).first()


    def get_by_asin(self, asin: str) -> list[PrezzoStorico] | None:

        stmt = (select(PrezzoStorico).where(PrezzoStorico.asin == asin).order_by(PrezzoStorico.rilevato.desc()))

        return list(self.session.scalars(stmt))


    def get_last_by_asin(self, asin: str) -> PrezzoStorico | None:

        stmt = (select(PrezzoStorico).where(PrezzoStorico.asin == asin).order_by(PrezzoStorico.rilevato.desc()).limit(1))

        return self.session.scalars(stmt).first()


    def create(self, prezzo: PrezzoStorico) -> PrezzoStorico:

        self.session.add(prezzo)

        return prezzo


    def delete(self, prezzo: PrezzoStorico) -> None:

        self.session.delete(prezzo)