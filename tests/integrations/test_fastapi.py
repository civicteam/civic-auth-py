"""Tests for FastAPI integration."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from civic_auth.integrations.fastapi import create_auth_dependencies, create_auth_router


def test_create_auth_router(auth_config):
    """Test auth router creation."""
    router = create_auth_router(auth_config)

    # Check routes are registered
    routes = [route.path for route in router.routes]
    assert "/auth/login" in routes
    assert "/auth/callback" in routes
    assert "/auth/logout" in routes
    assert "/auth/user" in routes
    assert "/auth/logoutcallback" in routes


def test_create_auth_dependencies(auth_config):
    """Test auth dependencies creation."""
    civic_auth_dep, get_current_user, require_auth = create_auth_dependencies(auth_config)

    assert civic_auth_dep is not None
    assert get_current_user is not None
    assert require_auth is not None


def test_auth_endpoints(auth_config):
    """Test auth endpoints basic functionality."""
    app = FastAPI()
    auth_router = create_auth_router(auth_config)
    app.include_router(auth_router)

    client = TestClient(app)

    # Test login redirect
    response = client.get("/auth/login", follow_redirects=False)
    assert response.status_code == 302
    assert "location" in response.headers

    # Test logout redirect
    response = client.get("/auth/logout", follow_redirects=False)
    assert response.status_code == 302

    # Test user endpoint (should fail without auth)
    response = client.get("/auth/user")
    assert response.status_code == 401
