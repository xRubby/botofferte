from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime, LargeBinary, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.canale import Canale
    from models.prodotto import Prodotto


class Pubblica(Base):

    __tablename__ = "pubblica"


    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


    id_canale: Mapped[str] = mapped_column(String, ForeignKey("canali.canale_id", ondelete="CASCADE"), nullable=False)


    asin_prodotti: Mapped[str] = mapped_column(String, ForeignKey("prodotti.asin", ondelete="CASCADE"), nullable=False)


    messaggio: Mapped[str] = mapped_column(String, nullable=False)


    link: Mapped[str] = mapped_column(String, nullable=False)


    link_short: Mapped[str | None] = mapped_column(String, nullable=True)


    img_bytes: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)


    is_pubblicato: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


    data_pubblicazione: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


    canale: Mapped["Canale"] = relationship(back_populates="pubblicazioni")

    prodotto: Mapped["Prodotto"] = relationship(back_populates="pubblicazioni")