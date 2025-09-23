import os
import logging
import re

from amazon_paapi import AmazonApi
from dotenv import load_dotenv

from utils.amazon_utils import *

load_dotenv()

ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')
ASSOCIATE_TAG = os.getenv('ASSOCIATE_TAG')
REGION = os.getenv('REGION')

def search_amazon_offers(keyword, seller_id = None):

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

    try:
        amazon_client = AmazonApi(
            ACCESS_KEY,
            SECRET_KEY,
            ASSOCIATE_TAG,
            country=REGION
        )

        is_warehouse = seller_id == "A1HO9729ND375Y"
        cond = "Used" if is_warehouse else "New"

        response = amazon_client.search_items(
            keywords=keyword,
            search_index="All",
            item_count=1,
            condition=cond
        )

        offer = []
        for item in response.items:
            asin = item.asin
            product_name = item.item_info.title.display_value
            new_price = item.offers.listings[0].price.amount
            old_price = item.offers.listings[0].saving_basis.amount if item.offers.listings[0].saving_basis else new_price
            currency = item.offers.listings[0].price.currency
            discount_percentage = int((old_price - new_price) / old_price * 100) if old_price > new_price else 0
            
            venditore = item.offers.listings[0].merchant_info.name
            spedito_amazon = item.offers.listings[0].delivery_info.is_amazon_fulfilled
            venduto = seller_name_mapping.get(venditore, venditore)

            product_url = f"https://www.amazon.it/dp/{asin}?m={seller_id}" if is_warehouse else f"https://www.amazon.it/dp/{asin}"

            image_url = item.images.primary.large.url if item.images and item.images.primary.large else ''

            brand = item.item_info.by_line_info.brand.label

            try:
                data = item.item_info.product_info.release_date.display_value
                preorder = is_future_date(data)
                data_preordine = formatta_data(data) if preorder else None
            except Exception:
                preorder = False
                data_preordine = None

            prime = get_prime_status(item)
        
            cond, cond_comm = get_condition(item)

            offer.append({
                'ASIN': asin,
                'titolo': product_name,
                'prezzo': format_price(new_price),
                'old_prezzo': format_price(old_price),
                'valuta': currency_symbols.get(currency,currency),
                'sconto': discount_percentage,
                'venditore': venduto,
                'spedito_Amazon': spedito_amazon,
                'link': product_url,
                'img_url': image_url,
                'brand': brand,
                'preordine': preorder,
                'data_preordine': data_preordine,
                'isPrime': prime,
                'isWarehouse': is_warehouse,
                'condizione': cond,
                'condizione_descrizione': cond_comm
            })
        
        return offer

    except Exception as e:
        logging.error(f"Errore nel recupero delle offerte: {e}")
        raise Exception("Errore nel recupero delle offerte")