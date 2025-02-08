import requests

def expand_bitly_url(short_url):
    response = requests.get(short_url, allow_redirects=True)
    return response.url