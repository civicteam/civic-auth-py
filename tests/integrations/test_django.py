"""Tests for Django integration."""

import os

# Configure Django settings before importing Django modules
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.django_settings")

import django

django.setup()

# noqa imports below need to come after django.setup()
from django.http import HttpResponse  # noqa: E402
from django.test import RequestFactory  # noqa: E402

from civic_auth.integrations.django import (  # noqa: E402
    CivicAuthMiddleware,
    DjangoCookieStorage,
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
