from sqlalchemy import select
from sqlalchemy.orm import Session

from models.prodotto import Prodotto


class ProdottoRepository:

    def __init__(self, session: Session):
        self.session = session


    def get_by_asin(self, asin: str) -> Prodotto | None:

        stmt = select(Prodotto).where(Prodotto.asin == asin)

        return self.session.scalars(stmt).first()


    def get_all(self) -> list[Prodotto]:

        stmt = select(Prodotto)

        return list(self.session.scalars(stmt))


    def create(self, prodotto: Prodotto) -> Prodotto:

        self.session.add(prodotto)

        return prodotto


    def delete(self, prodotto: Prodotto) -> None:

        self.session.delete(prodotto)