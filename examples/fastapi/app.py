"""FastAPI example app demonstrating Civic Auth integration."""

import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

from civic_auth import BaseUser, CivicAuth
from civic_auth.integrations.fastapi import create_auth_dependencies, create_auth_router

load_dotenv()

app = FastAPI(title="Civic Auth FastAPI Example")

# Configure Civic Auth
PORT = int(os.getenv("PORT", 8000))
config = {
    "client_id": os.getenv("CLIENT_ID"),
    "redirect_url": f"http://localhost:{PORT}/auth/callback",
    "post_logout_redirect_url": f"http://localhost:{PORT}/",
}

# Create Civic Auth dependencies
civic_auth_dep, get_current_user, require_auth = create_auth_dependencies(config)

# Add auth router
auth_router = create_auth_router(config)
app.include_router(auth_router)

# Home page HTML
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Civic Auth FastAPI Example</title>
</head>
<body>
    <h1>Welcome to Civic Auth FastAPI Example</h1>
    <p>Click the button below to login with Civic Auth</p>
    <button onclick="window.location.href='/auth/login'">Login with Civic</button>
</body>
</html>
"""

# Admin page HTML template
def admin_html(user: BaseUser) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Admin - Civic Auth FastAPI Example</title>
</head>
<body>
    <h1>Hello, {user.get('name', 'User')}!</h1>
    <p>Welcome to the admin area.</p>
    <p>Your email: {user.get('email', 'N/A')}</p>
    <p>Your ID: {user.get('id', 'N/A')}</p>
    <button onclick="window.location.href='/auth/logout'">Logout</button>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home(civic_auth: CivicAuth = Depends(civic_auth_dep)):
    """Home page - shows login button or redirects if logged in."""
    if await civic_auth.is_logged_in():
        return RedirectResponse(url="/admin/hello")
    return HOME_HTML


@app.get("/admin/hello", response_class=HTMLResponse, dependencies=[Depends(require_auth)])
async def admin_hello(user: BaseUser = Depends(get_current_user)):
    """Protected admin page."""
    return admin_html(user)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=PORT)
