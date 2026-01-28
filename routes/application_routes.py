from flask import Blueprint
from middlewares.auth_middleware import require_auth
from controllers import application_controller

application_routes = Blueprint("application_routes", __name__)


@application_routes.route("/applications", methods=["GET"])
@require_auth
def list_applications():
    return application_controller.list_applications()


@application_routes.route("/applications", methods=["POST"])
@require_auth
def create_application():
    return application_controller.create_application()


@application_routes.route("/applications/<app_id>", methods=["GET"])
@require_auth
def application_detail(app_id):
    return application_controller.application_detail(app_id)


@application_routes.route("/applications/<app_id>/regenerate", methods=["POST"])
@require_auth
def regenerate_resume(app_id):
    return application_controller.regenerate_resume(app_id)


@application_routes.route("/applications/<app_id>/cover-letter", methods=["POST"])
@require_auth
def generate_cover_letter(app_id):
    return application_controller.generate_cover_letter(app_id)


@application_routes.route("/assets/<asset_id>/download", methods=["GET"])
@require_auth
def download_asset(asset_id):
    return application_controller.download_asset(asset_id)
