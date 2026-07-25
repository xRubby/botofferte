from sqlalchemy import create_engine, text
from datetime import datetime

from sqlalchemy import create_engine, text
from datetime import datetime, date

from dotenv import load_dotenv
import os

# ==========================
# CONFIGURAZIONE
# ==========================

load_dotenv()

SQLITE_DB = "sqlite:///Z:/AppData/botofferte/data/amazon_offers.db"
POSTGRE_DB = os.getenv("DATABASE_URL_MIGRATION")


sqlite_engine = create_engine(SQLITE_DB)
postgres_engine = create_engine(POSTGRE_DB)


# ==========================
# FUNZIONI PULIZIA DATI
# ==========================

mesi = {
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
    "dicembre": 12
}


def clean_string(value):

    if value is None:
        return None

    if isinstance(value, str):

        value = value.strip()

        if value == "":
            return None

    return value



def convert_bool(value):

    if value is None:
        return False

    if isinstance(value, bool):
        return value

    return bool(int(value))



def convert_float(value):

    if value is None:
        return None

    if isinstance(value, str):

        value = (
            value
            .replace("€", "")
            .replace("%", "")
            .replace(",", ".")
            .strip()
        )

        if value == "":
            return None

    return float(value)



def convert_date(value):

    if value is None:
        return None


    if isinstance(value, date):
        return value


    if isinstance(value, str):

        value = value.strip()

        if value == "":
            return None


        # 2026-06-25
        try:
            return date.fromisoformat(value)
        except:
            pass


        # 25 giugno 2026
        try:

            giorno, mese, anno = value.lower().split()

            return date(
                int(anno),
                mesi[mese],
                int(giorno)
            )

        except:
            print(
                "DATA NON RICONOSCIUTA:",
                value
            )

            return None


    return None



def convert_datetime(value):

    if value is None:
        return None


    if isinstance(value, datetime):
        return value


    if isinstance(value, str):

        value = value.strip()

        if value == "":
            return None


        try:
            return datetime.fromisoformat(value)

        except:

            print(
                "DATETIME NON RICONOSCIUTO:",
                value
            )

            return None


    return None



# ==========================
# LICENZE
# ==========================

def migrate_licenze():

    print("Migrazione licenze...")


    with sqlite_engine.connect() as sqlite:

        rows = sqlite.execute(
            text(
                "SELECT * FROM Licenze"
            )
        ).fetchall()


    with postgres_engine.begin() as pg:

        for l in rows:

            pg.execute(
                text("""
                INSERT INTO licenze
                (
                    codice_licenza,
                    tipo,
                    data_attivazione,
                    data_scadenza,
                    attiva
                )
                VALUES
                (
                    :codice,
                    :tipo,
                    :attivazione,
                    :scadenza,
                    :attiva
                )
                ON CONFLICT DO NOTHING
                """),
                {
                    "codice": l.codice_licenza,
                    "tipo": clean_string(l.tipo),
                    "attivazione": convert_datetime(
                        l.data_attivazione
                    ),
                    "scadenza": convert_datetime(
                        l.data_scadenza
                    ),
                    "attiva": convert_bool(
                        l.attiva
                    )
                }
            )


    print("Licenze OK")



# ==========================
# UTENTI
# ==========================

def migrate_utenti():

    print("Migrazione utenti...")


    with sqlite_engine.connect() as sqlite:

        rows = sqlite.execute(
            text(
                "SELECT * FROM Utenti"
            )
        ).fetchall()


    with postgres_engine.begin() as pg:

        for u in rows:

            pg.execute(
                text("""
                INSERT INTO utenti
                (
                    telegram_id,
                    nome,
                    is_admin
                )
                VALUES
                (
                    :id,
                    :nome,
                    :admin
                )
                ON CONFLICT DO NOTHING
                """),
                {
                    "id": u.telegram_id,
                    "nome": clean_string(u.nome),
                    "admin": convert_bool(
                        u.isAdmin
                    )
                }
            )


    print("Utenti OK")



# ==========================
# CANALI
# ==========================

