from flask import Blueprint
from controllers.auth_controller import signup, login, logout
from middlewares.auth_middleware import guest_only

auth_routes = Blueprint("auth", __name__)

auth_routes.route("/login", methods=["GET", "POST"])(guest_only(login))
auth_routes.route("/signup", methods=["GET", "POST"])(guest_only(signup))
auth_routes.route("/logout")(logout)
