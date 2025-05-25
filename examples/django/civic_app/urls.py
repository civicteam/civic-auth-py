"""URL patterns for civic_app."""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/login', views.login, name='login'),
    path('auth/callback', views.auth_callback, name='auth_callback'),
    path('admin/hello', views.admin_hello, name='admin_hello'),
    path('auth/logout', views.logout, name='logout'),
    path('auth/logoutcallback', views.logout_callback, name='logout_callback'),
    
    # API endpoints
    path('api/user', views.api_user, name='api_user'),
    path('api/protected', views.async_protected, name='async_protected'),
]