from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.gestisce import Gestisce


class Utente(Base):

    __tablename__ = "utenti"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)

    nome: Mapped[str] = mapped_column(String, nullable=False)

    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=0)


    gestioni: Mapped[list["Gestisce"]] = relationship(back_populates="utente")