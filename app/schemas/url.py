"""Pydantic request/response schemas -- the HTTP boundary, distinct from
the ORM model that describes what's stored."""
from pydantic import BaseModel, HttpUrl


class CreateUrlRequest(BaseModel):
    url: HttpUrl


class CreateUrlResponse(BaseModel):
    short_code: str
    short_url: str

