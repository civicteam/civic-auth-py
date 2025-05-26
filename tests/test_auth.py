"""Tests for CivicAuth core functionality."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from civic_auth import CivicAuth
from civic_auth.exceptions import ConfigurationError
from civic_auth.storage import AuthStorage
from civic_auth.utils import generate_pkce_challenge, generate_random_string

# Mock endpoints to avoid network calls during tests
MOCK_ENDPOINTS = {
    "authorization_endpoint": "https://auth.civic.com/oauth/authorize",
    "token_endpoint": "https://auth.civic.com/oauth/token",
    "end_session_endpoint": "https://auth.civic.com/oauth/logout",
    "issuer": "https://auth.civic.com/oauth",
}


class MockStorage(AuthStorage):
    """Mock storage implementation for testing."""

    def __init__(self):
        self.data = {}

    async def get(self, key: str):
        return self.data.get(key)

    async def set(self, key: str, value: str):
        self.data[key] = value

    async def delete(self, key: str):
        self.data.pop(key, None)

    async def clear(self):
        self.data.clear()


@pytest.fixture
def mock_storage():
    """Create mock storage instance."""
    return MockStorage()


@pytest.fixture
def config():
    """Create test configuration."""
    return {
        "client_id": "test-client-id",
        "redirect_url": "http://localhost:3000/auth/callback",
        "post_logout_redirect_url": "http://localhost:3000/",
    }


@pytest.fixture
async def civic_auth(mock_storage, config):
    """Create CivicAuth instance for testing."""
    auth = CivicAuth(mock_storage, config)
    yield auth
    await auth.client.aclose()


class TestCivicAuth:
    """Test CivicAuth class."""

    def test_config_validation(self, mock_storage):
        """Test configuration validation."""
        # Missing client_id
        with pytest.raises(ConfigurationError, match="client_id is required"):
            CivicAuth(mock_storage, {"redirect_url": "http://test"})

        # Missing redirect_url
        with pytest.raises(ConfigurationError, match="redirect_url is required"):
            CivicAuth(mock_storage, {"client_id": "test"})

    @pytest.mark.asyncio
    async def test_build_login_url(self, civic_auth, mock_storage):
        """Test building login URL."""
        # Mock the discover_endpoints to avoid network calls
        civic_auth._endpoints = MOCK_ENDPOINTS

        url = await civic_auth.build_login_url()

        assert url.startswith("https://auth.civic.com/oauth/authorize")
        assert "client_id=test-client-id" in url
        assert "redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fauth%2Fcallback" in url
        assert "response_type=code" in url
        assert "scope=openid+email+profile" in url

        # Check PKCE verifier stored
        assert await mock_storage.get("civic_auth_pkce_verifier") is not None

        # Check state stored
        assert await mock_storage.get("civic_auth_state") is not None

        # Check nonce stored
        assert await mock_storage.get("civic_auth_nonce") is not None

    @pytest.mark.asyncio
    async def test_build_login_url_custom_scopes(self, civic_auth):
        """Test building login URL with custom scopes."""
        # Mock the discover_endpoints to avoid network calls
        civic_auth._endpoints = MOCK_ENDPOINTS

        url = await civic_auth.build_login_url(scopes=["openid", "custom"])
        assert "scope=openid+custom" in url

    @pytest.mark.asyncio
    async def test_is_logged_in_false(self, civic_auth):
        """Test is_logged_in when not authenticated."""
        assert await civic_auth.is_logged_in() is False

    @pytest.mark.asyncio
    async def test_is_logged_in_true(self, civic_auth, mock_storage):
        """Test is_logged_in when authenticated."""
        # Create a valid JWT token
        exp = datetime.now(timezone.utc) + timedelta(hours=1)
        token_data = {
            "sub": "user-123",
            "email": "test@example.com",
            "name": "Test User",
            "exp": int(exp.timestamp()),
        }
        id_token = jwt.encode(token_data, "secret", algorithm="HS256")

        await mock_storage.set("civic_auth_id_token", id_token)
        assert await civic_auth.is_logged_in() is True

    @pytest.mark.asyncio
    async def test_get_user(self, civic_auth, mock_storage):
        """Test getting user from token."""
        # Create a valid JWT token
        exp = datetime.now(timezone.utc) + timedelta(hours=1)
        token_data = {
            "sub": "user-123",
            "email": "test@example.com",
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "exp": int(exp.timestamp()),
        }
        id_token = jwt.encode(token_data, "secret", algorithm="HS256")

        await mock_storage.set("civic_auth_id_token", id_token)

        user = await civic_auth.get_user()
        assert user is not None
        assert user["id"] == "user-123"
        assert user["email"] == "test@example.com"
        assert user["name"] == "Test User"
        assert user["given_name"] == "Test"
        assert user["family_name"] == "User"

    @pytest.mark.asyncio
    async def test_get_user_expired_token(self, civic_auth, mock_storage):
        """Test getting user with expired token."""
        # Create an expired JWT token
        exp = datetime.now(timezone.utc) - timedelta(hours=1)
        token_data = {"sub": "user-123", "exp": int(exp.timestamp())}
        id_token = jwt.encode(token_data, "secret", algorithm="HS256")

        await mock_storage.set("civic_auth_id_token", id_token)

        user = await civic_auth.get_user()
        assert user is None

    @pytest.mark.asyncio
    async def test_clear_tokens(self, civic_auth, mock_storage):
        """Test clearing tokens."""
        # Set some tokens
        await mock_storage.set("civic_auth_id_token", "test-id-token")
        await mock_storage.set("civic_auth_access_token", "test-access-token")
        await mock_storage.set("civic_auth_refresh_token", "test-refresh-token")

        await civic_auth.clear_tokens()

        assert await mock_storage.get("civic_auth_id_token") is None
        assert await mock_storage.get("civic_auth_access_token") is None
        assert await mock_storage.get("civic_auth_refresh_token") is None

    @pytest.mark.asyncio
    async def test_build_logout_redirect_url(self, civic_auth, mock_storage):
        """Test building logout URL."""
        # Mock the discover_endpoints to avoid network calls
        civic_auth._endpoints = MOCK_ENDPOINTS

        await mock_storage.set("civic_auth_id_token", "test-id-token")

        url = await civic_auth.build_logout_redirect_url()

        assert url.startswith("https://auth.civic.com/oauth/logout")
        assert "post_logout_redirect_uri=http%3A%2F%2Flocalhost%3A3000%2F" in url
        assert "id_token_hint=test-id-token" in url

        # Check tokens were cleared
        assert await mock_storage.get("civic_auth_id_token") is None


class TestUtils:
    """Test utility functions."""

    def test_generate_random_string(self):
        """Test random string generation."""
        s1 = generate_random_string(32)
        s2 = generate_random_string(32)

        assert len(s1) == 32
        assert len(s2) == 32
        assert s1 != s2  # Should be different

    def test_generate_pkce_challenge(self):
        """Test PKCE challenge generation."""
        pkce = generate_pkce_challenge()

        assert "code_verifier" in pkce
        assert "code_challenge" in pkce
        assert "code_challenge_method" in pkce
        assert pkce["code_challenge_method"] == "S256"
        assert len(pkce["code_verifier"]) == 128
        assert len(pkce["code_challenge"]) > 0
