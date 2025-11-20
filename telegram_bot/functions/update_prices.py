import time
import sqlite3

from database.DAO.ProdottoDAO import ProdottoDAO
from scraper.amazon_scraper import scraping_product
from database.Entity.Prodotto import Prodotto

def aggiorna_priorita():
    conn = sqlite3.connect("amazon_offers.db")
    cursor = conn.cursor()
    
    # Calcoliamo la frequenza delle richieste per ogni prodotto
    cursor.execute("""
        UPDATE Prodotti
        SET priorita = (
            SELECT 
                CASE 
                    WHEN COUNT(*) > 50 THEN 3  -- Molto richiesto
                    WHEN COUNT(*) BETWEEN 20 AND 50 THEN 2  -- Medio
                    ELSE 1  -- Poco richiesto
                END
            FROM Pubblica
            WHERE Pubblica.asin_prodotti = Prodotti.asin
        )
    """)

    conn.commit()
    conn.close()



def get_prodotti_da_aggiornare():
    conn = sqlite3.connect("amazon_offers.db")
    cursor = conn.cursor()
    
    tempo_attuale = int(time.time())  # Otteniamo il timestamp attuale
    
    # Query per selezionare i prodotti con priorità dinamica
    cursor.execute("""
        SELECT asin, titolo, prezzo, last_check
        FROM Prodotti
        WHERE 
            (strftime('%s', 'now') - last_check) > 
            CASE 
                WHEN priorita = 3 THEN 1800  -- 30 min
                WHEN priorita = 2 THEN 7200  -- 2 ore
                WHEN priorita = 1 THEN 43200  -- 12 ore
                ELSE 86400  -- 24 ore per preordini
            END
        ORDER BY priorita DESC, last_check ASC  -- Prima i più importanti
        LIMIT 10;
    """)

    prodotti = cursor.fetchall()
    conn.close()
    return prodotti
    
def aggiorna_prezzi():
    prodotti = get_prodotti_da_aggiornare()
    conn = sqlite3.connect("amazon_offers.db")
    cursor = conn.cursor()

    for asin, titolo, prezzo, last_check in prodotti:
        nuovo_prezzo = fetch_price(asin)

        if nuovo_prezzo and nuovo_prezzo != prezzo:
            cursor.execute("""
                UPDATE Prodotti 
                SET old_prezzo = prezzo, prezzo = ?, sconto = ((old_prezzo - ?) / old_prezzo) * 100, last_check = strftime('%s', 'now')
                WHERE asin = ?
            """, (nuovo_prezzo, nuovo_prezzo, asin))
            
            print(f"✅ Aggiornato {titolo} → Nuovo prezzo: {nuovo_prezzo}€")

    conn.commit()
    conn.close()

def aggiorna_prezzo(prodotto: Prodotto) -> Prodotto:

    if not prodotto:
        return None
    
    print("Aggiorno prezzo")

    epoch_corrente = int(time.time())
    
    if(epoch_corrente - prodotto.last_check) > 1200:
        prodotto_aggiornato = scraping_product(prodotto.asin)
        with ProdottoDAO() as dao:
            if prodotto_aggiornato and prodotto_aggiornato['prezzo'] != prodotto.prezzo:
                dao.update_price(
                    prodotto.asin,
                    prodotto_aggiornato['prezzo'],
                    prodotto_aggiornato['old_prezzo'],
                    prodotto_aggiornato['valuta'],
                    prodotto_aggiornato['sconto'],
                    prodotto_aggiornato['venditore'],
                    prodotto_aggiornato['spedito_Amazon'],
                    prodotto_aggiornato['offertaesclusiva']
                )
                prodotto.prezzo = prodotto_aggiornato['prezzo']
                prodotto.old_prezzo = prodotto_aggiornato['old_prezzo']
                prodotto.valuta = prodotto_aggiornato['valuta']
                prodotto.sconto = prodotto_aggiornato['sconto']
                prodotto.venditore = prodotto_aggiornato['venditore']
                prodotto.spedito_Amazon = prodotto_aggiornato['spedito_Amazon']
                prodotto.offertaesclusiva = prodotto_aggiornato['offertaesclusiva']

            dao.update_last_check(prodotto.asin, epoch_corrente)
        prodotto.last_check = epoch_corrente

    return prodotto
        


