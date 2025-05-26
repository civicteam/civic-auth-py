"""Civic Auth Python SDK for server-side authentication."""

from .auth import CivicAuth
from .storage import CookieStorage, AuthStorage
from .types import BaseUser, AuthConfig, Tokens, CookieSettings

__version__ = "0.1.0"
__all__ = [
    "CivicAuth",
    "CookieStorage",
    "AuthStorage",
    "BaseUser",
    "AuthConfig",
    "Tokens",
    "CookieSettings",
]
