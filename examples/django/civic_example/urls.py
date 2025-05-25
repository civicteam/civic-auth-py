"""URL configuration for civic_example project."""

from django.urls import path, include

urlpatterns = [
    path('', include('civic_app.urls')),
]