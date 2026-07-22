from sqlalchemy import BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.utente import Utente
    from models.canale import Canale


class Gestisce(Base):

    __tablename__ = "gestisce"

    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("utenti.telegram_id", ondelete="CASCADE"), primary_key=True, autoincrement=False)

    canale_id: Mapped[str] = mapped_column(String, ForeignKey("canali.canale_id", ondelete="CASCADE"), primary_key=True, autoincrement=False)

    id_affiliato: Mapped[str | None] = mapped_column(String, nullable=True)

    is_creator: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


    utente: Mapped["Utente"] = relationship(back_populates="gestioni")

    canale: Mapped["Canale"] = relationship(back_populates="gestioni")