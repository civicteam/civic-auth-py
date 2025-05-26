"""URL configuration for civic_example project."""

from django.urls import include, path

urlpatterns = [
    path('', include('civic_app.urls')),
]
