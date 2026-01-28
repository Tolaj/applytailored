from flask import Blueprint
from controllers.profile_controller import profile
from middlewares.auth_middleware import require_auth

profile_routes = Blueprint("profile", __name__)


@profile_routes.route("/profile")
@require_auth
def profile_page():
    return profile()
