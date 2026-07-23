from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.gestisce import Gestisce
    from models.invito import Invito
    from models.layout import Layout
    from models.layout_immagine import LayoutImmagine
    from models.pubblica import Pubblica
    from models.tastiera import Tastiera
    from models.licenza import Licenza


class Canale(Base):

    __tablename__ = "canali"

    canale_id: Mapped[str] = mapped_column(String, primary_key=True, autoincrement=False)

    nome_canale: Mapped[str] = mapped_column(String, nullable=False)

    id_affiliato: Mapped[str | None] = mapped_column(String, nullable=True)

    codice_licenza: Mapped[str] = mapped_column(String, ForeignKey("licenze.codice_licenza", ondelete="SET NULL"), nullable=True)

    amazon_tag: Mapped[str] = mapped_column(String, nullable=False, default="Venduto e spedito da Amazon")

    venditoreamazon_tag: Mapped[str] = mapped_column(String, nullable=False, default="Venduto da {venditore} e spedito da Amazon")

    venditore_tag: Mapped[str] = mapped_column(String, nullable=False, default="Venduto e spedito da {venditore}")

    preorder_tag: Mapped[str] = mapped_column(String, nullable=False, default="Preordine:")
    
    prime_tag: Mapped[str] = mapped_column(String, nullable=False, default="Spedizione gratuita con Amazon Prime")  
    
    offertaexcl_tag: Mapped[str] = mapped_column(String, nullable=False, default="Offerta Speciale:") 


    tastiere: Mapped[list["Tastiera"]] = relationship(back_populates="canale")

    gestioni: Mapped[list["Gestisce"]] = relationship(back_populates="canale")

    inviti: Mapped[list["Invito"]] = relationship(back_populates="canale")

    layout: Mapped[list["Layout"]] = relationship(back_populates="canale")

    layout_immagini: Mapped[list["LayoutImmagine"]] = relationship(back_populates="canale")

    pubblicazioni: Mapped[list["Pubblica"]] = relationship(back_populates="canale")

    licenza: Mapped["Licenza"] = relationship(back_populates="canale")

