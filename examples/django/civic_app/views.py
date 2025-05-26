"""Views for Civic Auth Django example."""

from django.http import JsonResponse
from django.shortcuts import redirect, render

from civic_auth.integrations.django import civic_auth_required, get_civic_auth, run_async


def home(request):
    """Home page view - shows login button or redirects if logged in."""
    auth = get_civic_auth(request)
    is_logged_in = run_async(auth.is_logged_in())

    if is_logged_in:
        return redirect('/admin/hello')

    return render(request, 'home.html')


@civic_auth_required
def admin_hello(request):
    """Protected admin page."""
    user = request.civic_user
    return render(request, 'admin.html', {'user': user})


@civic_auth_required
def api_user(request):
    """API endpoint to get current user."""
    user = request.civic_user
    return JsonResponse({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'picture': user.picture
    })
