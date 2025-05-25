# Civic Auth Django Example

This example demonstrates how to integrate Civic Auth with a Django application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
# Edit .env with your Civic Auth client ID
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start the development server:
```bash
python manage.py runserver
```

5. Visit http://localhost:8000 and click "Login with Civic"

## Features

- Middleware-based integration
- Protected views with `@civic_auth_required` decorator
- Async view support with `@civic_auth_required_async`
- Template rendering with user data
- API endpoints returning JSON

## Project Structure

- `civic_example/` - Django project configuration
  - `settings.py` - Contains CIVIC_AUTH configuration
  - `urls.py` - Root URL configuration
- `civic_app/` - Django app with Civic Auth integration
  - `views.py` - View functions with auth examples
  - `urls.py` - URL patterns for auth endpoints
  - `templates/` - HTML templates

## Key Components

### Middleware Setup (settings.py)
```python
MIDDLEWARE = [
    # ... other middleware
    'civic_auth.integrations.django.CivicAuthMiddleware',
]

CIVIC_AUTH = {
    'client_id': os.getenv('CLIENT_ID'),
    'oauth_server': os.getenv('AUTH_SERVER', 'https://auth.civic.com/oauth'),
    'redirect_url': f'http://localhost:{PORT}/auth/callback',
    'post_logout_redirect_url': f'http://localhost:{PORT}/',
}
```

### Protected Views
```python
from civic_auth.integrations.django import civic_auth_required

@civic_auth_required
def protected_view(request):
    user = request.civic_user
    return render(request, 'protected.html', {'user': user})
```

### Async Views
```python
from civic_auth.integrations.django import civic_auth_required_async

@civic_auth_required_async
async def async_protected(request):
    user = request.civic_user
    return JsonResponse({'user': user})
```