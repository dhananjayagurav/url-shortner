"""FastAPI application entrypoint."""
from fastapi import FastAPI

from app.api.urls import router as urls_router
from app.core.database import Base, engine


app = FastAPI(title="URL Shortener", version="0.1.0")
app.include_router(urls_router)


@app.get("/health")
def health():
    return {"status": "ok"}