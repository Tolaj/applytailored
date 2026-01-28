# models/base_resume.py
from datetime import datetime
from bson import ObjectId


def base_resume_model(user_id, title, description, latex_template_path):
    """Factory function to create a new BaseResume instance"""
    return {
        "_id": str(ObjectId()),
        "user_id": user_id,
        "title": title,
        "description": description,
        "latex_template_path": latex_template_path,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
