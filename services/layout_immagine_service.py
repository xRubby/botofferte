from sqlalchemy.orm import Session

from models.layout_immagine import LayoutImmagine
from repositories.layout_immagine_repository import LayoutImmagineRepository

class LayoutImmagineService:

    def __init__(self, session: Session):
        self.session = session
        self.layout_immagine_repository = LayoutImmagineRepository(session)


    def ottieni_layout_immagine_in_uso(self, canale_id) -> LayoutImmagine | None:

        return self.layout_immagine_repository.get_in_uso(canale_id)

    def crea_layout_immagine(self, layout_immagine: LayoutImmagine) -> LayoutImmagine:

        return self.layout_immagine_repository.create(layout_immagine)

    def cancella_layout_immagine(self, layout_immagine: LayoutImmagine) -> None:

        return self.layout_immagine_repository.delete(layout_immagine)

    def ottieni_layout_immagini_canale(self, canale_id: str) -> list[LayoutImmagine] | None:

        return self.layout_immagine_repository.get_by_channel_id(canale_id)

    def ottieni_layout_immagine(self, layout_immagine_id: int) -> LayoutImmagine | None:

        return self.layout_immagine_repository.get(layout_immagine_id)

    def modifica_posizione_attributo_layout_immagine(self, layout_immagine_id: int, x_pct: int, y_pct: int, metodo: str) -> None:

        try:
            assert 0 <= x_pct <= 100 and 0 <= y_pct <= 100
        except (IndexError, ValueError, AssertionError):
            raise

        layout_immagine = self.ottieni_layout_immagine(layout_immagine_id)

        if layout_immagine:

            match metodo:
                case "update_posizione_prodotto":
                    layout_immagine.prod_x = x_pct
                    layout_immagine.prod_y = y_pct
                case "update_posizione_prezzo":
                    layout_immagine.prezzo_x = x_pct
                    layout_immagine.prezzo_y = y_pct
                case "update_posizione_prezzoold":
                    layout_immagine.prezzo_old_x = x_pct
                    layout_immagine.prezzo_old_y = y_pct
                case "update_posizione_sconto":
                    layout_immagine.sconto_x = x_pct
                    layout_immagine.sconto_y = y_pct

    def modifica_dimensione_attributo_layout_immagine(self, layout_immagine_id: int, w_pct: int, h_pct: int, metodo: str) -> None:

        try:
            assert 0 < w_pct <= 100 and 0 < h_pct <= 100
        except (IndexError, ValueError, AssertionError):
            raise

        layout_immagine = self.ottieni_layout_immagine(layout_immagine_id)

        if layout_immagine:

            match metodo:
                case "update_dimensioni_prodotto":
                    layout_immagine.prod_w_pct = w_pct
                    layout_immagine.prod_h_pct = h_pct
                case "update_dimensioni_prezzo":
                    layout_immagine.prezzo_w_pct = w_pct
                    layout_immagine.prezzo_h_pct = h_pct
                case "update_dimensioni_prezzoold":
                    layout_immagine.prezzo_old_w_pct = w_pct
                    layout_immagine.prezzo_old_h_pct = h_pct
                case "update_dimensioni_sconto":
                    layout_immagine.sconto_w_pct = w_pct
                    layout_immagine.sconto_h_pct = h_pct



