from datetime import datetime
from bson import ObjectId


def base_resume_model(user_id, title, description, latex_template_path):
    """Factory function to create a new BaseResume instance"""
    return {
        "_id": ObjectId(),
        "user_id": user_id,
        "title": title,
        "description": description,
        "latex_template_path": latex_template_path,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        # NEW: Section preferences for selective regeneration
        "section_preferences": {
            "enabled": False,  # Whether selective regeneration is enabled
            "selected_sections": [],  # List of section IDs to regenerate
            "parsed_structure": None,  # Cached parsed structure
            "last_parsed": None,  # When structure was last parsed
        },
    }
