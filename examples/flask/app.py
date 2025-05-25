"""Flask example app demonstrating Civic Auth integration."""

import os
import asyncio
from flask import Flask, redirect, request, render_template_string
from dotenv import load_dotenv

from civic_auth import CivicAuth
from civic_auth_flask import (
    init_civic_auth,
    civic_auth_required,
    get_civic_auth,
    get_civic_user
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Civic Auth
PORT = int(os.getenv("PORT", 8000))
config = {
    "client_id": os.getenv("CLIENT_ID"),
    "redirect_url": f"http://localhost:{PORT}/auth/callback",
    "post_logout_redirect_url": f"http://localhost:{PORT}/",
}

# Initialize Civic Auth
init_civic_auth(app, config)

# Home page template
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Civic Auth Flask Example</title>
</head>
<body>
    <h1>Welcome to Civic Auth Flask Example</h1>
    <p>Click the button below to login with Civic Auth</p>
    <button onclick="window.location.href='/auth/login'">Login with Civic</button>
</body>
</html>
"""

# Admin page template
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin - Civic Auth Flask Example</title>
</head>
<body>
    <h1>Hello, {{ user.name }}!</h1>
    <p>Welcome to the admin area.</p>
    <p>Your email: {{ user.email }}</p>
    <p>Your ID: {{ user.id }}</p>
    <button onclick="window.location.href='/auth/logout'">Logout</button>
</body>
</html>
"""


@app.route("/")
async def home():
    """Home page - redirects to login."""
    auth = await get_civic_auth()
    if await auth.is_logged_in():
        return redirect("/admin/hello")
    return render_template_string(HOME_TEMPLATE)


@app.route("/auth/login")
async def login():
    """Redirect to Civic Auth login."""
    auth = await get_civic_auth()
    url = await auth.build_login_url()
    return redirect(url)


@app.route("/auth/callback")
async def callback():
    """Handle OAuth callback."""
    code = request.args.get("code")
    state = request.args.get("state")
    
    if not code or not state:
        return "Missing code or state parameter", 400
    
    auth = await get_civic_auth()
    try:
        await auth.resolve_oauth_access_code(code, state)
        return redirect("/admin/hello")
    except Exception as e:
        return f"Authentication failed: {str(e)}", 400


@app.route("/admin/hello")
@civic_auth_required
async def admin_hello():
    """Protected admin page."""
    user = await get_civic_user()
    return render_template_string(ADMIN_TEMPLATE, user=user)


@app.route("/auth/logout")
async def logout():
    """Logout and redirect."""
    auth = await get_civic_auth()
    url = await auth.build_logout_redirect_url()
    return redirect(url)


@app.route("/auth/logoutcallback")
async def logout_callback():
    """Handle logout callback."""
    state = request.args.get("state")
    print(f"Logout-callback: state={state}")
    
    # Clear any remaining session data
    auth = await get_civic_auth()
    await auth.clear_tokens()
    
    return redirect("/")


if __name__ == "__main__":
    # Run with asyncio support
    import hypercorn.asyncio
    from hypercorn.config import Config
    
    config = Config()
    config.bind = [f"localhost:{PORT}"]
    
    print(f"Server is running on http://localhost:{PORT}")
    asyncio.run(hypercorn.asyncio.serve(app, config))