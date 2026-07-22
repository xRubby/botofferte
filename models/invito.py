from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.canale import Canale

class Invito(Base):

    __tablename__ = "inviti"

    token: Mapped[str] = mapped_column(String, primary_key=True, autoincrement=False)

    data_creazione: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    canale_id: Mapped[str] = mapped_column(String, ForeignKey("canali.canale_id", ondelete="CASCADE"), nullable=False, unique=True)
    

    canale: Mapped["Canale"] = relationship(back_populates="inviti")
