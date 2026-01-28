from flask import Blueprint, render_template
from middlewares.auth_middleware import require_auth

dashboard_routes = Blueprint("dashboard", __name__)


@dashboard_routes.route("/dashboard")
@require_auth
def dashboard():
    return render_template("dashboard/index.html")
