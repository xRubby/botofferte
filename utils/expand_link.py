import re
import httpx

async def expand_url(url: str) -> str:
    pattern = r'https?://[^\s/$.?#].[^\s]*'
    if not re.match(pattern, url):
        return url
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            response = await client.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            return str(response.url)
    except Exception:
        return url