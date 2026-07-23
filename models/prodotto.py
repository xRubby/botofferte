from datetime import datetime, date

from sqlalchemy import String, Float, Boolean, Date, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.prezzo_storico import PrezzoStorico
    from models.pubblica import Pubblica


class Prodotto(Base):

    __tablename__ = "prodotti"


    asin: Mapped[str] = mapped_column(String, primary_key=True, autoincrement=False)

    titolo: Mapped[str] = mapped_column(String, nullable=False)

    prezzo: Mapped[float] = mapped_column(Float, nullable=False)

    old_prezzo: Mapped[float] = mapped_column(Float, nullable=False)

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


    storico_prezzi: Mapped[list["PrezzoStorico"]] = relationship(back_populates="prodotto")

    pubblicazioni: Mapped[list["Pubblica"]] = relationship(back_populates="prodotto")