from app.core.database import SessionLocal
from app.core.id_generators import IdGenerator, create_with_random_retry


class _FixedThenNewGenerator(IdGenerator):
    """Test helper: yields a specific sequence of codes, so we can force
    a collision deterministically instead of hoping random() collides."""

    def __init__(self, codes: list[str]):
        self._codes = iter(codes)

    def generate(self) -> str:
        return next(self._codes)


def test_retries_past_a_collision():
    db = SessionLocal()
    try:
        first = create_with_random_retry(db, _FixedThenNewGenerator(["retry-a"]), "https://example.com/one")
        assert first.short_code == "retry-a"

        # "retry-a" is now taken; the generator offers it again before a fresh code.
        second = create_with_random_retry(
            db, _FixedThenNewGenerator(["retry-a", "retry-b"]), "https://example.com/two"
        )
        assert second.short_code == "retry-b"
    finally:
        db.close()