def migrate_canali():

    print("Migrazione canali...")


    with sqlite_engine.connect() as sqlite:

        rows = sqlite.execute(
            text(
                "SELECT * FROM Canali"
            )
        ).fetchall()


    with postgres_engine.begin() as pg:

        for c in rows:

            pg.execute(
                text("""
                INSERT INTO canali
                (
                    canale_id,
                    nome_canale,
                    id_affiliato,
                    codice_licenza,
                    amazon_tag,
                    venditoreamazon_tag,
                    venditore_tag,
                    preorder_tag,
                    prime_tag,
                    offertaexcl_tag
                )
                VALUES
                (
                    :id,
                    :nome,
                    :aff,
                    :licenza,
                    :amazon,
                    :venditoreamazon,
                    :venditore,
                    :preorder,
                    :prime,
                    :offerta
                )
                ON CONFLICT DO NOTHING
                """),
                {
                    "id": c.canale_id,
                    "nome": clean_string(
                        c.nome_canale
                    ),
                    "aff": clean_string(
                        c.id_affiliato
                    ),
                    "licenza": clean_string(
                        c.codice_licenza
                    ),

                    "amazon": c.amazon_tag,
                    "venditoreamazon": c.venditoreamazon_tag,
                    "venditore": c.venditore_tag,
                    "preorder": c.preorder_tag,
                    "prime": c.prime_tag,
                    "offerta": c.offertaexcl_tag
                }
            )


    print("Canali OK")



# ==========================
# PRODOTTI
# ==========================

def migrate_prodotti():

    print("Migrazione prodotti...")


    with sqlite_engine.connect() as sqlite:

        rows = sqlite.execute(
            text(
                "SELECT * FROM Prodotti"
            )
        ).fetchall()


    print(
        "Prodotti trovati:",
        len(rows)
    )


    errori = 0


    with postgres_engine.begin() as pg:

        for p in rows:

            try:

                pg.execute(
                    text("""
                    INSERT INTO prodotti
                    (
                    asin,
                    titolo,
                    prezzo,
                    old_prezzo,
                    valuta,
                    sconto,
                    venditore,
                    spedito_amazon,
                    link,
                    img_url,
                    brand,
                    preorder,
                    data_preordine,
                    is_prime,
                    is_warehouse,
                    condizione,
                    condizione_descrizione,
                    last_check,
                    priorita,
                    offertaesclusiva
                    )

                    VALUES
                    (
                    :asin,
                    :titolo,
                    :prezzo,
                    :old,
                    :valuta,
                    :sconto,
                    :venditore,
                    :spedito,
                    :link,
                    :img,
                    :brand,
                    :preorder,
                    :data,
                    :prime,
                    :warehouse,
                    :condizione,
                    :descrizione,
                    :check,
                    :priorita,
                    :offerta
                    )

                    ON CONFLICT DO NOTHING
                    """),
                    {

                    "asin": p.asin,

                    "titolo": clean_string(
                        p.titolo
                    ),

                    "prezzo": convert_float(
                        p.prezzo
                    ),

                    "old": convert_float(
                        p.old_prezzo
                    ),

                    "valuta": p.valuta,

                    "sconto": convert_float(
                        p.sconto
                    ),

                    "venditore": clean_string(
                        p.venditore
                    ),

                    "spedito": convert_bool(
                        p.spedito_Amazon
                    ),

                    "link": p.link,

                    "img": p.img_url,

                    "brand": p.brand,

                    "preorder": convert_bool(
                        p.preorder
                    ),

                    "data": convert_date(
                        p.data_preordine
                    ),

                    "prime": convert_bool(
                        p.isPrime
                    ),

                    "warehouse": convert_bool(
                        p.isWarehouse
                    ),

                    "condizione": clean_string(
                        p.condizione
                    ),

                    "descrizione": clean_string(
                        p.condizione_descrizione
                    ),

                    "check": convert_datetime(
                        p.last_check
                    ),

                    "priorita": p.priorita,

                    "offerta": convert_bool(
                        p.offertaesclusiva
                    )
                    }

                )


            except Exception as e:

                errori += 1

                print(
                    "ERRORE PRODOTTO",
                    p.asin,
                    e
                )


    print(
        "Prodotti OK - errori:",
        errori
    )

def migrate_inviti():

    print("Migrazione inviti...")

    with sqlite_engine.connect() as sqlite:
        rows = sqlite.execute(
            text("SELECT * FROM Inviti")
        ).fetchall()


    with postgres_engine.begin() as pg:

        for i in rows:

            pg.execute(
                text("""
                INSERT INTO inviti
                (
                    token,
                    data_creazione,
                    canale_id
                )
                VALUES
                (
                    :token,
                    :data,
                    :canale
                )
                ON CONFLICT DO NOTHING
                """),
                {
                    "token": i.token,

                    "data": convert_datetime(
                        i.data_creazione
                    ),

                    "canale": i.canale_id
                }
            )


    print("Inviti OK")

