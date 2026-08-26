"""Pydantic request/response schemas for the URL API."""
from pydantic import BaseModel, HttpUrl


class CreateUrlRequest(BaseModel):
    url: HttpUrl


class CreateUrlResponse(BaseModel):
    short_code: str
    short_url: str

