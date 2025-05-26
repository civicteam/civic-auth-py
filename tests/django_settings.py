"""Minimal Django settings for testing."""

SECRET_KEY = "test-secret-key-for-testing-only"
DEBUG = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
]

MIDDLEWARE = [
    "civic_auth.integrations.django.CivicAuthMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Civic Auth configuration
CIVIC_AUTH = {
    "client_id": "test-client-id",
    "redirect_url": "http://localhost:8000/auth/callback",
}

# Required Django settings
USE_TZ = True
ROOT_URLCONF = []
