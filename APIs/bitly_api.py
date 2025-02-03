import os
import logging
import requests
from dotenv import load_dotenv

# Carica le variabili d'ambiente
load_dotenv()

# Bitly token
BITLY_TOKEN = os.getenv('BITLY_TOKEN')

def shorten_url(url):
    headers = {
        'Authorization': f'Bearer {BITLY_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'long_url': url
    }
    
    response = requests.post('https://api-ssl.bitly.com/v4/shorten', headers=headers, json=data)
    
    if response.status_code in (200, 201):
        return response.json().get('link') 
    else:
        logging.error(f"Errore accorciando il link: {response.status_code} - {response.text}")
        return url