"""FastAPI application entrypoint."""
from fastapi import FastAPI

from app.api.urls import router as urls_router

app = FastAPI(title="URL Shortener", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(urls_router)
