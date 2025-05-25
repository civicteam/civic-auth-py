# Civic Auth Python SDK

Python SDK for Civic Auth server-side authentication. This library provides a Python implementation that matches the API of the [Node.js Civic Auth library](https://github.com/civicteam/civic-auth).

## Installation

```bash
pip install civic-auth
```

For specific framework support:

```bash
# Flask
pip install "civic-auth[flask]"

# FastAPI
pip install "civic-auth[fastapi]"

# Django
pip install "civic-auth[django]"
```

## Quick Start

### Core Usage

```python
from civic_auth import CivicAuth
from civic_auth.storage import AuthStorage

# Implement your storage backend
class MyStorage(AuthStorage):
    async def get(self, key: str) -> Optional[str]:
        # Implement get from your storage
        pass
    
    async def set(self, key: str, value: str) -> None:
        # Implement set to your storage
        pass
    
    async def delete(self, key: str) -> None:
        # Implement delete from your storage
        pass
    
    async def clear(self) -> None:
        # Implement clear all keys
        pass

# Configure and use
config = {
    "client_id": "your-client-id",
    "redirect_url": "http://localhost:3000/auth/callback",
    "post_logout_redirect_url": "http://localhost:3000/"
}

storage = MyStorage()
civic_auth = CivicAuth(storage, config)

# Build login URL
login_url = await civic_auth.build_login_url()

# Exchange code for tokens
tokens = await civic_auth.resolve_oauth_access_code(code, state)

# Get authenticated user
user = await civic_auth.get_user()

# Check if logged in
is_logged_in = await civic_auth.is_logged_in()

# Build logout URL
logout_url = await civic_auth.build_logout_redirect_url()
```

### Flask Integration

```python
from flask import Flask, redirect
from civic_auth.integrations.flask import (
    init_civic_auth,
    civic_auth_required,
    get_civic_auth,
    get_civic_user
)

app = Flask(__name__)

# Configure Civic Auth
config = {
    "client_id": "your-client-id",
    "redirect_url": "http://localhost:5000/auth/callback",
    "post_logout_redirect_url": "http://localhost:5000/"
}

# Initialize Civic Auth
init_civic_auth(app, config)

@app.route("/auth/login")
async def login():
    auth = await get_civic_auth()
    url = await auth.build_login_url()
    return redirect(url)

@app.route("/auth/callback")
async def callback():
    code = request.args.get("code")
    state = request.args.get("state")
    
    auth = await get_civic_auth()
    await auth.resolve_oauth_access_code(code, state)
    return redirect("/protected")

@app.route("/protected")
@civic_auth_required
async def protected():
    user = await get_civic_user()
    return f"Hello {user['name']}!"
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from civic_auth.integrations.fastapi import (
    create_civic_auth_dependency,
    create_auth_router,
    get_current_user,
    require_auth
)

app = FastAPI()

# Configure Civic Auth
config = {
    "client_id": "your-client-id",
    "redirect_url": "http://localhost:8000/auth/callback",
    "post_logout_redirect_url": "http://localhost:8000/"
}

# Add auth router
auth_router = create_auth_router(config)
app.include_router(auth_router)

# Protected endpoint
@app.get("/protected", dependencies=[Depends(require_auth)])
async def protected(user = Depends(get_current_user)):
    return {"message": f"Hello {user['name']}!"}
```

### Django Integration

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'civic_auth.integrations.django.CivicAuthMiddleware',
]

CIVIC_AUTH = {
    'client_id': 'your-client-id',
    'redirect_url': 'http://localhost:8000/auth/callback',
    'post_logout_redirect_url': 'http://localhost:8000/',
}

# views.py
from civic_auth.integrations.django import civic_auth_required, get_civic_auth

def login(request):
    auth = get_civic_auth(request)
    url = run_async(auth.build_login_url())
    return redirect(url)

@civic_auth_required
def protected_view(request):
    user = request.civic_user
    return render(request, 'protected.html', {'user': user})
```

## API Reference

### CivicAuth Class

#### Methods

- `get_user()` - Get the authenticated user information
- `get_tokens()` - Get the stored OAuth tokens
- `is_logged_in()` - Check if user is authenticated
- `build_login_url(scopes=None)` - Build OAuth authorization URL
- `resolve_oauth_access_code(code, state)` - Exchange auth code for tokens
- `refresh_tokens()` - Refresh access tokens
- `build_logout_redirect_url()` - Build logout URL
- `clear_tokens()` - Clear all stored tokens

### Types

```python
from civic_auth.types import BaseUser, AuthConfig, Tokens

# BaseUser
{
    "id": str,
    "email": Optional[str],
    "username": Optional[str],
    "name": Optional[str],
    "given_name": Optional[str],
    "family_name": Optional[str],
    "picture": Optional[str],
    "updated_at": Optional[datetime]
}

# AuthConfig
{
    "client_id": str,  # Required
    "redirect_url": str,  # Required
    "oauth_server": Optional[str],  # Default: "https://auth.civic.com/oauth"
    "post_logout_redirect_url": Optional[str],
    "scopes": Optional[List[str]]  # Default: ["openid", "email", "profile"]
}

# Tokens
{
    "access_token": str,
    "id_token": str,
    "refresh_token": Optional[str],
    "token_type": str,
    "expires_in": Optional[int],
    "scope": Optional[str]
}
```

## Examples

See the [examples](examples/) directory for complete working examples:

- [Flask Example](examples/flask/)
- [FastAPI Example](examples/fastapi/)
- [Django Example](examples/django/)

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/civicteam/civic-auth-py.git
cd civic-auth-py

# Install development dependencies
pip install -e ".[dev]"
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=civic_auth
```

### Linting and Formatting

```bash
# Format code
black civic_auth tests

# Lint
ruff civic_auth tests

# Type checking
mypy civic_auth
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- GitHub Issues: [https://github.com/civicteam/civic-auth-py/issues](https://github.com/civicteam/civic-auth-py/issues)
- Documentation: [https://docs.civic.com](https://docs.civic.com)