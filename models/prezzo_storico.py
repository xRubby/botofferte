from datetime import datetime

from sqlalchemy import String, Float, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.prodotto import Prodotto


class PrezzoStorico(Base):

    __tablename__ = "prezzi_storico"


    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


    asin: Mapped[str] = mapped_column(String, ForeignKey("prodotti.asin", ondelete="CASCADE"), nullable=False)


    prezzo: Mapped[float] = mapped_column(Float, nullable=False)


    valuta: Mapped[str] = mapped_column(String, nullable=False)


    venditore: Mapped[str] = mapped_column(String, nullable=False)


    rilevato: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


    prodotto: Mapped["Prodotto"] = relationship(back_populates="storico_prezzi")