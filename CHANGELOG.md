# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-01-26

### Added
- Initial release of civic-auth Python SDK
- Core CivicAuth class for OAuth/OIDC authentication
- Storage abstraction for session/cookie management
- Framework integrations:
  - FastAPI integration with dependencies and router
  - Flask integration with middleware and blueprint
  - Django integration with middleware and URL patterns
- OIDC discovery support for dynamic endpoint configuration
- Automatic token refresh functionality
- Type hints throughout the codebase
- Comprehensive examples for each framework
- MIT License

### Features
- Multiple authentication methods support (email, social, passkeys, wallets)
- Privacy-preserving authentication
- Flexible storage backend system
- Framework-agnostic core library
- Optional framework dependencies

[0.1.0]: https://github.com/civicteam/civic-auth-py/releases/tag/v0.1.0