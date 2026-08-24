"""Data access layer. The service layer never touches SQLAlchemy directly --
only this module does. This is what lets us swap storage later without
touching business logic."""
from sqlalchemy.orm import Session

from app.models.url import Url


class UrlRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, short_code: str, original_url: str) -> Url:
        url = Url(short_code=short_code, original_url=original_url)
        self.db.add(url)
        self.db.commit()
        self.db.refresh(url)
        return url

    def get_by_short_code(self, short_code: str) -> Url | None:
        return self.db.query(Url).filter(Url.short_code == short_code).first()