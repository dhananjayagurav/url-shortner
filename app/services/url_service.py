"""Business logic. Compare to Step 1.3's UrlService: identical shape
(create_short_url, resolve), and it has no idea the storage underneath
just changed from a dict to Postgres -- that's the whole point."""

from app.config import get_settings
from app.repositories.url_repository import UrlRepository
from app.cache.url_cache import UrlCache



class UrlService:
    def __init__(self, repository: UrlRepository, cache: UrlCache):
        self.repository = repository
        self.cache = cache
        self.settings = get_settings()

    def create_short_url(self, original_url: str) -> tuple[str, str]:
        url = self.repository.create(original_url=original_url)
        short_url = f"{self.settings.base_url}/{url.short_code}"
        return url.short_code, short_url

    def resolve(self, short_code: str) -> str | None:
        cached_url = self.cache.get(short_code)
        if cached_url is not None:
            return cached_url

        url = self.repository.get_by_short_code(short_code)
        if url is None:
            return None

        self.cache.set(short_code, url.original_url)
        return url.original_url

    def delete_short_url(self, short_code: str) -> bool:
        return self.repository.delete(short_code=short_code)
    