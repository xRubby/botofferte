import random
import string
import locale
import re
from datetime import datetime, timedelta


def generate_license():
    license_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return license_code

def calcola_tipo_scadenza(tipo: str) -> bool:
    if tipo.lower() == "senza scadenza":
        return True

    match = re.match(r"(\d+)\s*(giorno|giorni|settimana|settimane|mese|mesi|anno|anni)", tipo.lower())

    if not match:
        return False

    return True


def calcola_data_scadenza(tipo: str, data_attivazione: datetime) -> str | None:



    if tipo.lower() == "senza scadenza":
        return None

    match = re.match(r"(\d+)\s*(giorno|giorni|settimana|settimane|mese|mesi|anno|anni)", tipo.lower())

    if not match:
        raise ValueError(f"Formato della licenza non valido: {tipo}")

    numero = int(match.group(1))
    unita = match.group(2)

    if unita in ["giorno", "giorni"]:
        giorni_validita = numero
    elif unita in ["settimana", "settimane"]:
        giorni_validita = numero * 7
    elif unita in ["mese", "mesi"]:
        giorni_validita = numero * 30
    elif unita in ["anno", "anni"]:
        giorni_validita = numero * 365
    else:
        raise ValueError(f"Unità di tempo sconosciuta: {unita}")

    data_scadenza = data_attivazione + timedelta(days=giorni_validita)
    return data_scadenza.strftime("%Y-%m-%d %H:%M:%S")