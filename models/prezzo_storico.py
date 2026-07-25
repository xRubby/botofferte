from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, String, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.prodotto import Prodotto
    from models.pubblica import Pubblica


class PrezzoStorico(Base):

    __tablename__ = "prezzi_storico"


    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


    asin: Mapped[str] = mapped_column(String, ForeignKey("prodotti.asin", ondelete="CASCADE"), nullable=False)


    prezzo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


    valuta: Mapped[str] = mapped_column(String, nullable=False)


    venditore: Mapped[str] = mapped_column(String, nullable=False)


    rilevato: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


    prodotto: Mapped["Prodotto"] = relationship(back_populates="storico_prezzi")

    pubblicazioni: Mapped[list["Pubblica"]] = relationship(back_populates="storico_prezzo")