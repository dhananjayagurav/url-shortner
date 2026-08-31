"""Seed the urls table with a large number of rows -- not part of the app,
a one-off developer tool for query-planning (EXPLAIN) and later load-test
experiments."""
import random
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import insert

from app.core.database import SessionLocal
from app.models.url import Url

_ALPHABET = string.ascii_letters + string.digits


def _random_code(length: int = 7) -> str:
    return "".join(random.choices(_ALPHABET, k=length))


def seed(n: int = 500_000, batch_size: int = 5_000) -> None:
    db = SessionLocal()
    seen: set[str] = set()
    try:
        inserted = 0
        while inserted < n:
            batch = []
            while len(batch) < batch_size and inserted + len(batch) < n:
                code = _random_code()
                if code in seen:
                    continue
                seen.add(code)
                batch.append(
                    {"short_code": code, "original_url": f"https://example.com/seed/{code}"}
                )
            db.execute(insert(Url), batch)
            db.commit()
            inserted += len(batch)
            print(f"inserted {inserted}/{n}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()