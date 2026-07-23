from datetime import datetime

from models.licenza import Licenza
from repositories.licenza_repository import LicenzaRepository
from utils.generate_license import calcola_data_scadenza
from enums.StatoLicenza import StatoLicenza


class LicenzaService:

    def __init__(self, licenza_repository: LicenzaRepository):
        self.licenza_repository = licenza_repository


    def activate_licenza(self, licenza: str | Licenza) -> bool:

        if isinstance(licenza, str):
            licenza = self.repository.get(licenza)

        if not licenza:
            return False

        if not licenza.attiva:
            return False

        if licenza.data_attivazione is not None:
            return False


        data_attivazione = datetime.now()

        licenza.data_attivazione = data_attivazione

        licenza.data_scadenza = (
            calcola_data_scadenza(
                licenza.tipo,
                data_attivazione
            )
        )

        self.session.commit()

        return True

    def get_stato(self, licenza: str | Licenza) -> StatoLicenza | None:

        if isinstance(licenza, str):
            licenza = self.repository.get(licenza)

        if not licenza:
            return None

        if not licenza.attiva:
            return StatoLicenza.DISATTIVATA

        if licenza.data_attivazione is None:
            return StatoLicenza.NON_ATTIVATA

        if (licenza.data_scadenza and licenza.data_scadenza < datetime.now()):
            return StatoLicenza.SCADUTA

        return StatoLicenza.ATTIVA

    def release_licenza(self, licenza: str | Licenza):

        if isinstance(licenza, str):
            licenza = self.repository.get(licenza)

        if not licenza:
            return

        if not licenza.data_scadenza:
            return

        giorni = (licenza.data_scadenza - datetime.now()).days

        if giorni <= 0:
            return

        licenza.tipo = f"{giorni} giorni"
        licenza.data_attivazione = None
        licenza.data_scadenza = None

        self.session.commit()