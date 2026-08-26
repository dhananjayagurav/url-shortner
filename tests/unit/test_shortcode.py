"""Unit tests for URL shortcode generation logic"""

from app.shortcode import generate_short_code

def test_generate_short_code_length():
    assert len(generate_short_code()) == 7

def test_generate_short_code_is_alphanumeric():
    assert generate_short_code().isalnum()

def test_generate_short_code_is_configurable():
    assert len(generate_short_code(length=10)) == 10

