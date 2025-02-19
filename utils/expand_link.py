import requests
import re

def expand_url(url):
    pattern = r'https?://[^\s/$.?#].[^\s]*'
    if re.match(pattern, url):
        try:

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, allow_redirects=True)
            return response.url

        except requests.RequestException as e:
            return None
    return url