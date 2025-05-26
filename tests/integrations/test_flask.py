"""Tests for Flask integration."""

from flask import Flask

from civic_auth.integrations.flask import create_auth_blueprint, init_civic_auth


def test_init_civic_auth(auth_config):
    """Test Flask app initialization."""
    app = Flask(__name__)
    app.secret_key = "test-secret"

    # Initialize Civic Auth
    init_civic_auth(app, auth_config)

    # Check that before_request and after_request handlers are registered
    assert len(app.before_request_funcs[None]) > 0
    assert len(app.after_request_funcs[None]) > 0


def test_create_auth_blueprint(auth_config):
    """Test auth blueprint creation."""
    auth_bp = create_auth_blueprint(auth_config)

    # Check routes are registered
    rules = list(auth_bp.deferred_functions)
    assert len(rules) > 0  # Blueprint has routes registered


def test_auth_endpoints(auth_config):
    """Test auth endpoints basic functionality."""
    app = Flask(__name__)
    app.secret_key = "test-secret"
    app.config["TESTING"] = True

    init_civic_auth(app, auth_config)
    auth_bp = create_auth_blueprint(auth_config)
    app.register_blueprint(auth_bp)

    with app.test_client() as client:
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
