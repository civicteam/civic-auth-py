"""
Django settings for civic_example project.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition - Minimal setup for Civic Auth example
INSTALLED_APPS = [
    'django.contrib.contenttypes',  # Required by Django internals
    'django.contrib.staticfiles',  # Keep for serving static files
    'civic_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'civic_auth.integrations.django.CivicAuthMiddleware',  # Add Civic Auth middleware
]

ROOT_URLCONF = 'civic_example.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'civic_example.wsgi.application'

# Database - Not needed for this example
DATABASES = {}

# Password validation - Not needed since we're using Civic Auth
AUTH_PASSWORD_VALIDATORS = []

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Civic Auth Configuration
PORT = int(os.getenv('PORT', 8000))
CIVIC_AUTH = {
    'client_id': os.getenv('CLIENT_ID'),
    'redirect_url': f'http://localhost:{PORT}/auth/callback',
    'post_logout_redirect_url': f'http://localhost:{PORT}/',
}
