from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.canale import Canale


class Licenza(Base):

    __tablename__ = "licenze"

    codice_licenza: Mapped[str] = mapped_column(String, primary_key=True, autoincrement=False)

    tipo: Mapped[str] = mapped_column(String, nullable=False)
    
    data_attivazione: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    data_scadenza: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    attiva: Mapped[bool] = mapped_column(Boolean, nullable=False, default=1)

    canale: Mapped["Canale"] = relationship(back_populates="licenza")