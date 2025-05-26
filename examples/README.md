# Civic Auth Python Examples

This directory contains example applications demonstrating how to integrate Civic Auth with popular Python web frameworks.

## Examples

- **FastAPI** - Modern async web API framework
- **Flask** - Lightweight WSGI web application framework  
- **Django** - High-level Python web framework

Each example includes:
- Complete working application
- Authentication flow implementation
- Protected routes demonstration
- User information display

## Installation

Install the base library:
```bash
pip install civic-auth
```

Install with framework support:
```bash
# For FastAPI
pip install civic-auth[fastapi]

# For Flask
pip install civic-auth[flask]

# For Django
pip install civic-auth[django]

# For all frameworks
pip install civic-auth[all]
```

## Configuration

All examples use environment variables for configuration:

```bash
CLIENT_ID=your_civic_client_id
PORT=8000  # Optional, defaults to 8000
```

## Running the Examples

Each example can be run from its directory:

```bash
# FastAPI
cd fastapi
pip install -r requirements.txt
python app.py

# Flask
cd flask
pip install -r requirements.txt
python app.py

# Django
cd django
pip install -r requirements.txt
python manage.py runserver
```

All examples will be available at http://localhost:8000