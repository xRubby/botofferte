from sqlalchemy import select
from sqlalchemy.orm import Session

from models.categoria import Categoria


class CategoriaRepository:

    def __init__(self, session: Session):
        self.session = session


    def create(self, categoria: Categoria) -> Categoria:

        self.session.add(categoria)

        return categoria


    def delete(self, categoria: Categoria) -> None:

        self.session.delete(categoria)


    def get(self, categoria_id: int) -> Categoria | None:
    
        stmt = (select(Categoria).where(Categoria.id == categoria_id))

        return self.session.scalars(stmt).first()
    
    
    def get_all(self) -> list[Categoria]:

        stmt = select(Categoria)

        return list(self.session.scalars(stmt))

    def get_by_amazon_id(self, amazon_id: str) -> Categoria | None:

        stmt = (select(Categoria).where(Categoria.amazon_id == amazon_id))
        
        return self.session.scalars(stmt).first()