from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Boolean, Date, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.prezzo_storico import PrezzoStorico
    from models.pubblica import Pubblica
    from models.categoria import Categoria


class Prodotto(Base):

    __tablename__ = "prodotti"


    asin: Mapped[str] = mapped_column(String, primary_key=True, autoincrement=False)

    titolo: Mapped[str] = mapped_column(String, nullable=False)

    prezzo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    old_prezzo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    valuta: Mapped[str] = mapped_column(String, nullable=False)

    sconto: Mapped[int] = mapped_column(Integer, nullable=False)

    venditore: Mapped[str] = mapped_column(String, nullable=False)

    spedito_amazon: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    link: Mapped[str] = mapped_column(String, nullable=False)

    img_url: Mapped[str] = mapped_column(String, nullable=False)

    brand: Mapped[str] = mapped_column(String, nullable=False)

    preorder: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    data_preordine: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_prime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    is_warehouse: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    condizione: Mapped[str | None] = mapped_column(String, nullable=True)

    condizione_descrizione: Mapped[str | None] = mapped_column(String, nullable=True)

    last_check: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    priorita: Mapped[int] = mapped_column(Integer, default=2, nullable=False)

    offertaesclusiva: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorie.id", ondelete="SET NULL"), default=None, nullable=True)

    root_categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorie.id", ondelete="SET NULL"), default=None, nullable=True)


    storico_prezzi: Mapped[list["PrezzoStorico"]] = relationship(back_populates="prodotto", passive_deletes=True,)

    pubblicazioni: Mapped[list["Pubblica"]] = relationship(back_populates="prodotto", passive_deletes=True,)

    categoria: Mapped["Categoria | None"] = relationship("Categoria", foreign_keys=[categoria_id], back_populates="prodotti")

    root_categoria: Mapped["Categoria | None"] = relationship("Categoria", foreign_keys=[root_categoria_id], back_populates="root_prodotti")