"""In memory storage functions. These are pulled out of main.py. 
Still at module level, no class implementation yet"""

_urls: dict[str, str] = {}

def save_url(short_code: str, original_url: str) -> None:
    _urls[short_code] = original_url

def find_url(short_code: str) -> str | None:
    return _urls.get(short_code)


