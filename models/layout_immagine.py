from sqlalchemy import ForeignKey, LargeBinary, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.canale import Canale


class LayoutImmagine(Base):

    __tablename__ = "layout_immagini"


    immagine_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    canale_id: Mapped[str] = mapped_column(ForeignKey("canali.canale_id", ondelete="CASCADE"), nullable=False)

    nome: Mapped[str] = mapped_column(String, nullable=False)

    template_img: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    template_w: Mapped[int] = mapped_column(Integer, nullable=False)

    template_h: Mapped[int] = mapped_column(Integer, nullable=False)

    prod_x: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    prod_y: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    prod_w_pct: Mapped[int] = mapped_column(Integer, default=40, nullable=False)

    prod_h_pct: Mapped[int] = mapped_column(Integer, default=40, nullable=False)

    prezzo_x: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    prezzo_y: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    prezzo_w_pct: Mapped[int] = mapped_column(Integer, default=40, nullable=False)

    prezzo_h_pct: Mapped[int] = mapped_column(Integer, default=40, nullable=False)

    prezzo_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    prezzo_old_x: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    prezzo_old_y: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    prezzo_old_w_pct: Mapped[int] = mapped_column(Integer, default=40, nullable=False)

    prezzo_old_h_pct: Mapped[int] = mapped_column(Integer, default=40, nullable=False)

    prezzo_old_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    sconto_x: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    sconto_y: Mapped[int] = mapped_column(Integer, default=50, nullable=False)

    sconto_w_pct: Mapped[int] = mapped_column(Integer, default=40, nullable=False)

    sconto_h_pct: Mapped[int] = mapped_column(Integer, default=40, nullable=False)

    sconto_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    in_uso: Mapped[bool] = mapped_column(Boolean, default=False)


    canale: Mapped["Canale"] = relationship( back_populates="layout_immagini")