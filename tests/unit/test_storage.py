"""Unit tests for storage module"""

from app.storage import save_url, find_url
import pytest

def test_save_and_find_url():
    save_url("123abcD", "https://example.com/long/url/test_suite")
    assert find_url("123abcD") == "https://example.com/long/url/test_suite"

def test_find_retruns_none_for_unknown_url():
    assert find_url("non-existent") is None

def test_creates_an_entry_in_store():
    save_url("shared-code", "https://example.com/a")

@pytest.mark.xfail(reason = "module level _url dict is shared across all tests; fixed in step 1.3")
def test_z_expects_a_clean_store():
    assert find_url("shared-code") is None


