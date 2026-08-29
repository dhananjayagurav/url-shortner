"""HTTP layer. get_url_service() is called fresh by FastAPI on every
single request -- constructing a plain object is cheap; what's expensive
(the physical DB connection) is pooled underneath get_db()."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.url_repository import UrlRepository
from app.schemas.url import CreateUrlRequest, CreateUrlResponse
from app.services.url_service import UrlService

router = APIRouter()


def get_url_service(db: Session = Depends(get_db)) -> UrlService:
    return UrlService(UrlRepository(db))


@router.post(
    "/api/v1/urls",
    response_model=CreateUrlResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_url(payload: CreateUrlRequest, service: UrlService = Depends(get_url_service)):
    short_code, short_url = service.create_short_url(str(payload.url))
    return CreateUrlResponse(short_code=short_code, short_url=short_url)


@router.get("/{short_code}")
def redirect(short_code: str, service: UrlService = Depends(get_url_service)):
    original_url = service.resolve(short_code)
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    return RedirectResponse(url=original_url, status_code=302)