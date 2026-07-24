from datetime import datetime, timedelta

from enums.esito_invito import EsitoInvito
from models import Invito
from models.gestisce import Gestisce
from repositories.gestisce_repository import GestisceRepository
from repositories.invito_repository import InvitoRepository
from sqlalchemy.orm import Session


class InvitoService:

    def __init__(self, session: Session):
        self.session = session
        self.invito_repository = InvitoRepository(session)
        self.gestisce_repository = GestisceRepository(session)

    def accetta_invito(self, token: str, telegram_id: int) -> EsitoInvito:
        invito = self.ottieni_invito(token)

        if invito is None:
            return EsitoInvito.NON_TROVATO

        if datetime.now() >= invito.data_creazione + timedelta(hours=2):
            return EsitoInvito.SCADUTO

        if self.gestisce_repository.get(telegram_id, invito.canale_id) is not None:
            return EsitoInvito.GIA_MEMBRO

        gestione = Gestisce(
            telegram_id=telegram_id,
            canale_id=invito.canale_id,
            id_affiliato="",
            is_creator=False,
        )

        self.gestisce_repository.create(gestione)

        self.invito_repository.delete(invito)

        return EsitoInvito.OK

    def crea_invito(self, invito: Invito) -> Invito:

        return self.invito_repository.create(invito)

    def ottieni_invito(self, token: str) -> Invito | None:

        return self.invito_repository.get(token)

    def ottieni_invito_per_canale(self, token: str) -> Invito | None:

        return self.invito_repository.get_by_canale(token)

    def cancella_invito(self, invito: Invito | str) -> bool:

        if isinstance(invito, str):
            invito = self.ottieni_invito(invito)

        if invito is None:
            return False

        self.invito_repository.delete(invito)

        return True