from app.security.rate_limit import RateLimiter


def test_rate_limiter_allows_requests_within_limit():
    limiter = RateLimiter(limit=2, window_seconds=60)

    assert limiter.allow("client-1")
    assert limiter.allow("client-1")
    assert not limiter.allow("client-1")


def test_rate_limiter_isolated_by_key():
    limiter = RateLimiter(limit=1, window_seconds=60)

    assert limiter.allow("client-1")
    assert not limiter.allow("client-1")
    assert limiter.allow("client-2")
