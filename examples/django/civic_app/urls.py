"""URL patterns for civic_app."""

from django.urls import include, path

from civic_auth.integrations.django import get_auth_urls

from . import views

urlpatterns = [
    # App views
    path('', views.home, name='home'),
    path('admin/hello/', views.admin_hello, name='admin_hello'),
    path('api/user/', views.api_user, name='api_user'),

    # Include Civic Auth URLs
    path('', include(get_auth_urls())),
]
