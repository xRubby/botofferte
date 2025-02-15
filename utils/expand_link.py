import requests
import re

def expand_url(url):

    pattern = r'https?://[^\s/$.?#].[^\s]*'
    if re.match(pattern, url):
        response = requests.get(url, allow_redirects=True)
        return response.url
    return url