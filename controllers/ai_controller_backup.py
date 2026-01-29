import os
from datetime import datetime
from typing import Optional, Dict, Any
from bson.objectid import ObjectId
from db import db
from services.claude_ai_service import ClaudeAIService
from services.latex_service import LatexService
from models.generated_asset import generated_asset_model


class AIController:
    def __init__(self):
        self.claude_service = ClaudeAIService()
        self.latex_service = LatexService()

    def process_job_application(
        self, application_id: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Main workflow to process a job application:
        1. Analyze job description
        2. Get base resume
        3. Tailor resume with Claude
        4. Compile to PDF
        5. Save to database
        """
        # Get application - handle both string and ObjectId
        try:

            application_id = ObjectId(application_id)
            # Try as string first (how it's stored from model)
            application = db.applications.find_one(
                {"_id": application_id, "user_id": user_id}
            )

            # If not found, try as ObjectId
            if not application:
                application = db.applications.find_one(
                    {"_id": ObjectId(application_id), "user_id": user_id}
                )
        except:
            application = db.applications.find_one(
                {"_id": application_id, "user_id": user_id}
            )

        if not application:
            return {"success": False, "error": "Application not found"}

        try:
            # Update status to processing - use the _id as it is stored
            db.applications.update_one(
                {"_id": ObjectId(application["_id"])},
                {
                    "$set": {
                        "status": "processing",
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            # Step 1: Analyze job description
            job_analysis = self.claude_service.analyze_job_description(
                application["job_description"]
            )

            # Step 2: Get base resume
            base_resume = self._get_base_resume(user_id)
            if not base_resume:
                raise Exception("No base resume found")

            base_latex_content = self.latex_service.read_base_resume(
                base_resume["latex_template_path"]
            )

            if not base_latex_content:
                raise Exception("Could not read base resume template")

            # Step 3: Tailor resume with Claude
            tailored_latex = self.claude_service.tailor_resume(
                base_latex_content, application["job_description"], job_analysis
            )

            # Step 4: Compile to PDF
            output_filename = (
                f"resume_{application_id}_{int(datetime.now().timestamp())}"
            )
            success, pdf_path, error = self.latex_service.compile_latex(
                tailored_latex, output_filename
            )

            if not success:
                # If compilation fails, fallback to base resume
                print(f"LaTeX compilation failed: {error}")
                print("Falling back to base resume...")

                success, pdf_path, error = self.latex_service.compile_latex(
                    base_latex_content, output_filename
                )

                if not success:
                    raise Exception(f"Even base resume compilation failed: {error}")

                tailored_latex = base_latex_content  # Use base as fallback

            # Step 5: Save generated asset to database
            tex_filename = f"{output_filename}.tex"
            tex_path = f"storage/generated/{tex_filename}"

            # Save the tex file
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tailored_latex)

            # Extract text content for storage
            content_text = self.latex_service.extract_text_from_latex(tailored_latex)

            # Create generated asset record
            asset_data = generated_asset_model(
                job_application_id=str(application_id),  # Ensure it's a string
                user_id=user_id,
                asset_type="resume",
                title=f"Tailored Resume - {job_analysis.get('position_title', 'Position')}",
                content_text=content_text,
                ai_model="claude-sonnet-4-20250514",
                pdf_path=pdf_path,
                tex_path=tex_path,
                version=1,
            )

            result = db.generated_assets.insert_one(asset_data)
            generated_asset_id = str(result.inserted_id)

            # Step 6: Update application with results - use the _id as stored
            db.applications.update_one(
                {"_id": ObjectId(application["_id"])},
                {
                    "$set": {
                        "status": "completed",
                        "company_name": job_analysis.get("company_name"),
                        "position_title": job_analysis.get("position_title"),
                        "base_resume_id": str(base_resume["_id"]),
                        "generated_resume_id": generated_asset_id,
                        "ai_analysis": job_analysis,
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            return {
                "success": True,
                "generated_asset_id": generated_asset_id,
                "pdf_path": pdf_path,
                "tex_path": tex_path,
                "job_analysis": job_analysis,
            }

        except Exception as e:
            # Update status to failed - use the _id as stored
            db.applications.update_one(
                {"_id": ObjectId(application["_id"])},
                {
                    "$set": {
                        "status": "failed",
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            return {"success": False, "error": str(e)}

    def _get_base_resume(self, user_id: str) -> Optional[Dict]:
        """Get the user's base resume, or a default one"""
        # Try to get user's base resume
        base_resume = db.base_resumes.find_one({"user_id": user_id})

        if base_resume:
            return base_resume

        # Fallback to default base resume if exists
        default_resume = db.base_resumes.find_one({"user_id": "default"})

        return default_resume

    def generate_cover_letter(
        self, application_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Generate a cover letter for a job application"""
        try:
            # Get application - handle both string and ObjectId
            application_id = ObjectId(application_id)
            try:
                application = db.applications.find_one(
                    {"_id": application_id, "user_id": user_id}
                )
                if not application:
                    application = db.applications.find_one(
                        {"_id": ObjectId(application_id), "user_id": user_id}
                    )
            except:
                application = db.applications.find_one(
                    {"_id": application_id, "user_id": user_id}
                )

            if not application:
                return {"success": False, "error": "Application not found"}

            # Get the generated resume for context
            resume_text = ""
            if application.get("generated_resume_id"):
                try:
                    generated_resume = db.generated_assets.find_one(
                        {"_id": application["generated_resume_id"]}
                    )
                    if not generated_resume:
                        generated_resume = db.generated_assets.find_one(
                            {"_id": ObjectId(application["generated_resume_id"])}
                        )
                except:
                    generated_resume = db.generated_assets.find_one(
                        {"_id": application["generated_resume_id"]}
                    )

                if generated_resume:
                    resume_text = generated_resume.get("content_text", "")

            # Generate cover letter
            cover_letter_text = self.claude_service.generate_cover_letter(
                resume_text,
                application["job_description"],
                application.get("ai_analysis"),
            )

            # Save as generated asset
            asset_data = generated_asset_model(
                job_application_id=str(application_id),  # Ensure it's a string
                user_id=user_id,
                asset_type="cover_letter",
                title=f"Cover Letter - {application.get('position_title', 'Position')}",
                content_text=cover_letter_text,
                ai_model="claude-sonnet-4-20250514",
                version=1,
            )

            result = db.generated_assets.insert_one(asset_data)

            return {
                "success": True,
                "asset_id": str(result.inserted_id),
                "content": cover_letter_text,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
