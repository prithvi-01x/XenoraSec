# tests/conftest.py
import pytest
from app.core.config import settings
from app.core.rate_limit import rate_limiter

@pytest.fixture(autouse=True)
def restore_settings():
    """Snapshot and restore global settings after each test to prevent cross-test contamination."""
    snapshot = settings.model_dump().copy()
    rate_limiter.requests_per_minute.clear()
    rate_limiter.requests_per_hour.clear()
    yield
    for k, v in snapshot.items():
        setattr(settings, k, v)
    rate_limiter.requests_per_minute.clear()
    rate_limiter.requests_per_hour.clear()

