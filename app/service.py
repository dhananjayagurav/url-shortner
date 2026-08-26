"""Step 1.3 - business logic wrapped in a class too. URLService owns 
a URLStore and co-ordinates short_code generation + storage"""

from app.shortcode import generate_short_code
from app.storage import URLStore

class URLService:
    def __init__(self, store: URLStore):
        self.store = store 

    def create_short_url(self, original_url: str) -> str:
        short_code = generate_short_code()
        self.store.save_url(short_code, original_url)
        return short_code

    def resolve(self, short_code: str) -> str | None:
        return self.store.find_url(short_code)

    

