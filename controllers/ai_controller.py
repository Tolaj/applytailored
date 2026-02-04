"""
Enhanced AI Controller with hierarchical selective regeneration
Processes: Section -> Subsection -> Item selections
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson.objectid import ObjectId
from db import db
from services.claude_ai_service import ClaudeAIService
from services.latex_service import LatexService
from services.latex_parser_service import EnhancedLatexParser
from models.generated_asset import generated_asset_model


class AIController:
    def __init__(self):
        self.claude_service = ClaudeAIService()
        self.latex_service = LatexService()
        self.parser = EnhancedLatexParser()

    def process_job_application(
        self, application_id: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Main workflow with hierarchical selective regeneration

        Checks if base resume has section preferences enabled with hierarchical structure.
        If enabled, only regenerates selected sections/subsections/items.
        """
        try:
            application_id = ObjectId(application_id)
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

        try:
            # Update status
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

            # Step 3: Check for hierarchical selective regeneration
            section_prefs = base_resume.get("section_preferences", {})
            selective_enabled = section_prefs.get("enabled", False)
            sections_config = section_prefs.get("sections", {})

            if selective_enabled and sections_config:
                # USE HIERARCHICAL SELECTIVE REGENERATION
                print(f"Using hierarchical selective regeneration")

                tailored_latex = self._regenerate_hierarchical(
                    base_latex_content,
                    sections_config,
                    application["job_description"],
                    job_analysis,
                )

                regeneration_type = "hierarchical_selective"
                regeneration_details = self._get_regeneration_summary(sections_config)

            else:
                # USE FULL REGENERATION
                print("Using full resume regeneration")
                tailored_latex = self.claude_service.tailor_resume(
                    base_latex_content, application["job_description"], job_analysis
                )
                regeneration_type = "full"
                regeneration_details = None

            # Step 4: Compile to PDF
            output_filename = (
                f"resume_{application_id}_{int(datetime.now().timestamp())}"
            )
            success, pdf_path, error = self.latex_service.compile_latex(
                tailored_latex, output_filename
            )

            if not success:
                print(f"LaTeX compilation failed: {error}")
                print("Falling back to base resume...")

                success, pdf_path, error = self.latex_service.compile_latex(
                    base_latex_content, output_filename
                )

                if not success:
                    raise Exception(f"Even base resume compilation failed: {error}")

                tailored_latex = base_latex_content

            # Step 5: Save generated asset
            tex_filename = f"{output_filename}.tex"
            tex_path = f"storage/generated/{tex_filename}"

            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tailored_latex)

            content_text = self.latex_service.extract_text_from_latex(tailored_latex)

            # Create title based on regeneration type
            if regeneration_type == "hierarchical_selective":
                title = f"Tailored Resume (Selective) - {job_analysis.get('position_title', 'Position')}"
            else:
                title = f"Tailored Resume - {job_analysis.get('position_title', 'Position')}"

            asset_data = generated_asset_model(
                job_application_id=str(application_id),
                user_id=user_id,
                asset_type="resume",
                title=title,
                content_text=content_text,
                ai_model="claude-sonnet-4-20250514",
                pdf_path=pdf_path,
                tex_path=tex_path,
                version=1,
            )

            result = db.generated_assets.insert_one(asset_data)
            generated_asset_id = str(result.inserted_id)

            # Step 6: Update application
            update_data = {
                "status": "completed",
                "company_name": job_analysis.get("company_name"),
                "position_title": job_analysis.get("position_title"),
                "base_resume_id": str(base_resume["_id"]),
                "generated_resume_id": generated_asset_id,
                "ai_analysis": job_analysis,
                "updated_at": datetime.utcnow(),
                "regeneration_type": regeneration_type,
            }

            if regeneration_details:
                update_data["regeneration_details"] = regeneration_details

            db.applications.update_one(
                {"_id": ObjectId(application["_id"])}, {"$set": update_data}
            )

            return {
                "success": True,
                "generated_asset_id": generated_asset_id,
                "pdf_path": pdf_path,
                "tex_path": tex_path,
                "job_analysis": job_analysis,
                "regeneration_type": regeneration_type,
                "regeneration_details": regeneration_details,
            }

        except Exception as e:
            db.applications.update_one(
                {"_id": ObjectId(application["_id"])},
                {
                    "$set": {
                        "status": "failed",
                        "updated_at": datetime.utcnow(),
                    }
                },
            )

            import traceback

            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def _regenerate_hierarchical(
        self,
        base_latex: str,
        sections_config: Dict[str, Any],
        job_description: str,
        job_analysis: Dict[str, Any],
    ) -> str:
        """
        Regenerate only selected sections/subsections/items

        sections_config structure:
        {
            "experience": {
                "selected": true,
                "subsections": {
                    "experience_0": {
                        "selected": true,
                        "items": ["item_0_0", "item_0_1"]
                    }
                }
            }
        }
        """
        # Parse resume into hierarchical structure
        parsed = self.parser.parse_resume_to_hierarchy(base_latex)

        result_latex = base_latex

        # Process each selected section
        for section in parsed["sections"]:
            section_id = section.section_id
            section_config = sections_config.get(section_id, {})

            if not section_config.get("selected", False):
                continue  # Skip unselected sections

            print(f"Processing section: {section.title}")

            # Process subsections
            subsections_config = section_config.get("subsections", {})

            for subsection in section.subsections:
                subsection_id = subsection.subsection_id
                subsection_config = subsections_config.get(subsection_id, {})

                # Skip if subsection not selected and no items selected
                if not subsection_config.get(
                    "selected", False
                ) and not subsection_config.get("items", []):
                    continue

                print(f"  Processing subsection: {subsection.title}")

                selected_items = subsection_config.get("items", [])

                if selected_items:
                    # Regenerate specific items
                    print(f"    Regenerating {len(selected_items)} items")

                    for item in subsection.items:
                        if item.item_id in selected_items:
                            # Regenerate this specific item
                            new_content = self.claude_service.regenerate_bullet_point(
                                item.content,
                                job_description,
                                job_analysis,
                                {
                                    "section": section.title,
                                    "subsection": subsection.title,
                                },
                            )

                            # Replace in LaTeX
                            result_latex = result_latex.replace(item.latex, new_content)

                elif subsection_config.get("selected", False):
                    # Regenerate entire subsection
                    print(f"    Regenerating entire subsection")

                    new_subsection = self.claude_service.regenerate_subsection(
                        subsection.latex,
                        section.section_id,
                        job_description,
                        job_analysis,
                        {"subsection_title": subsection.title},
                    )

                    # Replace in LaTeX
                    result_latex = result_latex.replace(
                        subsection.latex, new_subsection
                    )

        return result_latex

    def _get_regeneration_summary(
        self, sections_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a summary of what was regenerated"""
        summary = {"sections": [], "total_subsections": 0, "total_items": 0}

        for section_id, section_data in sections_config.items():
            if section_data.get("selected", False):
                section_summary = {"section_id": section_id, "subsections": []}

                for subsection_id, subsection_data in section_data.get(
                    "subsections", {}
                ).items():
                    items = subsection_data.get("items", [])
                    if subsection_data.get("selected", False) or items:
                        section_summary["subsections"].append(
                            {"subsection_id": subsection_id, "items_count": len(items)}
                        )
                        summary["total_subsections"] += 1
                        summary["total_items"] += len(items)

                summary["sections"].append(section_summary)

        return summary

    def _get_base_resume(self, user_id: str) -> Optional[Dict]:
        """Get the user's active base resume"""
        base_resume = db.base_resumes.find_one({"user_id": user_id, "is_active": True})

        if base_resume:
            return base_resume

        base_resume = db.base_resumes.find_one({"user_id": user_id})
        if base_resume:
            return base_resume

        default_resume = db.base_resumes.find_one({"user_id": "default"})
        return default_resume

    def generate_cover_letter(
        self, application_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Generate a cover letter for a job application"""
        try:
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

            cover_letter_text = self.claude_service.generate_cover_letter(
                resume_text,
                application["job_description"],
                application.get("ai_analysis"),
            )

            asset_data = generated_asset_model(
                job_application_id=str(application_id),
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

    def parse_base_resume(self, resume_id: str, user_id: str) -> Dict[str, Any]:
        """
        Parse a base resume into hierarchical structure
        (For backward compatibility with routes that still use this)
        """
        try:
            resume = db.base_resumes.find_one(
                {"_id": ObjectId(resume_id), "user_id": user_id}
            )

            if not resume:
                return {"success": False, "error": "Resume not found"}

            latex_content = self.latex_service.read_base_resume(
                resume["latex_template_path"]
            )

            if not latex_content:
                return {"success": False, "error": "Could not read resume file"}

            parsed = self.parser.parse_resume_to_hierarchy(latex_content)
            structure = self.parser.serialize_structure(parsed["sections"])

            return {
                "success": True,
                "structure": structure,
                "header": parsed["header"],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}
