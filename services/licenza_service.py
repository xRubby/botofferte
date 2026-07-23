from datetime import datetime

from enums.esito_licenza import EsitoLicenza
from models.licenza import Licenza
from repositories.licenza_repository import LicenzaRepository
from utils.generate_license import calcola_data_scadenza, calcola_tipo_scadenza, generate_license
from enums.StatoLicenza import StatoLicenza


class LicenzaService:

    def __init__(self, session):
        self.session = session
        self.licenza_repository = LicenzaRepository(session)

    def crea_licenza(self, tipo_licenza) -> EsitoLicenza:
        if calcola_tipo_scadenza(tipo_licenza):
            codice_licenza = generate_license()

            licenza = Licenza(
                codice_licenza = codice_licenza,
                tipo = tipo_licenza
            )

            self.licenza_repository.create(licenza)

            return EsitoLicenza.OK, codice_licenza
        else:
            return EsitoLicenza.ERRORE


    def activate_licenza(self, licenza: str | Licenza) -> bool:

        if isinstance(licenza, str):
            licenza = self.licenza_repository.get(licenza)

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

        return True

    def get_stato(self, licenza: str | Licenza) -> StatoLicenza | None:

        if isinstance(licenza, str):
            licenza = self.licenza_repository.get(licenza)

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
            licenza = self.licenza_repository.get(licenza)

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

    def ottieni_licenza(self, codice_licenza: str) -> Licenza | None:

        return self.licenza_repository.get(codice_licenza)

    def ottieni_licenze_paginate(self, pagina: int, item_per_pagina: int) -> tuple[list[Licenza], int]:

        return self.licenza_repository.get_paginated(pagina, item_per_pagina)