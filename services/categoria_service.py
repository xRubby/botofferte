from sqlalchemy.orm import Session

from models.categoria import Categoria
from repositories.categoria_repository import CategoriaRepository


class CategoriaService:

    def __init__(self, session: Session):
        self.session = session
        self.categoria_repository = CategoriaRepository(session)

    def aggiungi_categoria(self, categoria: Categoria) -> Categoria:

        return self.categoria_repository.create(categoria)

    def rimuovi_categoria(self, categoria: Categoria) -> None:

        self.categoria_repository.delete(categoria)

    def ottieni_categoria(self, categoria_id: int) -> Categoria:

        return self.categoria_repository.get(categoria_id)

    def aggiungi_o_ottieni_categorie_da_lista(self, categorie: list[dict]) -> tuple[Categoria, Categoria] | None:

        if not categorie:
            return None, None

        categoria_root = None
        categoria_padre = None

        for categoria in categorie:

            nuova_categoria = self.categoria_repository.get_by_amazon_id(categoria["amazon_id"])


            padre_id = categoria_padre.id if categoria_padre else None

            if not nuova_categoria:
                nuova_categoria = self.aggiungi_categoria(
                    Categoria(
                        amazon_id = categoria["amazon_id"], 
                        nome = categoria["nome"], 
                        id_padre = categoria_padre.id if categoria_padre else None)
                    )
            elif nuova_categoria.id_padre != padre_id:
                nuova_categoria.id_padre = padre_id

            if categoria_root is None:
                categoria_root = nuova_categoria

            categoria_padre = nuova_categoria

            self.session.flush()

        return categoria_root, categoria_padre