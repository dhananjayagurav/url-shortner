"""Step 1.3 - the dict is now encapsulated inside a class.
Each URLStore instance owns it's own data, and nothing outside 
the class reaches it directly"""

class URLStore:
    def __init__(self):
        self._urls: dict[str, str] = {}

    def save_url(self, short_code: str, original_url: str) -> None:
        self._urls[short_code] = original_url

    def find_url(self, short_code: str) -> str | None:
        return self._urls.get(short_code)

    


