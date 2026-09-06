"""Phase 4: alternative ID generation strategies, compared side by side.
These are intentionally NOT wired into the live UrlRepository -- Phase 3's
DB-sequence + Base62 approach stays in production. This module exists so
the comparison in docs/07-id-generation.md is grounded in code you've
actually run, not just prose.

Notice only three of the four approaches from the book share the
interface below. The current production approach (DB sequence + Base62)
needs a database Session to generate anything at all -- it cannot stand
alone, which is exactly the distributed-systems trade-off this phase is
about."""

import random
import string
import threading
import time
import uuid
from abc import ABC, abstractmethod

from app.core.base62 import encode
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.url import Url


class IdGenerator(ABC):
    """Common interface: any coordination-free generator can produce a
    ready-to-use short code with no arguments and no external state."""

    @abstractmethod
    def generate(self) -> str:
        ...


class RandomBase62Generator(IdGenerator):
    """The Phase 1 approach, done properly this time: still random, but
    now meant to be paired with retry-on-collision at the point of
    insertion, instead of hoping a collision never happens."""

    _ALPHABET = string.ascii_letters + string.digits
    _LENGTH = 7

    def generate(self) -> str:
        return "".join(random.choices(self._ALPHABET, k=self._LENGTH))


class UuidBase62Generator(IdGenerator):
    """A UUID is 128 bits of (mostly) randomness -- far more than a short
    code needs. Encoding it through your own Base62 function compresses
    it, but even compressed it will be much longer than 7 characters:
    that length is the direct cost of needing no coordinator at all."""

    def generate(self) -> str:
        random_128_bit_int = uuid.uuid4().int
        return encode(random_128_bit_int)


class SnowflakeGenerator(IdGenerator):
    """A simplified version of Twitter's Snowflake scheme: pack a
    millisecond timestamp, a machine id, and a per-millisecond sequence
    number into one integer, then Base62-encode it. No database round
    trip for the ID itself -- only the machine_id needs to be assigned
    uniquely per running instance, once, out of band."""

    _EPOCH_MS = 1_700_000_000_000  # a fixed custom epoch, not the Unix epoch
    _MACHINE_ID_BITS = 10
    _SEQUENCE_BITS = 12
    _MAX_MACHINE_ID = (1 << _MACHINE_ID_BITS) - 1
    _MAX_SEQUENCE = (1 << _SEQUENCE_BITS) - 1

    def __init__(self, machine_id: int):
        if not (0 <= machine_id <= self._MAX_MACHINE_ID):
            raise ValueError(f"machine_id must be between 0 and {self._MAX_MACHINE_ID}")
        self._machine_id = machine_id
        self._lock = threading.Lock()
        self._last_timestamp_ms = -1
        self._sequence = 0

    def _current_millis(self) -> int:
        return int(time.time() * 1000)

    def generate(self) -> str:
        with self._lock:
            now = self._current_millis()

            if now < self._last_timestamp_ms:
                raise RuntimeError("Clock moved backwards -- refusing to generate an ID")

            if now == self._last_timestamp_ms:
                self._sequence = (self._sequence + 1) & self._MAX_SEQUENCE
                if self._sequence == 0:
                    # This millisecond's sequence space is exhausted; wait for the next one.
                    while now <= self._last_timestamp_ms:
                        now = self._current_millis()
            else:
                self._sequence = 0

            self._last_timestamp_ms = now

            timestamp_part = (now - self._EPOCH_MS) << (self._MACHINE_ID_BITS + self._SEQUENCE_BITS)
            machine_part = self._machine_id << self._SEQUENCE_BITS
            snowflake_id = timestamp_part | machine_part | self._sequence

            return encode(snowflake_id)


def create_with_random_retry(
    db: Session, generator: RandomBase62Generator, original_url: str, max_attempts: int = 5
) -> Url:
    """Demonstrates the retry-on-collision pattern the Phase 1 random
    generator never had. Not wired into the live repository -- this is
    here so you can see, and test, what 'handle the collision properly'
    actually looks like."""
    for _ in range(max_attempts):
        short_code = generator.generate()
        url = Url(short_code=short_code, original_url=original_url)
        db.add(url)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            continue
        db.commit()
        db.refresh(url)
        return url
    raise RuntimeError(f"Failed to generate a unique short_code after {max_attempts} attempts")