def migrate_gestisce():

    print("Migrazione gestisce...")

    with sqlite_engine.connect() as sqlite:
        rows = sqlite.execute(
            text("SELECT * FROM Gestisce")
        ).fetchall()


    with postgres_engine.begin() as pg:

        for g in rows:

            pg.execute(
                text("""
                INSERT INTO gestisce
                (
                    telegram_id,
                    canale_id,
                    id_affiliato,
                    is_creator
                )
                VALUES
                (
                    :telegram,
                    :canale,
                    :aff,
                    :creator
                )
                ON CONFLICT DO NOTHING
                """),
                {

                    "telegram": g.telegram_id,

                    "canale": g.canale_id,

                    "aff": clean_string(
                        g.id_affiliato
                    ),

                    "creator": convert_bool(
                        g.isCreator
                    )

                }
            )


    print("Gestisce OK")

def migrate_layout():

    print("Migrazione layout...")

    with sqlite_engine.connect() as sqlite:

        rows = sqlite.execute(
            text("SELECT * FROM Layout")
        ).fetchall()


    with postgres_engine.begin() as pg:

        for l in rows:

            pg.execute(
                text("""
                INSERT INTO layout
                (
                    layout_id,
                    nome_layout,
                    messaggio,
                    in_uso,
                    canale_id
                )
                VALUES
                (
                    :id,
                    :nome,
                    :msg,
                    :uso,
                    :canale
                )
                ON CONFLICT DO NOTHING
                """),
                {

                    "id": l.layout_id,

                    "nome": clean_string(
                        l.nome_layout
                    ),

                    "msg": l.messaggio,

                    "uso": convert_bool(
                        l.in_uso
                    ),

                    "canale": l.canale_id

                }
            )


    print("Layout OK")

def migrate_tastiere():

    print("Migrazione tastiere...")

    with sqlite_engine.connect() as sqlite:
        rows = sqlite.execute(
            text("SELECT * FROM Tastiere")
        ).fetchall()


    with postgres_engine.begin() as pg:

        for t in rows:

            pg.execute(
                text("""
                INSERT INTO tastiere
                (
                    tastiera_id,
                    nome_tastiera,
                    messaggio,
                    in_uso,
                    canale_id
                )
                VALUES
                (
                    :id,
                    :nome,
                    :messaggio,
                    :uso,
                    :canale
                )
                ON CONFLICT DO NOTHING
                """),
                {
                    "id": t.tastiera_id,

                    "nome": clean_string(
                        t.nome_tastiera
                    ),

                    "messaggio": t.messaggio,

                    "uso": convert_bool(
                        t.in_uso
                    ),

                    "canale": t.canale_id
                }
            )


    print("Tastiere OK")

def migrate_layout_immagini():

    print("Migrazione layout immagini...")

    with sqlite_engine.connect() as sqlite:

        rows = sqlite.execute(
            text("SELECT * FROM LayoutImmagini")
        ).fetchall()


    with postgres_engine.begin() as pg:

        for i in rows:

            pg.execute(
                text("""
                INSERT INTO layout_immagini
                (
                    immagine_id,
                    canale_id,
                    nome,
                    template_img,
                    template_w,
                    template_h,

                    prod_x,
                    prod_y,
                    prod_w_pct,
                    prod_h_pct,

                    prezzo_x,
                    prezzo_y,
                    prezzo_w_pct,
                    prezzo_h_pct,
                    prezzo_active,

                    prezzo_old_x,
                    prezzo_old_y,
                    prezzo_old_w_pct,
                    prezzo_old_h_pct,
                    prezzo_old_active,

                    sconto_x,
                    sconto_y,
                    sconto_w_pct,
                    sconto_h_pct,
                    sconto_active,

                    in_uso
                )

                VALUES
                (
                    :id,
                    :canale,
                    :nome,
                    :img,
                    :tw,
                    :th,

                    :px,
                    :py,
                    :pw,
                    :ph,

                    :prezzox,
                    :prezzoy,
                    :prezzow,
                    :prezzoh,
                    :prezzoactive,

                    :oldx,
                    :oldy,
                    :oldw,
                    :oldh,
                    :oldactive,

                    :sx,
                    :sy,
                    :sw,
                    :sh,
                    :sactive,

                    :uso
                )

                ON CONFLICT DO NOTHING
                """),

                {

                "id": i.immagine_id,

                "canale": i.canale_id,

                "nome": clean_string(i.nome),

                "img": i.template_img,

                "tw": i.template_w,
                "th": i.template_h,


                "px": i.prod_x,
                "py": i.prod_y,
                "pw": i.prod_w_pct,
                "ph": i.prod_h_pct,


                "prezzox": i.prezzo_x,
                "prezzoy": i.prezzo_y,
                "prezzow": i.prezzo_w_pct,
                "prezzoh": i.prezzo_h_pct,

                "prezzoactive": convert_bool(
                    i.prezzo_active
                ),


                "oldx": i.prezzo_old_x,
                "oldy": i.prezzo_old_y,
                "oldw": i.prezzo_old_w_pct,
                "oldh": i.prezzo_old_h_pct,

                "oldactive": convert_bool(
                    i.prezzo_old_active
                ),


                "sx": i.sconto_x,
                "sy": i.sconto_y,
                "sw": i.sconto_w_pct,
                "sh": i.sconto_h_pct,

                "sactive": convert_bool(
                    i.sconto_active
                ),


                "uso": convert_bool(
                    i.in_uso
                )

                }
            )


    print("Layout immagini OK")

