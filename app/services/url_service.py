"""Business logic. Compare to Step 1.3's UrlService: identical shape
(create_short_url, resolve), and it has no idea the storage underneath
just changed from a dict to Postgres -- that's the whole point."""
import random
import string

from app.config import get_settings
from app.repositories.url_repository import UrlRepository

_ALPHABET = string.ascii_letters + string.digits
_CODE_LENGTH = 7


def _generate_short_code() -> str:
    return "".join(random.choices(_ALPHABET, k=_CODE_LENGTH))


class UrlService:
    def __init__(self, repository: UrlRepository):
        self.repository = repository
        self.settings = get_settings()

    def create_short_url(self, original_url: str) -> tuple[str, str]:
        short_code = _generate_short_code()
        url = self.repository.create(short_code=short_code, original_url=original_url)
        short_url = f"{self.settings.base_url}/{url.short_code}"
        return url.short_code, short_url

    def resolve(self, short_code: str) -> str | None:
        url = self.repository.get_by_short_code(short_code)
        return url.original_url if url else None