"""
Controller for managing base resume section preferences
"""

from flask import request, jsonify, g, render_template
from bson.objectid import ObjectId
from datetime import datetime
from db import db
from controllers.ai_controller import AIController

ai_controller = AIController()


def view_section_preferences(resume_id):
    """
    View and manage section preferences for a base resume
    """
    resume = db.base_resumes.find_one(
        {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]}
    )

    if not resume:
        return "Resume not found", 404

    return render_template(
        "resume/section_preferences.html", resume=resume, resume_id=str(resume["_id"])
    )


def load_resume_sections(resume_id):
    """
    Parse resume and return sections for selection
    """
    try:
        result = ai_controller.parse_base_resume(resume_id, g.user["user_id"])

        if result["success"]:
            # Cache the parsed structure in the database
            db.base_resumes.update_one(
                {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]},
                {
                    "$set": {
                        "section_preferences.parsed_structure": result["sections"],
                        "section_preferences.last_parsed": datetime.utcnow(),
                    }
                },
            )

            return jsonify(
                {
                    "success": True,
                    "sections": result["sections"],
                    "header": result["header"],
                }
            )
        else:
            return jsonify(result), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def save_section_preferences(resume_id):
    """
    Save which sections should be regenerated for this resume

    Request body:
    {
        "enabled": true,
        "selected_sections": ["experience_123", "skills_456"]
    }
    """
    try:
        data = request.json

        enabled = data.get("enabled", False)
        selected_sections = data.get("selected_sections", [])

        # Update resume with preferences
        result = db.base_resumes.update_one(
            {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]},
            {
                "$set": {
                    "section_preferences.enabled": enabled,
                    "section_preferences.selected_sections": selected_sections,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        if result.matched_count == 0:
            return jsonify({"success": False, "error": "Resume not found"}), 404

        return jsonify(
            {
                "success": True,
                "message": "Section preferences saved",
                "enabled": enabled,
                "selected_count": len(selected_sections),
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def get_section_preferences(resume_id):
    """
    Get saved section preferences for a resume
    """
    try:
        resume = db.base_resumes.find_one(
            {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]},
            {"section_preferences": 1},
        )

        if not resume:
            return jsonify({"success": False, "error": "Resume not found"}), 404

        preferences = resume.get(
            "section_preferences",
            {"enabled": False, "selected_sections": [], "parsed_structure": None},
        )

        return jsonify({"success": True, "preferences": preferences})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
