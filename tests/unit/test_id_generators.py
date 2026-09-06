import pytest

from app.core.id_generators import (
    IdGenerator,
    RandomBase62Generator,
    SnowflakeGenerator,
    UuidBase62Generator,
)
from app.core.base62 import decode


def test_cannot_instantiate_abstract_base():
    with pytest.raises(TypeError):
        IdGenerator()


def test_random_generator_produces_expected_shape():
    code = RandomBase62Generator().generate()
    assert len(code) == 7
    assert code.isalnum()


def test_uuid_generator_produces_decodable_base62():
    code = UuidBase62Generator().generate()
    assert decode(code) >= 0  # round-trips through your own decode without error


def test_snowflake_generator_rejects_invalid_machine_id():
    with pytest.raises(ValueError):
        SnowflakeGenerator(machine_id=-1)
    with pytest.raises(ValueError):
        SnowflakeGenerator(machine_id=2000)  # exceeds 10-bit range (max 1023)


def test_snowflake_ids_are_unique_across_rapid_calls():
    gen = SnowflakeGenerator(machine_id=1)
    codes = {gen.generate() for _ in range(500)}
    assert len(codes) == 500  # no duplicates, even generated back-to-back


def test_snowflake_ids_are_monotonically_increasing():
    gen = SnowflakeGenerator(machine_id=1)
    values = [decode(gen.generate()) for _ in range(50)]
    assert values == sorted(values)