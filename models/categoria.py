from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.prodotto import Prodotto


class Categoria(Base):

    __tablename__ = "categorie"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    amazon_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    nome: Mapped[str] = mapped_column(String(255), nullable=False)

    id_padre: Mapped[int | None] = mapped_column(ForeignKey("categorie.id", ondelete="CASCADE"), nullable=True)



    padre: Mapped["Categoria | None"] = relationship(remote_side="Categoria.id", back_populates="figli")

    figli: Mapped[list["Categoria"]] = relationship(back_populates="padre", passive_deletes=True)

    prodotti: Mapped[list["Prodotto"]] = relationship("Prodotto", foreign_keys="Prodotto.categoria_id", back_populates="categoria")

    root_prodotti: Mapped[list["Prodotto"]] = relationship("Prodotto", foreign_keys="Prodotto.root_categoria_id", back_populates="root_categoria")