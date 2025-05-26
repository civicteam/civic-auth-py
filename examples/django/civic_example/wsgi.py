"""
WSGI config for civic_example project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'civic_example.settings')

application = get_wsgi_application()
