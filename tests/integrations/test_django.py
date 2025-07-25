"""Tests for Django integration."""

import os
from unittest.mock import patch

# Configure Django settings before importing Django modules
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.django_settings")

import django

django.setup()

# noqa imports below need to come after django.setup()
from django.http import HttpResponse  # noqa: E402
from django.test import RequestFactory, override_settings  # noqa: E402

from civic_auth.integrations.django import (  # noqa: E402
    CivicAuthMiddleware,
    DjangoCookieStorage,
    callback,
    civic_auth_required,
    get_auth_urls,
)


class TestDjangoIntegration:
    """Test Django integration."""

    def test_get_auth_urls(self):
        """Test Django URL patterns creation."""
        urls = get_auth_urls()

        # Check that all required URLs are present
        url_names = [url.name for url in urls]
        assert "civic_auth_login" in url_names
        assert "civic_auth_callback" in url_names
        assert "civic_auth_logout" in url_names
        assert "civic_auth_logout_callback" in url_names
        assert "civic_auth_user" in url_names

    def test_middleware_initialization(self):
        """Test middleware can be initialized."""

        def get_response(request):
            return HttpResponse("OK")

        middleware = CivicAuthMiddleware(get_response)
        assert middleware is not None
        assert middleware.config["client_id"] == "test-client-id"

    def test_middleware_adds_civic_auth_to_request(self):
        """Test middleware adds civic_auth to request."""

        def get_response(request):
            assert hasattr(request, "civic_auth")
            assert hasattr(request, "civic_storage")
            return HttpResponse("OK")

        middleware = CivicAuthMiddleware(get_response)
        factory = RequestFactory()
        request = factory.get("/")

        response = middleware(request)
        assert response.status_code == 200

    def test_civic_auth_required_decorator(self):
        """Test the civic_auth_required decorator blocks unauthenticated requests."""
        from civic_auth import CivicAuth

        @civic_auth_required
        def protected_view(request):
            return HttpResponse("Protected content")

        factory = RequestFactory()
        request = factory.get("/protected")

        # Add middleware attributes to simulate middleware running
        config = {
            "client_id": "test-client-id",
            "redirect_url": "http://localhost:8000/auth/callback",
        }
        request.civic_storage = DjangoCookieStorage(request)
        request.civic_auth = CivicAuth(request.civic_storage, config)

        # Should return 401 because user is not logged in
        response = protected_view(request)
        assert response.status_code == 401
        assert response.content == b"Unauthorized"

    @patch("civic_auth.integrations.django.run_async")
    def test_callback_default_redirect(self, mock_run_async):
        """Test callback redirects to default '/' when no custom redirect URL is set."""
        from civic_auth import CivicAuth

        # Mock the async auth operations
        mock_run_async.return_value = None

        factory = RequestFactory()
        request = factory.get("/auth/callback?code=test-code&state=test-state")

        # Add middleware attributes to simulate middleware running
        config = {
            "client_id": "test-client-id",
            "redirect_url": "http://localhost:8000/auth/callback",
        }
        request.civic_storage = DjangoCookieStorage(request)
        request.civic_auth = CivicAuth(request.civic_storage, config)

        response = callback(request)

        # Should redirect to default "/"
        assert response.status_code == 302
        assert response.url == "/"

    @override_settings(CIVIC_AUTH_SUCCESS_REDIRECT_URL="/dashboard")
    @patch("civic_auth.integrations.django.run_async")
    def test_callback_custom_redirect(self, mock_run_async):
        """Test callback redirects to custom URL when CIVIC_AUTH_SUCCESS_REDIRECT_URL is set."""
        from civic_auth import CivicAuth

        # Mock the async auth operations
        mock_run_async.return_value = None

        factory = RequestFactory()
        request = factory.get("/auth/callback?code=test-code&state=test-state")

        # Add middleware attributes to simulate middleware running
        config = {
            "client_id": "test-client-id",
            "redirect_url": "http://localhost:8000/auth/callback",
        }
        request.civic_storage = DjangoCookieStorage(request)
        request.civic_auth = CivicAuth(request.civic_storage, config)

        response = callback(request)

        # Should redirect to custom URL
        assert response.status_code == 302
        assert response.url == "/dashboard"

    def test_callback_missing_parameters(self):
        """Test callback returns 400 when code or state parameters are missing."""
        from civic_auth import CivicAuth

        factory = RequestFactory()

        # Test missing code
        request = factory.get("/auth/callback?state=test-state")
        config = {
            "client_id": "test-client-id",
            "redirect_url": "http://localhost:8000/auth/callback",
        }
        request.civic_storage = DjangoCookieStorage(request)
        request.civic_auth = CivicAuth(request.civic_storage, config)

        response = callback(request)
        assert response.status_code == 400
        assert "Missing code or state parameter" in response.content.decode()

        # Test missing state
        request = factory.get("/auth/callback?code=test-code")
        request.civic_storage = DjangoCookieStorage(request)
        request.civic_auth = CivicAuth(request.civic_storage, config)

        response = callback(request)
        assert response.status_code == 400
        assert "Missing code or state parameter" in response.content.decode()

    @patch("civic_auth.integrations.django.run_async")
    def test_callback_auth_failure(self, mock_run_async):
        """Test callback returns 400 when authentication fails."""
        from civic_auth import CivicAuth

        # Mock auth failure
        mock_run_async.side_effect = Exception("Auth failed")

        factory = RequestFactory()
        request = factory.get("/auth/callback?code=test-code&state=test-state")

        config = {
            "client_id": "test-client-id",
            "redirect_url": "http://localhost:8000/auth/callback",
        }
        request.civic_storage = DjangoCookieStorage(request)
        request.civic_auth = CivicAuth(request.civic_storage, config)

        response = callback(request)

        # Should return 400 with error message
        assert response.status_code == 400
        assert "Auth failed: Auth failed" in response.content.decode()
