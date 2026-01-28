from datetime import datetime
from bson import ObjectId


def job_application_model(
    user_id, job_description, company_name=None, position_title=None
):
    """Factory function to create a new JobApplication instance"""
    return {
        "_id": ObjectId(),  # ← Changed from str(ObjectId())
        "user_id": user_id,
        "job_description": job_description,
        "company_name": company_name,
        "position_title": position_title,
        "status": "draft",
        "base_resume_id": None,
        "generated_resume_id": None,
        "ai_analysis": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