def migrate_prezzi_storico():
    print("Migrazione prezzi storico...")
    
    # Recupera gli ASIN validi già presenti in Postgres
    with postgres_engine.connect() as pg:
        asin_validi = {
            row.asin for row in pg.execute(text("SELECT asin FROM prodotti")).fetchall()
        }

    with sqlite_engine.connect() as sqlite:
        rows = sqlite.execute(text("SELECT * FROM PrezziStorico")).fetchall()

    skipped = 0
    with postgres_engine.begin() as pg:
        for p in rows:
            if p.asin not in asin_validi:
                skipped += 1
                continue
            pg.execute(
                text("""
                INSERT INTO prezzi_storico
                (id, asin, prezzo, valuta, venditore, rilevato)
                VALUES
                (:id, :asin, :prezzo, :valuta, :venditore, :rilevato)
                ON CONFLICT DO NOTHING
                """),
                {
                    "id": p.id,
                    "asin": p.asin,
                    "prezzo": convert_float(p.prezzo),
                    "valuta": p.valuta,
                    "venditore": p.venditore,
                    "rilevato": convert_datetime(p.rilevato),
                }
            )
    print(f"Prezzi storico OK ({skipped} righe orfane saltate)")

def migrate_pubblica():
    print("Migrazione pubblicazioni...")

    # Recupera le chiavi valide già presenti in Postgres
    with postgres_engine.connect() as pg:
        asin_validi = {
            row.asin for row in pg.execute(text("SELECT asin FROM prodotti")).fetchall()
        }
        canali_validi = {
            row.canale_id for row in pg.execute(text("SELECT canale_id FROM canali")).fetchall()
        }

    with sqlite_engine.connect() as sqlite:
        rows = sqlite.execute(text("SELECT * FROM Pubblica")).fetchall()

    skipped = 0
    with postgres_engine.begin() as pg:
        for p in rows:
            if p.asin_prodotti not in asin_validi or p.id_canale not in canali_validi:
                skipped += 1
                continue

            pg.execute(
                text("""
                INSERT INTO pubblica
                (
                    id,
                    id_canale,
                    asin_prodotti,
                    messaggio,
                    link,
                    link_short,
                    img_bytes,
                    is_pubblicato,
                    data_pubblicazione
                )
                VALUES
                (
                    :id,
                    :canale,
                    :asin,
                    :msg,
                    :link,
                    :short,
                    :img,
                    :pub,
                    :data
                )
                ON CONFLICT DO NOTHING
                """),
                {
                    "id": p.id,
                    "canale": p.id_canale,
                    "asin": p.asin_prodotti,
                    "msg": p.messaggio,
                    "link": p.link,
                    "short": clean_string(p.link_short),
                    "img": p.img_bytes,
                    "pub": convert_bool(p.isPubblicato),
                    "data": convert_datetime(p.data_pubblicazione),
                }
            )
    print(f"Pubblica OK ({skipped} righe orfane saltate)")


# ==========================
# AVVIO
# ==========================
if __name__ == "__main__":

    migrate_licenze()

    migrate_utenti()

    migrate_canali()

    migrate_inviti()

    migrate_gestisce()

    migrate_layout()

    migrate_tastiere()

    migrate_layout_immagini()

    migrate_prodotti()

    migrate_prezzi_storico()

    migrate_pubblica()


    print("\nMIGRAZIONE COMPLETATA")