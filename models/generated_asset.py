# models/generated_asset.py
from datetime import datetime
from bson import ObjectId


def generated_asset_model(
    job_application_id,
    user_id,
    asset_type,
    title,
    content_text,
    ai_model,
    pdf_path=None,
    tex_path=None,
    version=1,
):
    """Factory function to create a new GeneratedAsset instance"""
    return {
        "_id": str(ObjectId()),
        "job_application_id": job_application_id,
        "user_id": user_id,
        "type": asset_type,  # resume / cover_letter / cold_email / followup / question_answer
        "title": title,
        "content_text": content_text,
        "pdf_path": pdf_path,
        "tex_path": tex_path,
        "ai_model": ai_model,
        "version": version,
        "created_at": datetime.utcnow(),
    }
