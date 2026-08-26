""" Step 1.2 - main.py now only handles HTTP. Storage and short_code 
generation live in their own modules"""

from fastapi import FastAPI, HTTPException 
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

from shortcode import generate_short_code
from storage import save_url, find_url

app = FastAPI(title="URL shortner")

class CreateURLRequest(BaseModel):
    url: HttpUrl

class CreateURLResponse(BaseModel):
    short_code: str
    short_url: str

@app.post("/api/v1/urls", response_model=CreateURLResponse, status_code=201)
def create_url(payload: CreateURLRequest):
    short_code = generate_short_code(k = 7)
    save_url(short_code, str(payload.url))
    return CreateURLResponse(
        short_code=short_code,
        short_url=f"http://localhost:8000/{short_code}"
    )


@app.get("/{short_code}")
def redirect(short_code: str):
    url = find_url(short_code)
    if url is not None:
        raise HTTPException(status_code=404, detail="short code not found")
    return RedirectResponse(url, status_code=302)

