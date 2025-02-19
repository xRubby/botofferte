import locale
import re

from urllib.parse import urlparse, parse_qs
from datetime import datetime

def check_url_pattern(keyword):
    pattern = r'https?://[^\s/$.?#].[^\s]*'
    if re.match(pattern, keyword):
        return True
    return False

def extract_asin_from_url(url):

    if check_url_pattern(url):

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
    return None

def search_warehouse_seller_id_from_link(url):
    if check_url_pattern(url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        return query_params.get('m', [None])[0]
    return None



def formatta_data(data):
    locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
    data_temp = datetime.strptime(data, "%Y-%m-%dT%H:%M:%SZ")

    giorno = data_temp.strftime("%d")
    anno = data_temp.strftime("%Y")

    mese = data_temp.strftime("%B").lower()

    data_formattata = f"{giorno} {mese} {anno}"
    return data_formattata