# tests/conftest.py
import pytest
from app.core.config import settings

@pytest.fixture(autouse=True)
def restore_settings():
    """Snapshot and restore global settings after each test to prevent cross-test contamination."""
    snapshot = settings.model_dump().copy()
    yield
    for k, v in snapshot.items():
        setattr(settings, k, v)
