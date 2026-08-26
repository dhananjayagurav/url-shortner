"""Step 1.3 - Each test builds it's own URLStore, so there is no shared 
state between tests at all. So no clean-up, no fixture, no xfail"""

from app.storage import URLStore

def test_save_and_find():
    store = URLStore()
    store.save_url("abc1234","https://example.com/some/long/url")
    assert store.find_url("abc1234") == str("https://example.com/some/long/url")

def test_find_returns_none_for_unknown_url():
    store = URLStore()
    assert store.find_url("does_not_exists") is None

def test_two_instance_do_not_share_state():
    store_a = URLStore()
    store_b = URLStore()
    store_a.save_url("shared_code", "https://example.com/a")
    assert store_b.find_url("shared_code") is None



