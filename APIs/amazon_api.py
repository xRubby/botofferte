import os
import logging
from amazon_paapi import AmazonApi
from dotenv import load_dotenv
from APIs.bitly_api import shorten_url
import re
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from utils.expand_bitly_link import expand_bitly_url


load_dotenv()

ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
ASSOCIATE_TAG = os.getenv('ASSOCIATE_TAG')
REGION = os.getenv('REGION')


def extract_asin_from_url(url):
    parsed_url = urlparse(url)
    
    if '/dp/' in parsed_url.path:
        asin = parsed_url.path.split('/dp/')[1].split('/')[0]
    elif '/gp/product/' in parsed_url.path:
        asin = parsed_url.path.split('/gp/product/')[1].split('/')[0]
    else:
        asin_match = re.search(r'/([A-Z0-9]{10})', parsed_url.path)
        if asin_match:
            asin = asin_match.group(1)
        else:
            return None

    return asin



def formatta_data(data,preorder):
    if preorder:
        data_temp = datetime.strptime(data, "%Y-%m-%dT%H:%M:%SZ")

        giorno = data_temp.strftime("%d")
        anno = data_temp.strftime("%Y")

        mese = data_temp.strftime("%B").lower()

        data_formattata = f"{giorno} {mese} {anno}"
        return data_formattata

def verifica_preordine(data):

    data_temp = datetime.strptime(data, "%Y-%m-%dT%H:%M:%SZ")
    oggi = datetime.today()

    if data_temp > oggi:
        return "Preordine"
    else:
        return ""

def search_amazon_offers(keyword_or_url):

    currency_symbols = {
        'EUR': '€',
        'USD': '$',
        'GBP': '£',
        'JPY': '¥',
        'CAD': 'C$',
    }

    seller_name_mapping = {
        "Amazon.it": "Amazon",
        "Amazon.com": "Amazon",
    }

    pattern = r'https?://[^\s/$.?#].[^\s]*'
    if re.match(pattern, keyword_or_url):
        if "amazon" not in keyword_or_url:
            keyword_or_url = expand_bitly_url(keyword_or_url)
        

    asin = extract_asin_from_url(keyword_or_url)
    parsed_url = urlparse(keyword_or_url)
    query_params = parse_qs(parsed_url.query)
    warehouse_seller_id = query_params.get('m', [None])[0]
    
    if asin:
        keyword = asin
    else:
        keyword = keyword_or_url

    try:
        amazon_client = AmazonApi(
            ACCESS_KEY,
            SECRET_KEY,
            ASSOCIATE_TAG,
            country=REGION
        )

        is_warehouse = warehouse_seller_id == "A1HO9729ND375Y"
        if(is_warehouse):
            cond="Used"
        else:
            cond="New"
        
        response = amazon_client.search_items(
            keywords=keyword,
            search_index="All",
            item_count=1,
            condition=cond
                
        )

        offers = []
        for item in response.items:
            product_name = item.item_info.title.display_value
            image_url = item.images.primary.large.url if item.images and item.images.primary.large else ''
            new_price = item.offers.listings[0].price.amount
            old_price = item.offers.listings[0].saving_basis.amount if item.offers.listings[0].saving_basis else new_price
            discount_percentage = int((old_price - new_price) / old_price * 100) if old_price > new_price else 0
            asin = item.asin
            currency= item.offers.listings[0].price.currency

            venditore=item.offers.listings[0].merchant_info.name
            spedito_amazon=item.offers.listings[0].delivery_info.is_amazon_fulfilled

            venduto=seller_name_mapping.get(venditore,venditore)



            if(venduto=="Amazon" and spedito_amazon):
                spedito="Venduto e spedito da Amazon"
            elif(spedito_amazon):
                spedito=f"Venduto da {venditore} e spedito da Amazon"
            else:
                spedito=f"Venduto e spedito da {venditore}"



            if item.offers.listings[0].delivery_info.is_prime_eligible:
                prime="Amazon Prime"
            else:
                prime=""

            currency_symbol=currency_symbols.get(currency,currency)

            data=item.item_info.product_info.release_date.display_value

            
            preorder=verifica_preordine(data)
            data_preordine=formatta_data(data,preorder)

            if item.offers.listings[0].condition.value=="Used":
                warehouse="Warehouse"
                cond=item.offers.listings[0].condition.value
                cond_comm=item.offers.listings[0].condition.condition_note.value
            else:
                warehouse=""
                cond=""
                cond_comm=""



            if is_warehouse:
                product_url = f"https://www.amazon.it/dp/{asin}?m={warehouse_seller_id}&tag={ASSOCIATE_TAG}"
            else:
                product_url = f"https://www.amazon.it/dp/{asin}?tag={ASSOCIATE_TAG}"
            short_url = shorten_url(product_url)

            offers.append({
                'name': product_name,
                'old_price': "{:.2f}".format(old_price),
                'new_price': "{:.2f}".format(new_price),
                'discount_percentage': discount_percentage,
                'image_url': image_url,
                'url': short_url,
                'full_url': product_url,
                'currency': currency_symbol,
                'spedito': spedito,
                'prime': prime,
                'preorder': preorder,
                'preorderdate': data_preordine,
                'warehouse': warehouse,
                'condition': cond,
                'conditioncomm': cond_comm,
                'minimo': ""
            })
        
        return offers
    
    except Exception as e:
        logging.error(f"Errore nel recupero delle offerte: {e}")
        raise Exception("Errore nel recupero delle offerte")
        return []