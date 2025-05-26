"""Pytest configuration and fixtures."""

from typing import Any, Dict, Optional

import pytest

from civic_auth import AuthConfig, CookieStorage


class MockStorage(CookieStorage):
    """Mock storage for testing."""

    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        super().__init__(settings)
        self._data: Dict[str, str] = {}

    async def get(self, key: str) -> Optional[str]:
        return self._data.get(key)

    async def set(self, key: str, value: str) -> None:
        self._data[key] = value

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)

    async def clear(self) -> None:
        self._data.clear()


@pytest.fixture
def auth_config() -> AuthConfig:
    """Test auth configuration."""
    return {
        "client_id": "test-client-id",
        "redirect_url": "http://localhost:8000/auth/callback",
        "post_logout_redirect_url": "http://localhost:8000/",
    }


@pytest.fixture
def mock_storage() -> MockStorage:
    """Mock storage instance."""
    return MockStorage()
