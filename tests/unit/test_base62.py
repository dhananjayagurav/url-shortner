import pytest
from app.core.base62 import decode, encode


@pytest.mark.parametrize(
    "num, code",
    [
        (0, "0"),
        (1, "1"),
        (61, "Z"),
        (62, "10"),
        (123456, "w7e"),
    ],
)
def test_encode_known_values(num, code):
    assert encode(num) == code


@pytest.mark.parametrize(
    "num, code",
    [
        (0, "0"),
        (1, "1"),
        (61, "Z"),
        (62, "10"),
        (123456, "w7e"),
    ],
)
def test_decode_known_values(num, code):
    assert decode(code) == num


@pytest.mark.parametrize("num", [0, 1, 61, 62, 3844, 123456, 999_999_999, 2**62])
def test_round_trip(num):
    assert decode(encode(num)) == num


def test_encode_negative_raises():
    with pytest.raises(ValueError):
        encode(-1)


def test_decode_empty_string_raises():
    with pytest.raises(ValueError):
        decode("")


def test_decode_invalid_character_raises():
    with pytest.raises(ValueError):
        decode("abc!")