""" Step 1.2 - main.py now only handles HTTP. Storage and short_code 
generation live in their own modules"""

from fastapi import FastAPI, HTTPException 
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

from app.service import URLService
from app.storage import URLStore

app = FastAPI(title="URL shortner -> step 1.3(classes)")

service = URLService(URLStore())

class CreateURLRequest(BaseModel):
    url: HttpUrl

class CreateURLResponse(BaseModel):
    short_code: str
    short_url: str

@app.post("/api/v1/urls", response_model=CreateURLResponse, status_code=201)
def create_url(payload: CreateURLRequest):
    short_code = service.create_short_url(str(payload.url))
    return CreateURLResponse(
        short_code=short_code,
        short_url=f"http://localhost:8000/{short_code}"
    )


@app.get("/{short_code}")
def redirect(short_code: str):
    original_url = service.resolve(short_code)
    if original_url is None:
        raise HTTPException(status_code=404, detail="short code not found")
    return RedirectResponse(url=original_url, status_code=302)

