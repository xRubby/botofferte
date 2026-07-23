from datetime import date, datetime

MESI = {
    "gennaio": 1,
    "febbraio": 2,
    "marzo": 3,
    "aprile": 4,
    "maggio": 5,
    "giugno": 6,
    "luglio": 7,
    "agosto": 8,
    "settembre": 9,
    "ottobre": 10,
    "novembre": 11,
    "dicembre": 12,
}

MESI_NOMI = {
    1: "gennaio",
    2: "febbraio",
    3: "marzo",
    4: "aprile",
    5: "maggio",
    6: "giugno",
    7: "luglio",
    8: "agosto",
    9: "settembre",
    10: "ottobre",
    11: "novembre",
    12: "dicembre",
}


def converti_data_preordine_da_db(data: date | None):
    if not data:
        return None

    return f"{data.day} {MESI_NOMI[data.month]} {data.year}"


def converti_data_preordine_per_db(data_testo: str | None):
    if not data_testo:
        return None

    try:
        giorno, mese, anno = data_testo.lower().split()

        return date(
            int(anno),
            MESI[mese],
            int(giorno)
        )

    except (ValueError, KeyError):
        return None