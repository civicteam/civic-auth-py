"""Views for Civic Auth Django example."""

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .civic_auth_django import (
    civic_auth_required,
    civic_auth_required_async,
    get_civic_auth,
    get_civic_user_sync,
    run_async
)


def home(request):
    """Home page view."""
    auth = get_civic_auth(request)
    
    # Check if user is logged in
    is_logged_in = run_async(auth.is_logged_in())
    
    if is_logged_in:
        return redirect('/admin/hello')
    
    return render(request, 'home.html')


def login(request):
    """Redirect to Civic Auth login."""
    auth = get_civic_auth(request)
    url = run_async(auth.build_login_url())
    
    # Create redirect response and apply cookies
    response = redirect(url)
    if hasattr(request, 'civic_storage'):
        request.civic_storage.apply_to_response(response)
    
    return response


@csrf_exempt
def auth_callback(request):
    """Handle OAuth callback."""
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if not code or not state:
        return HttpResponse("Missing code or state parameter", status=400)
    
    auth = get_civic_auth(request)
    try:
        run_async(auth.resolve_oauth_access_code(code, state))
        
        # Create redirect response and apply cookies
        response = redirect('/admin/hello')
        if hasattr(request, 'civic_storage'):
            request.civic_storage.apply_to_response(response)
        
        return response
    except Exception as e:
        return HttpResponse(f"Authentication failed: {str(e)}", status=400)


@civic_auth_required
def admin_hello(request):
    """Protected admin page."""
    user = request.civic_user
    return render(request, 'admin.html', {'user': user})


def logout(request):
    """Logout and redirect."""
    auth = get_civic_auth(request)
    url = run_async(auth.build_logout_redirect_url())
    
    # Create redirect response and apply cookies
    response = redirect(url)
    if hasattr(request, 'civic_storage'):
        request.civic_storage.apply_to_response(response)
    
    return response


@csrf_exempt
def logout_callback(request):
    """Handle logout callback."""
    state = request.GET.get('state')
    print(f"Logout-callback: state={state}")
    
    # Clear any remaining session data
    auth = get_civic_auth(request)
    run_async(auth.clear_tokens())
    
    return redirect('/')


# API endpoint example using async view
async def api_user(request):
    """API endpoint to get current user (async view)."""
    auth = get_civic_auth(request)
    
    if not await auth.is_logged_in():
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    user = await auth.get_user()
    return JsonResponse(user)


# Alternative protected view using async decorator
@civic_auth_required_async
async def async_protected(request):
    """Async protected view example."""
    user = request.civic_user
    return JsonResponse({
        'message': f'Hello {user.get("name", "User")}!',
        'user': user
    })