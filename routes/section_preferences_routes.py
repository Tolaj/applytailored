"""
Routes for managing resume section preferences with HTML preview
"""

from flask import Blueprint
from middlewares.auth_middleware import require_auth
from controllers.section_preferences_controller import (
    view_section_preferences,
    load_resume_sections,
    save_section_preferences,
    get_section_preferences,
    get_resume_html_preview,  # Add this import
)

section_preferences_routes = Blueprint("section_preferences", __name__)


@section_preferences_routes.route("/resume/<resume_id>/preferences", methods=["GET"])
@require_auth
def preferences_page(resume_id):
    """View page for managing section preferences"""
    return view_section_preferences(resume_id)


@section_preferences_routes.route("/resume/<resume_id>/sections", methods=["GET"])
@require_auth
def get_sections(resume_id):
    """Get parsed sections from resume"""
    return load_resume_sections(resume_id)


@section_preferences_routes.route("/resume/<resume_id>/preferences", methods=["POST"])
@require_auth
def save_preferences(resume_id):
    """Save section preferences"""
    return save_section_preferences(resume_id)


@section_preferences_routes.route(
    "/resume/<resume_id>/preferences/get", methods=["GET"]
)
@require_auth
def get_preferences(resume_id):
    """Get saved section preferences"""
    return get_section_preferences(resume_id)


# NEW: HTML Preview endpoint
@section_preferences_routes.route("/resume/<resume_id>/html-preview", methods=["GET"])
@require_auth
def get_html_preview(resume_id):
    """Get HTML preview of resume for interactive editing"""
    return get_resume_html_preview(resume_id)
