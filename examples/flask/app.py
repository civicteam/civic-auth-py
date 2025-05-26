"""Flask example app demonstrating Civic Auth integration."""

import os

from dotenv import load_dotenv
from flask import Flask, render_template_string

from civic_auth.integrations.flask import (
    civic_auth_required,
    create_auth_blueprint,
    get_civic_auth,
    get_civic_user,
    init_civic_auth,
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

# Add auth blueprint
auth_bp = create_auth_blueprint(config)
app.register_blueprint(auth_bp)

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
    <h1>Hello, {{ user.name or user.email }}!</h1>
    <p>Welcome to the admin area.</p>
    <p>Your email: {{ user.email }}</p>
    <p>Your ID: {{ user.id }}</p>
    <button onclick="window.location.href='/auth/logout'">Logout</button>
</body>
</html>
"""


@app.route("/")
async def home():
    """Home page - shows login button or redirects if logged in."""
    from flask import redirect
    auth = await get_civic_auth()
    if await auth.is_logged_in():
        return redirect("/admin/hello")
    return render_template_string(HOME_TEMPLATE)


@app.route("/admin/hello")
@civic_auth_required
async def admin_hello():
    """Protected admin page."""
    user = await get_civic_user()
    return render_template_string(ADMIN_TEMPLATE, user=user)


if __name__ == "__main__":
    # Run Flask app
    app.run(host="0.0.0.0", port=PORT, debug=True)
