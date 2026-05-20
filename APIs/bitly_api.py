import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
BITLY_TOKEN = os.getenv('BITLY_TOKEN')

async def shorten_url(url: str) -> str:
    headers = {
        'Authorization': f'Bearer {BITLY_TOKEN}',
        'Content-Type': 'application/json'
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                'https://api-ssl.bitly.com/v4/shorten',
                headers=headers,
                json={'long_url': url}
            )
        if response.status_code in (200, 201):
            return response.json().get('link', url)
    except Exception as e:
        logging.error(f"Errore accorciando il link: {e}")
    return url