from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.canale import Canale


class Layout(Base):

    __tablename__ = "layout"

    layout_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    nome_layout: Mapped[str] = mapped_column(String, nullable=False)
    
    messaggio: Mapped[str] = mapped_column(String, nullable=False)

    in_uso: Mapped[bool] = mapped_column(Boolean, nullable=False, default=0)

    canale_id: Mapped[str] = mapped_column(String, ForeignKey("canali.canale_id", ondelete="CASCADE"), nullable=False)
    

    canale: Mapped["Canale"] = relationship(back_populates="tastiere")
