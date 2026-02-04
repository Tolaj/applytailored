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
        # UPDATED: Hierarchical section preferences
        "section_preferences": {
            "enabled": False,  # Master toggle for selective regeneration
            "sections": {
                # Structure: section_name -> subsection -> items
                # Example:
                # "experience": {
                #     "selected": true,  # Is this section selected?
                #     "subsections": {
                #         "job_0": {  # NCR Corporation
                #             "selected": true,
                #             "items": ["item_0", "item_1"]  # Selected bullet points
                #         },
                #         "job_1": {  # Georgia Tech Research Institute
                #             "selected": false,
                #             "items": []
                #         }
                #     }
                # },
                # "education": {
                #     "selected": false,
                #     "subsections": {}
                # }
            },
            "parsed_structure": None,  # Cached HTML structure
            "last_parsed": None,  # When structure was last parsed
        },
    }
