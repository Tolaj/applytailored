from flask import Blueprint, render_template
from controllers.profile_controller import profile
from controllers.base_resume_controller import (
    create_base_resume,
    delete_base_resume,
    activate_base_resume,
    download_base_resume,
    download_class_file,
)
from middlewares.auth_middleware import require_auth

profile_routes = Blueprint("profile", __name__)


@profile_routes.route("/profile")
@require_auth
def profile_page():
    return profile()


@profile_routes.route("/base-resumes", methods=["POST"])
@require_auth
def upload_base_resume():
    return create_base_resume()


@profile_routes.route("/base-resumes/<resume_id>", methods=["DELETE"])
@require_auth
def delete_resume(resume_id):
    return delete_base_resume(resume_id)


@profile_routes.route("/base-resumes/<resume_id>/activate", methods=["POST"])
@require_auth
def activate_resume(resume_id):
    return activate_base_resume(resume_id)


@profile_routes.route("/base-resumes/<resume_id>/download", methods=["GET"])
@require_auth
def download_resume(resume_id):
    return download_base_resume(resume_id)


@profile_routes.route("/base-resumes/<resume_id>/download-class", methods=["GET"])
@require_auth
def download_cls(resume_id):
    return download_class_file(resume_id)
