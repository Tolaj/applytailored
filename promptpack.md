# PromptPack Output

**Root:** `/Users/swapnil/Documents/Projects/applytailored`
**Generated:** 2026-01-29T14:32:46.362Z

---

## 1) Folder Structure

```txt
.
├─ app.py
├─ config.py
├─ controllers/
│  ├─ ai_controller_backup.py
│  ├─ ai_controller.py
│  ├─ application_controller.py
│  ├─ auth_controller.py
│  ├─ base_resume_controller.py
│  ├─ dashboard_controller.py
│  ├─ profile_controller.py
│  └─ section_preferences_controller.py
├─ db.py
├─ middlewares/
│  └─ auth_middleware.py
├─ models/
│  ├─ base_resume.py
│  ├─ generated_asset.py
│  ├─ job_application.py
│  └─ user.py
├─ promptpack.md
├─ public/
├─ QUICK_START.md
├─ README.md
├─ requirements.txt
├─ routes/
│  ├─ application_routes.py
│  ├─ auth_routes.py
│  ├─ dashboard_routes.py
│  ├─ profile_routes.py
│  └─ section_preferences_routes.py
├─ seed_database.py
├─ services/
│  ├─ claude_ai_service_backup.py
│  ├─ claude_ai_service.py
│  ├─ latex_parser_service.py
│  └─ latex_service.py
├─ storage/
│  ├─ base_resumes/
│  │  ├─ a31e559f-8d9c-4389-a562-2e0b7314bf0e.tex
│  │  └─ base_resume_template.tex
│  └─ generated/
│     ├─ resume_697b6c657e75610931541e23_1769696371.pdf
│     └─ resume_697b6c657e75610931541e23_1769696371.tex
└─ views/
   ├─ applications/
   │  ├─ detail.html
   │  ├─ index.html
   │  └─ modal.html
   ├─ auth/
   │  ├─ login.html
   │  └─ signup.html
   ├─ dashboard/
   │  └─ index.html
   ├─ layouts/
   │  ├─ auth.html
   │  ├─ dashboard.html
   │  └─ signup.html
   ├─ partials/
   │  ├─ navbar.html
   │  └─ sidebar.html
   ├─ profile/
   │  └─ index.html
   └─ resume/
      └─ section_preferences.html
```

<!-- PAGE BREAK: FILE CONTENTS BELOW -->

## 2) File Contents


### app.py

```python
from flask import Flask, app
from config import Config
from routes.auth_routes import auth_routes
from routes.dashboard_routes import dashboard_routes
from routes.application_routes import application_routes

from routes.profile_routes import profile_routes

from routes.section_preferences_routes import section_preferences_routes


def create_app():
    app = Flask(__name__, template_folder="views")  # <--- specify template folder
    app.config.from_object(Config)

    @app.route("/")
    def index():
        return "Flask app is running 🚀"

    app.register_blueprint(auth_routes)
    app.register_blueprint(dashboard_routes)
    app.register_blueprint(profile_routes)
    app.register_blueprint(application_routes)

    app.register_blueprint(section_preferences_routes)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

```

### config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    JWT_SECRET = os.getenv("JWT_SECRET", "jwt-secret-key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "applytailored")

```

### controllers/ai_controller_backup.py

```python
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

```

### controllers/ai_controller.py

```python
"""
Enhanced AI Controller with automatic selective regeneration based on saved preferences
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson.objectid import ObjectId
from db import db
from services.claude_ai_service import ClaudeAIService
from services.latex_service import LatexService
from services.latex_parser_service import LatexParserService
from models.generated_asset import generated_asset_model


class AIController:
    def __init__(self):
        self.claude_service = ClaudeAIService()
        self.latex_service = LatexService()
        self.parser_service = LatexParserService()

    def parse_base_resume(self, resume_id: str, user_id: str) -> Dict[str, Any]:
        """
        Parse a base resume into selectable sections
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

            parsed = self.parser_service.parse_resume(latex_content)

            sections_for_ui = []
            for section in parsed["sections"]:
                section_info = {
                    "id": f"{section.section_type}_{section.start_pos}",
                    "type": section.section_type,
                    "title": section.title,
                    "preview": self.parser_service.get_section_preview(section),
                    "has_subsections": len(section.subsections) > 0,
                    "subsections": [],
                }

                for subsection in section.subsections:
                    subsection_info = {
                        "id": f"sub_{subsection.start_pos}",
                        "title": subsection.title,
                        "lines": subsection.lines,
                        "line_count": len(subsection.lines),
                    }
                    section_info["subsections"].append(subsection_info)

                sections_for_ui.append(section_info)

            return {
                "success": True,
                "parsed_structure": parsed,
                "sections": sections_for_ui,
                "header": parsed["header"],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_job_application(
        self, application_id: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Main workflow to process a job application.

        NEW BEHAVIOR: Checks if base resume has section preferences enabled.
        If enabled, only regenerates selected sections. Otherwise, regenerates entire resume.
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
            # Update status to processing
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

            # Step 3: Check if selective regeneration is enabled
            section_prefs = base_resume.get("section_preferences", {})
            selective_enabled = section_prefs.get("enabled", False)
            selected_sections = section_prefs.get("selected_sections", [])

            if selective_enabled and selected_sections:
                # USE SELECTIVE REGENERATION
                print(
                    f"Using selective regeneration for {len(selected_sections)} sections"
                )

                # Parse resume
                parsed = self.parser_service.parse_resume(base_latex_content)

                # Regenerate only selected sections
                regenerated = {}
                for section in parsed["sections"]:
                    section_id = f"{section.section_type}_{section.start_pos}"

                    if section_id in selected_sections:
                        print(f"Regenerating section: {section.title}")
                        new_content = self.claude_service.regenerate_section(
                            section_content=section.content,
                            section_type=section.section_type,
                            job_description=application["job_description"],
                            job_analysis=job_analysis,
                            context={
                                "section_title": section.title,
                                "has_subsections": len(section.subsections) > 0,
                            },
                        )
                        regenerated[section_id] = new_content

                # Rebuild LaTeX with regenerated sections
                tailored_latex = self.parser_service.rebuild_latex(
                    original_content=base_latex_content,
                    parsed_structure=parsed,
                    selected_sections={s: True for s in selected_sections},
                    regenerated_sections=regenerated,
                )

                regeneration_type = "selective"

            else:
                # USE FULL REGENERATION (original behavior)
                print("Using full resume regeneration")
                tailored_latex = self.claude_service.tailor_resume(
                    base_latex_content, application["job_description"], job_analysis
                )
                regeneration_type = "full"

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

            # Step 5: Save generated asset to database
            tex_filename = f"{output_filename}.tex"
            tex_path = f"storage/generated/{tex_filename}"

            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tailored_latex)

            content_text = self.latex_service.extract_text_from_latex(tailored_latex)

            # Create title based on regeneration type
            if regeneration_type == "selective":
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

            # Step 6: Update application with results
            update_data = {
                "status": "completed",
                "company_name": job_analysis.get("company_name"),
                "position_title": job_analysis.get("position_title"),
                "base_resume_id": str(base_resume["_id"]),
                "generated_resume_id": generated_asset_id,
                "ai_analysis": job_analysis,
                "updated_at": datetime.utcnow(),
                "regeneration_type": regeneration_type,  # Track which method was used
            }

            if regeneration_type == "selective":
                update_data["regenerated_sections"] = selected_sections

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
                "sections_regenerated": (
                    selected_sections if regeneration_type == "selective" else None
                ),
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

            return {"success": False, "error": str(e)}

    def _get_base_resume(self, user_id: str) -> Optional[Dict]:
        """Get the user's base resume, or a default one"""
        # Try to get user's active base resume
        base_resume = db.base_resumes.find_one({"user_id": user_id, "is_active": True})

        if base_resume:
            return base_resume

        # Try any user resume
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

```

### controllers/application_controller.py

```python
from flask import render_template, request, redirect, g, jsonify
from bson.objectid import ObjectId
from db import db
from models.job_application import job_application_model
from controllers.ai_controller import AIController
import os


ai_controller = AIController()


def list_applications():
    """List all applications for the current user"""
    apps = list(
        db.applications.find({"user_id": g.user["user_id"]}).sort("created_at", -1)
    )
    return render_template("applications/index.html", applications=apps)


def create_application():
    """Create a new job application and process it with AI"""
    job_description = request.form.get("job_description")

    if not job_description:
        return redirect("/applications")

    # Create application
    application = job_application_model(
        user_id=g.user["user_id"],
        job_description=job_description,
    )

    result = db.applications.insert_one(application)
    application_id = str(result.inserted_id)

    # Trigger AI processing in background
    # For now, we'll do it synchronously, but you could use Celery/Redis for async
    try:
        ai_result = ai_controller.process_job_application(
            application_id, g.user["user_id"]
        )

        if not ai_result["success"]:
            print(f"AI processing error: {ai_result.get('error')}")
    except Exception as e:
        print(f"Error during AI processing: {e}")

    return redirect(f"/applications/{application_id}")


def application_detail(app_id):
    """View detailed application with generated assets"""
    # Try to find by string ID first, then ObjectId
    try:
        app = db.applications.find_one({"_id": app_id, "user_id": g.user["user_id"]})

        # If not found, try as ObjectId
        if not app:
            app = db.applications.find_one(
                {"_id": ObjectId(app_id), "user_id": g.user["user_id"]}
            )
    except:
        app = db.applications.find_one({"_id": app_id, "user_id": g.user["user_id"]})

    if not app:
        return redirect("/applications")

    # Get generated assets for this application
    generated_assets = list(
        db.generated_assets.find(
            {"job_application_id": str(app["_id"]), "user_id": g.user["user_id"]}
        ).sort("created_at", -1)
    )

    return render_template(
        "applications/detail.html", application=app, generated_assets=generated_assets
    )


def regenerate_resume(app_id):
    """Regenerate resume for an application"""
    app = db.applications.find_one(
        {"_id": ObjectId(app_id), "user_id": g.user["user_id"]}
    )

    if not app:
        return jsonify({"success": False, "error": "Application not found"}), 404

    try:
        result = ai_controller.process_job_application(app_id, g.user["user_id"])

        if result["success"]:
            return jsonify(
                {
                    "success": True,
                    "message": "Resume regenerated successfully",
                    "pdf_path": result.get("pdf_path"),
                }
            )
        else:
            return (
                jsonify(
                    {"success": False, "error": result.get("error", "Unknown error")}
                ),
                500,
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def generate_cover_letter(app_id):
    """Generate cover letter for an application"""
    app = db.applications.find_one(
        {"_id": ObjectId(app_id), "user_id": g.user["user_id"]}
    )

    if not app:
        return jsonify({"success": False, "error": "Application not found"}), 404

    try:
        result = ai_controller.generate_cover_letter(app_id, g.user["user_id"])

        if result["success"]:
            return jsonify(
                {
                    "success": True,
                    "message": "Cover letter generated successfully",
                    "content": result.get("content"),
                }
            )
        else:
            return (
                jsonify(
                    {"success": False, "error": result.get("error", "Unknown error")}
                ),
                500,
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def download_asset(asset_id):
    """Download generated asset (PDF or TEX)"""
    from flask import send_file

    asset = db.generated_assets.find_one(
        {"_id": ObjectId(asset_id), "user_id": g.user["user_id"]}
    )
    if not asset:
        return "Not found", 404

    file_type = request.args.get("type", "pdf")

    if file_type == "tex":
        file_path = asset.get("tex_path")
        ext = "tex"
    else:
        file_path = asset.get("pdf_path")
        ext = "pdf"

    if not file_path:
        return "File not available", 404

    if not os.path.exists(file_path):
        return "File not found on disk", 404

    return send_file(
        file_path, as_attachment=True, download_name=f"{asset['title']}.{ext}"
    )


def delete_asset(asset_id):
    """Delete a single generated asset"""
    asset = db.generated_assets.find_one(
        {"_id": ObjectId(asset_id), "user_id": g.user["user_id"]}
    )
    if not asset:
        return jsonify({"success": False, "error": "Asset not found"}), 404

    # Delete files from disk
    for file_path in [asset.get("pdf_path"), asset.get("tex_path")]:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

    # Delete from database
    db.generated_assets.delete_one({"_id": ObjectId(asset_id)})
    return jsonify({"success": True})


def delete_application(app_id):
    """Delete an application and all its associated assets"""
    # Find application
    app = db.applications.find_one(
        {"_id": ObjectId(app_id), "user_id": g.user["user_id"]}
    )
    if not app:
        return jsonify({"success": False, "error": "Application not found"}), 404

    # Find all assets for this application
    assets = list(
        db.generated_assets.find(
            {"job_application_id": str(app_id), "user_id": g.user["user_id"]}
        )
    )

    # Delete all asset files
    for asset in assets:
        for file_path in [asset.get("pdf_path"), asset.get("tex_path")]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")

    # Delete all assets from database
    db.generated_assets.delete_many({"job_application_id": str(app_id)})

    # Delete application from database
    db.applications.delete_one({"_id": ObjectId(app_id)})

    return jsonify({"success": True})

```

### controllers/auth_controller.py

```python
import jwt
from datetime import datetime, timedelta
from flask import request, render_template, redirect, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from config import Config
from models.user import user_model


def generate_jwt(user_id, role):
    payload = {
        "user_id": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            return render_template("auth/signup.html", error="All fields are required")

        if db.users.find_one({"email": email.lower()}):
            return render_template("auth/signup.html", error="Email already exists")

        user = user_model(
            email=email, name=name, password_hash=generate_password_hash(password)
        )

        db.users.insert_one(user)
        return redirect("/login")

    return render_template("auth/signup.html")


def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.users.find_one({"email": email.lower()})
        if not user or not check_password_hash(user["password"], password):
            return render_template("auth/login.html", error="Invalid email or password")

        token = generate_jwt(user["_id"], user["role"])

        response = make_response(redirect("/dashboard"))
        response.set_cookie(
            "access_token",
            token,
            httponly=True,
            secure=False,  # set True in production (HTTPS)
            samesite="Lax",
        )
        return response

    return render_template("auth/login.html")


def logout():
    response = make_response(redirect("/login"))
    response.delete_cookie("access_token")
    return response

```

### controllers/base_resume_controller.py

```python
from flask import (
    request,
    render_template,
    redirect,
    make_response,
    g,
    jsonify,
    send_file,
)
from bson.objectid import ObjectId
from db import db
from models.base_resume import base_resume_model
from uuid import uuid4
import os


def create_base_resume():
    """Upload a new base resume template with optional class files"""
    tex_file = request.files.get("latex")
    title = request.form.get("title")
    description = request.form.get("description", "")

    # Get optional class file
    cls_file = request.files.get("class_file")

    if not tex_file or not title:
        return redirect("/profile")

    # Generate unique filename for the .tex file
    tex_filename = f"{uuid4()}.tex"
    tex_path = f"storage/base_resumes/{tex_filename}"

    # Save the .tex file
    tex_file.save(tex_path)
    print(f"✓ Saved .tex file: {tex_path}")

    # If a class file was uploaded, save it too
    cls_filename = None
    if cls_file and cls_file.filename:
        # Keep the original class filename (e.g., lmdEN.cls)
        cls_filename = cls_file.filename
        cls_path = f"storage/base_resumes/{cls_filename}"
        cls_file.save(cls_path)
        print(f"✓ Saved class file: {cls_path}")

    # Deactivate old resumes for this user
    db.base_resumes.update_many(
        {"user_id": g.user["user_id"]}, {"$set": {"is_active": False}}
    )

    # Create new base resume
    resume = base_resume_model(
        user_id=g.user["user_id"],
        title=title,
        description=description,
        latex_template_path=tex_filename,  # Store just the filename
    )
    resume["is_active"] = True

    # Store class file reference if provided
    if cls_filename:
        resume["class_file"] = cls_filename

    db.base_resumes.insert_one(resume)
    print(f"✓ Base resume created: {title}")

    return redirect("/profile")


def delete_base_resume(resume_id):
    """Delete a base resume template and its associated class file"""
    resume = db.base_resumes.find_one(
        {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]}
    )

    if not resume:
        return jsonify({"success": False, "error": "Resume not found"}), 404

    # Prevent deletion of active resume
    if resume.get("is_active"):
        return jsonify({"success": False, "error": "Cannot delete active resume"}), 400

    # Delete the .tex file
    tex_path = f"storage/base_resumes/{resume['latex_template_path']}"
    if os.path.exists(tex_path):
        try:
            os.remove(tex_path)
            print(f"✓ Deleted .tex file: {tex_path}")
        except Exception as e:
            print(f"Error deleting .tex file: {e}")

    # Delete the .cls file if it exists
    if resume.get("class_file"):
        cls_path = f"storage/base_resumes/{resume['class_file']}"
        if os.path.exists(cls_path):
            try:
                # Check if any other resume is using this class file
                other_resumes_using_cls = db.base_resumes.count_documents(
                    {
                        "class_file": resume["class_file"],
                        "_id": {"$ne": ObjectId(resume_id)},
                    }
                )

                if other_resumes_using_cls == 0:
                    # Only delete if no other resume is using it
                    os.remove(cls_path)
                    print(f"✓ Deleted class file: {cls_path}")
                else:
                    print(f"⚠ Kept class file (used by other resumes): {cls_path}")
            except Exception as e:
                print(f"Error deleting class file: {e}")

    # Delete from database
    db.base_resumes.delete_one({"_id": ObjectId(resume_id)})
    return jsonify({"success": True})


def activate_base_resume(resume_id):
    """Set a base resume as active"""
    resume = db.base_resumes.find_one(
        {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]}
    )

    if not resume:
        return jsonify({"success": False, "error": "Resume not found"}), 404

    # Deactivate all other resumes for this user
    db.base_resumes.update_many(
        {"user_id": g.user["user_id"]}, {"$set": {"is_active": False}}
    )

    # Activate this resume
    db.base_resumes.update_one(
        {"_id": ObjectId(resume_id)}, {"$set": {"is_active": True}}
    )

    return jsonify({"success": True})


def download_base_resume(resume_id):
    """Download a base resume LaTeX file"""
    resume = db.base_resumes.find_one(
        {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]}
    )

    if not resume:
        return "Not found", 404

    file_path = f"storage/base_resumes/{resume['latex_template_path']}"

    if not os.path.exists(file_path):
        return "File not found", 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"{resume['title']}.tex",
    )


def download_class_file(resume_id):
    """Download the associated class file if it exists"""
    resume = db.base_resumes.find_one(
        {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]}
    )

    if not resume:
        return "Not found", 404

    if not resume.get("class_file"):
        return "No class file associated with this resume", 404

    file_path = f"storage/base_resumes/{resume['class_file']}"

    if not os.path.exists(file_path):
        return "Class file not found", 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=resume["class_file"],
    )

```

### controllers/dashboard_controller.py

```python


```

### controllers/profile_controller.py

```python
from flask import render_template, g
from bson.objectid import ObjectId
from db import db


def profile():
    user_id = g.user["user_id"]

    user = db.users.find_one(
        {"_id": ObjectId(user_id)}, {"password": 0}  # never send password to view
    )

    # Get all base resumes for this user
    base_resumes = list(
        db.base_resumes.find({"user_id": user_id}).sort("created_at", -1)
    )

    return render_template("profile/index.html", user=user, base_resumes=base_resumes)

```

### controllers/section_preferences_controller.py

```python
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

```

### db.py

```python
from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]

```

### middlewares/auth_middleware.py

```python
import jwt
from functools import wraps
from flask import request, redirect, g
from config import Config


def require_auth(f):
    """Middleware to require authentication for routes"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return redirect("/login")

        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            g.user = payload  # { user_id, role, exp }
        except jwt.ExpiredSignatureError:
            return redirect("/login")
        except jwt.InvalidTokenError:
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated


def guest_only(f):
    """Middleware to allow only guests (non-authenticated users)"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")
        if token:
            try:
                jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
                return redirect("/dashboard")
            except:
                pass
        return f(*args, **kwargs)

    return decorated

```

### models/base_resume.py

```python
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

```

### models/generated_asset.py

```python
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
        "_id": ObjectId(),  # ← Changed from str(ObjectId())
        "job_application_id": job_application_id,
        "user_id": user_id,
        "type": asset_type,
        "title": title,
        "content_text": content_text,
        "pdf_path": pdf_path,
        "tex_path": tex_path,
        "ai_model": ai_model,
        "version": version,
        "created_at": datetime.utcnow(),
    }

```

### models/job_application.py

```python
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

```

### models/user.py

```python
from datetime import datetime


def user_model(email, name, password_hash, role="user"):
    return {
        "email": email.lower(),
        "name": name,
        "password": password_hash,
        "role": role,
        "created_at": datetime.utcnow(),
    }

```

### promptpack.md

```markdown
# PromptPack Output

**Root:** `/Users/swapnil/Documents/Projects/applytailored`
**Generated:** 2026-01-29T14:25:46.544Z

---

## 1) Folder Structure

```txt
.
├─ app.py
├─ config.py
├─ controllers/
│  ├─ ai_controller_backup.py
│  ├─ ai_controller.py
│  ├─ application_controller.py
│  ├─ auth_controller.py
│  ├─ base_resume_controller.py
│  ├─ dashboard_controller.py
│  ├─ profile_controller.py
│  └─ section_preferences_controller.py
├─ db.py
├─ middlewares/
│  └─ auth_middleware.py
├─ models/
│  ├─ base_resume.py
│  ├─ generated_asset.py
│  ├─ job_application.py
│  └─ user.py
├─ public/
├─ QUICK_START.md
├─ README.md
├─ requirements.txt
├─ routes/
│  ├─ application_routes.py
│  ├─ auth_routes.py
│  ├─ dashboard_routes.py
│  ├─ profile_routes.py
│  └─ section_preferences_routes.py
├─ seed_database.py
├─ services/
│  ├─ claude_ai_service_backup.py
│  ├─ claude_ai_service.py
│  ├─ latex_parser_service.py
│  └─ latex_service.py
├─ storage/
│  ├─ base_resumes/
│  │  ├─ a31e559f-8d9c-4389-a562-2e0b7314bf0e.tex
│  │  └─ base_resume_template.tex
│  └─ generated/
│     ├─ resume_697b6c657e75610931541e23_1769696371.pdf
│     └─ resume_697b6c657e75610931541e23_1769696371.tex
└─ views/
   ├─ applications/
   │  ├─ detail.html
   │  ├─ index.html
   │  └─ modal.html
   ├─ auth/
   │  ├─ login.html
   │  └─ signup.html
   ├─ dashboard/
   │  └─ index.html
   ├─ layouts/
   │  ├─ auth.html
   │  ├─ dashboard.html
   │  └─ signup.html
   ├─ partials/
   │  ├─ navbar.html
   │  └─ sidebar.html
   ├─ profile/
   │  └─ index.html
   └─ resume/
      └─ section_preferences.html
```

<!-- PAGE BREAK: FILE CONTENTS BELOW -->

## 2) File Contents


### app.py

```python
from flask import Flask, app
from config import Config
from routes.auth_routes import auth_routes
from routes.dashboard_routes import dashboard_routes
from routes.application_routes import application_routes

from routes.profile_routes import profile_routes

from routes.section_preferences_routes import section_preferences_routes


def create_app():
    app = Flask(__name__, template_folder="views")  # <--- specify template folder
    app.config.from_object(Config)

    @app.route("/")
    def index():
        return "Flask app is running 🚀"

    app.register_blueprint(auth_routes)
    app.register_blueprint(dashboard_routes)
    app.register_blueprint(profile_routes)
    app.register_blueprint(application_routes)

    app.register_blueprint(section_preferences_routes)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

```

### config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    JWT_SECRET = os.getenv("JWT_SECRET", "jwt-secret-key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "applytailored")

```

### controllers/ai_controller_backup.py

```python
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

```

### controllers/ai_controller.py

```python
"""
Enhanced AI Controller with automatic selective regeneration based on saved preferences
"""

import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from bson.objectid import ObjectId
from db import db
from services.claude_ai_service import ClaudeAIService
from services.latex_service import LatexService
from services.latex_parser_service import LatexParserService
from models.generated_asset import generated_asset_model


class AIController:
    def __init__(self):
        self.claude_service = ClaudeAIService()
        self.latex_service = LatexService()
        self.parser_service = LatexParserService()

    def parse_base_resume(self, resume_id: str, user_id: str) -> Dict[str, Any]:
        """
        Parse a base resume into selectable sections
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

            parsed = self.parser_service.parse_resume(latex_content)

            sections_for_ui = []
            for section in parsed["sections"]:
                section_info = {
                    "id": f"{section.section_type}_{section.start_pos}",
                    "type": section.section_type,
                    "title": section.title,
                    "preview": self.parser_service.get_section_preview(section),
                    "has_subsections": len(section.subsections) > 0,
                    "subsections": [],
                }

                for subsection in section.subsections:
                    subsection_info = {
                        "id": f"sub_{subsection.start_pos}",
                        "title": subsection.title,
                        "lines": subsection.lines,
                        "line_count": len(subsection.lines),
                    }
                    section_info["subsections"].append(subsection_info)

                sections_for_ui.append(section_info)

            return {
                "success": True,
                "parsed_structure": parsed,
                "sections": sections_for_ui,
                "header": parsed["header"],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def process_job_application(
        self, application_id: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Main workflow to process a job application.

        NEW BEHAVIOR: Checks if base resume has section preferences enabled.
        If enabled, only regenerates selected sections. Otherwise, regenerates entire resume.
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
            # Update status to processing
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

            # Step 3: Check if selective regeneration is enabled
            section_prefs = base_resume.get("section_preferences", {})
            selective_enabled = section_prefs.get("enabled", False)
            selected_sections = section_prefs.get("selected_sections", [])

            if selective_enabled and selected_sections:
                # USE SELECTIVE REGENERATION
                print(
                    f"Using selective regeneration for {len(selected_sections)} sections"
                )

                # Parse resume
                parsed = self.parser_service.parse_resume(base_latex_content)

                # Regenerate only selected sections
                regenerated = {}
                for section in parsed["sections"]:
                    section_id = f"{section.section_type}_{section.start_pos}"

                    if section_id in selected_sections:
                        print(f"Regenerating section: {section.title}")
                        new_content = self.claude_service.regenerate_section(
                            section_content=section.content,
                            section_type=section.section_type,
                            job_description=application["job_description"],
                            job_analysis=job_analysis,
                            context={
                                "section_title": section.title,
                                "has_subsections": len(section.subsections) > 0,
                            },
                        )
                        regenerated[section_id] = new_content

                # Rebuild LaTeX with regenerated sections
                tailored_latex = self.parser_service.rebuild_latex(
                    original_content=base_latex_content,
                    parsed_structure=parsed,
                    selected_sections={s: True for s in selected_sections},
                    regenerated_sections=regenerated,
                )

                regeneration_type = "selective"

            else:
                # USE FULL REGENERATION (original behavior)
                print("Using full resume regeneration")
                tailored_latex = self.claude_service.tailor_resume(
                    base_latex_content, application["job_description"], job_analysis
                )
                regeneration_type = "full"

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

            # Step 5: Save generated asset to database
            tex_filename = f"{output_filename}.tex"
            tex_path = f"storage/generated/{tex_filename}"

            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tailored_latex)

            content_text = self.latex_service.extract_text_from_latex(tailored_latex)

            # Create title based on regeneration type
            if regeneration_type == "selective":
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

            # Step 6: Update application with results
            update_data = {
                "status": "completed",
                "company_name": job_analysis.get("company_name"),
                "position_title": job_analysis.get("position_title"),
                "base_resume_id": str(base_resume["_id"]),
                "generated_resume_id": generated_asset_id,
                "ai_analysis": job_analysis,
                "updated_at": datetime.utcnow(),
                "regeneration_type": regeneration_type,  # Track which method was used
            }

            if regeneration_type == "selective":
                update_data["regenerated_sections"] = selected_sections

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
                "sections_regenerated": (
                    selected_sections if regeneration_type == "selective" else None
                ),
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

            return {"success": False, "error": str(e)}

    def _get_base_resume(self, user_id: str) -> Optional[Dict]:
        """Get the user's base resume, or a default one"""
        # Try to get user's active base resume
        base_resume = db.base_resumes.find_one({"user_id": user_id, "is_active": True})

        if base_resume:
            return base_resume

        # Try any user resume
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

```

### controllers/application_controller.py

```python
from flask import render_template, request, redirect, g, jsonify
from bson.objectid import ObjectId
from db import db
from models.job_application import job_application_model
from controllers.ai_controller import AIController
import os


ai_controller = AIController()


def list_applications():
    """List all applications for the current user"""
    apps = list(
        db.applications.find({"user_id": g.user["user_id"]}).sort("created_at", -1)
    )
    return render_template("applications/index.html", applications=apps)


def create_application():
    """Create a new job application and process it with AI"""
    job_description = request.form.get("job_description")

    if not job_description:
        return redirect("/applications")

    # Create application
    application = job_application_model(
        user_id=g.user["user_id"],
        job_description=job_description,
    )

    result = db.applications.insert_one(application)
    application_id = str(result.inserted_id)

    # Trigger AI processing in background
    # For now, we'll do it synchronously, but you could use Celery/Redis for async
    try:
        ai_result = ai_controller.process_job_application(
            application_id, g.user["user_id"]
        )

        if not ai_result["success"]:
            print(f"AI processing error: {ai_result.get('error')}")
    except Exception as e:
        print(f"Error during AI processing: {e}")

    return redirect(f"/applications/{application_id}")


def application_detail(app_id):
    """View detailed application with generated assets"""
    # Try to find by string ID first, then ObjectId
    try:
        app = db.applications.find_one({"_id": app_id, "user_id": g.user["user_id"]})

        # If not found, try as ObjectId
        if not app:
            app = db.applications.find_one(
                {"_id": ObjectId(app_id), "user_id": g.user["user_id"]}
            )
    except:
        app = db.applications.find_one({"_id": app_id, "user_id": g.user["user_id"]})

    if not app:
        return redirect("/applications")

    # Get generated assets for this application
    generated_assets = list(
        db.generated_assets.find(
            {"job_application_id": str(app["_id"]), "user_id": g.user["user_id"]}
        ).sort("created_at", -1)
    )

    return render_template(
        "applications/detail.html", application=app, generated_assets=generated_assets
    )


def regenerate_resume(app_id):
    """Regenerate resume for an application"""
    app = db.applications.find_one(
        {"_id": ObjectId(app_id), "user_id": g.user["user_id"]}
    )

    if not app:
        return jsonify({"success": False, "error": "Application not found"}), 404

    try:
        result = ai_controller.process_job_application(app_id, g.user["user_id"])

        if result["success"]:
            return jsonify(
                {
                    "success": True,
                    "message": "Resume regenerated successfully",
                    "pdf_path": result.get("pdf_path"),
                }
            )
        else:
            return (
                jsonify(
                    {"success": False, "error": result.get("error", "Unknown error")}
                ),
                500,
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def generate_cover_letter(app_id):
    """Generate cover letter for an application"""
    app = db.applications.find_one(
        {"_id": ObjectId(app_id), "user_id": g.user["user_id"]}
    )

    if not app:
        return jsonify({"success": False, "error": "Application not found"}), 404

    try:
        result = ai_controller.generate_cover_letter(app_id, g.user["user_id"])

        if result["success"]:
            return jsonify(
                {
                    "success": True,
                    "message": "Cover letter generated successfully",
                    "content": result.get("content"),
                }
            )
        else:
            return (
                jsonify(
                    {"success": False, "error": result.get("error", "Unknown error")}
                ),
                500,
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def download_asset(asset_id):
    """Download generated asset (PDF or TEX)"""
    from flask import send_file

    asset = db.generated_assets.find_one(
        {"_id": ObjectId(asset_id), "user_id": g.user["user_id"]}
    )
    if not asset:
        return "Not found", 404

    file_type = request.args.get("type", "pdf")

    if file_type == "tex":
        file_path = asset.get("tex_path")
        ext = "tex"
    else:
        file_path = asset.get("pdf_path")
        ext = "pdf"

    if not file_path:
        return "File not available", 404

    if not os.path.exists(file_path):
        return "File not found on disk", 404

    return send_file(
        file_path, as_attachment=True, download_name=f"{asset['title']}.{ext}"
    )


def delete_asset(asset_id):
    """Delete a single generated asset"""
    asset = db.generated_assets.find_one(
        {"_id": ObjectId(asset_id), "user_id": g.user["user_id"]}
    )
    if not asset:
        return jsonify({"success": False, "error": "Asset not found"}), 404

    # Delete files from disk
    for file_path in [asset.get("pdf_path"), asset.get("tex_path")]:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

    # Delete from database
    db.generated_assets.delete_one({"_id": ObjectId(asset_id)})
    return jsonify({"success": True})


def delete_application(app_id):
    """Delete an application and all its associated assets"""
    # Find application
    app = db.applications.find_one(
        {"_id": ObjectId(app_id), "user_id": g.user["user_id"]}
    )
    if not app:
        return jsonify({"success": False, "error": "Application not found"}), 404

    # Find all assets for this application
    assets = list(
        db.generated_assets.find(
            {"job_application_id": str(app_id), "user_id": g.user["user_id"]}
        )
    )

    # Delete all asset files
    for asset in assets:
        for file_path in [asset.get("pdf_path"), asset.get("tex_path")]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file {file_path}: {e}")

    # Delete all assets from database
    db.generated_assets.delete_many({"job_application_id": str(app_id)})

    # Delete application from database
    db.applications.delete_one({"_id": ObjectId(app_id)})

    return jsonify({"success": True})

```

### controllers/auth_controller.py

```python
import jwt
from datetime import datetime, timedelta
from flask import request, render_template, redirect, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from config import Config
from models.user import user_model


def generate_jwt(user_id, role):
    payload = {
        "user_id": str(user_id),
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=7),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")


def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            return render_template("auth/signup.html", error="All fields are required")

        if db.users.find_one({"email": email.lower()}):
            return render_template("auth/signup.html", error="Email already exists")

        user = user_model(
            email=email, name=name, password_hash=generate_password_hash(password)
        )

        db.users.insert_one(user)
        return redirect("/login")

    return render_template("auth/signup.html")


def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.users.find_one({"email": email.lower()})
        if not user or not check_password_hash(user["password"], password):
            return render_template("auth/login.html", error="Invalid email or password")

        token = generate_jwt(user["_id"], user["role"])

        response = make_response(redirect("/dashboard"))
        response.set_cookie(
            "access_token",
            token,
            httponly=True,
            secure=False,  # set True in production (HTTPS)
            samesite="Lax",
        )
        return response

    return render_template("auth/login.html")


def logout():
    response = make_response(redirect("/login"))
    response.delete_cookie("access_token")
    return response

```

### controllers/base_resume_controller.py

```python
from flask import (
    request,
    render_template,
    redirect,
    make_response,
    g,
    jsonify,
    send_file,
)
from bson.objectid import ObjectId
from db import db
from models.base_resume import base_resume_model
from uuid import uuid4
import os


def create_base_resume():
    """Upload a new base resume template with optional class files"""
    tex_file = request.files.get("latex")
    title = request.form.get("title")
    description = request.form.get("description", "")

    # Get optional class file
    cls_file = request.files.get("class_file")

    if not tex_file or not title:
        return redirect("/profile")

    # Generate unique filename for the .tex file
    tex_filename = f"{uuid4()}.tex"
    tex_path = f"storage/base_resumes/{tex_filename}"

    # Save the .tex file
    tex_file.save(tex_path)
    print(f"✓ Saved .tex file: {tex_path}")

    # If a class file was uploaded, save it too
    cls_filename = None
    if cls_file and cls_file.filename:
        # Keep the original class filename (e.g., lmdEN.cls)
        cls_filename = cls_file.filename
        cls_path = f"storage/base_resumes/{cls_filename}"
        cls_file.save(cls_path)
        print(f"✓ Saved class file: {cls_path}")

    # Deactivate old resumes for this user
    db.base_resumes.update_many(
        {"user_id": g.user["user_id"]}, {"$set": {"is_active": False}}
    )

    # Create new base resume
    resume = base_resume_model(
        user_id=g.user["user_id"],
        title=title,
        description=description,
        latex_template_path=tex_filename,  # Store just the filename
    )
    resume["is_active"] = True

    # Store class file reference if provided
    if cls_filename:
        resume["class_file"] = cls_filename

    db.base_resumes.insert_one(resume)
    print(f"✓ Base resume created: {title}")

    return redirect("/profile")


def delete_base_resume(resume_id):
    """Delete a base resume template and its associated class file"""
    resume = db.base_resumes.find_one(
        {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]}
    )

    if not resume:
        return jsonify({"success": False, "error": "Resume not found"}), 404

    # Prevent deletion of active resume
    if resume.get("is_active"):
        return jsonify({"success": False, "error": "Cannot delete active resume"}), 400

    # Delete the .tex file
    tex_path = f"storage/base_resumes/{resume['latex_template_path']}"
    if os.path.exists(tex_path):
        try:
            os.remove(tex_path)
            print(f"✓ Deleted .tex file: {tex_path}")
        except Exception as e:
            print(f"Error deleting .tex file: {e}")

    # Delete the .cls file if it exists
    if resume.get("class_file"):
        cls_path = f"storage/base_resumes/{resume['class_file']}"
        if os.path.exists(cls_path):
            try:
                # Check if any other resume is using this class file
                other_resumes_using_cls = db.base_resumes.count_documents(
                    {
                        "class_file": resume["class_file"],
                        "_id": {"$ne": ObjectId(resume_id)},
                    }
                )

                if other_resumes_using_cls == 0:
                    # Only delete if no other resume is using it
                    os.remove(cls_path)
                    print(f"✓ Deleted class file: {cls_path}")
                else:
                    print(f"⚠ Kept class file (used by other resumes): {cls_path}")
            except Exception as e:
                print(f"Error deleting class file: {e}")

    # Delete from database
    db.base_resumes.delete_one({"_id": ObjectId(resume_id)})
    return jsonify({"success": True})


def activate_base_resume(resume_id):
    """Set a base resume as active"""
    resume = db.base_resumes.find_one(
        {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]}
    )

    if not resume:
        return jsonify({"success": False, "error": "Resume not found"}), 404

    # Deactivate all other resumes for this user
    db.base_resumes.update_many(
        {"user_id": g.user["user_id"]}, {"$set": {"is_active": False}}
    )

    # Activate this resume
    db.base_resumes.update_one(
        {"_id": ObjectId(resume_id)}, {"$set": {"is_active": True}}
    )

    return jsonify({"success": True})


def download_base_resume(resume_id):
    """Download a base resume LaTeX file"""
    resume = db.base_resumes.find_one(
        {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]}
    )

    if not resume:
        return "Not found", 404

    file_path = f"storage/base_resumes/{resume['latex_template_path']}"

    if not os.path.exists(file_path):
        return "File not found", 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"{resume['title']}.tex",
    )


def download_class_file(resume_id):
    """Download the associated class file if it exists"""
    resume = db.base_resumes.find_one(
        {"_id": ObjectId(resume_id), "user_id": g.user["user_id"]}
    )

    if not resume:
        return "Not found", 404

    if not resume.get("class_file"):
        return "No class file associated with this resume", 404

    file_path = f"storage/base_resumes/{resume['class_file']}"

    if not os.path.exists(file_path):
        return "Class file not found", 404

    return send_file(
        file_path,
        as_attachment=True,
        download_name=resume["class_file"],
    )

```

### controllers/dashboard_controller.py

```python


```

### controllers/profile_controller.py

```python
from flask import render_template, g
from bson.objectid import ObjectId
from db import db


def profile():
    user_id = g.user["user_id"]

    user = db.users.find_one(
        {"_id": ObjectId(user_id)}, {"password": 0}  # never send password to view
    )

    # Get all base resumes for this user
    base_resumes = list(
        db.base_resumes.find({"user_id": user_id}).sort("created_at", -1)
    )

    return render_template("profile/index.html", user=user, base_resumes=base_resumes)

```

### controllers/section_preferences_controller.py

```python
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

```

### db.py

```python
from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]

```

### middlewares/auth_middleware.py

```python
import jwt
from functools import wraps
from flask import request, redirect, g
from config import Config


def require_auth(f):
    """Middleware to require authentication for routes"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            return redirect("/login")

        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            g.user = payload  # { user_id, role, exp }
        except jwt.ExpiredSignatureError:
            return redirect("/login")
        except jwt.InvalidTokenError:
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated


def guest_only(f):
    """Middleware to allow only guests (non-authenticated users)"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("access_token")
        if token:
            try:
                jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
                return redirect("/dashboard")
            except:
                pass
        return f(*args, **kwargs)

    return decorated

```

### models/base_resume.py

```python
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

```

### models/generated_asset.py

```python
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
        "_id": ObjectId(),  # ← Changed from str(ObjectId())
        "job_application_id": job_application_id,
        "user_id": user_id,
        "type": asset_type,
        "title": title,
        "content_text": content_text,
        "pdf_path": pdf_path,
        "tex_path": tex_path,
        "ai_model": ai_model,
        "version": version,
        "created_at": datetime.utcnow(),
    }

```

### models/job_application.py

```python
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

```

### models/user.py

```python
from datetime import datetime


def user_model(email, name, password_hash, role="user"):
    return {
        "email": email.lower(),
        "name": name,
        "password": password_hash,
        "role": role,
        "created_at": datetime.utcnow(),
    }

```

### QUICK_START.md

```markdown
# Quick Start Guide - Updating Your Existing Project

This guide will help you integrate the AI-powered resume tailoring features into your existing ApplyTailored project.

## Step-by-Step Integration

### 1. Install New Dependencies

Add to your `requirements.txt`:
```bash
anthropic==0.40.0
pydantic==2.5.3
```

Install:
```bash
pip install anthropic pydantic
```

### 2. Set Up Environment Variables

Add to your `.env` file:
```env
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

Get your API key from: https://console.anthropic.com/

### 3. Add New Models

Replace/add these files in your `models/` directory:

- `models/base_resume.py` - NEW
- `models/generated_asset.py` - NEW  
- `models/job_application.py` - UPDATE with the enhanced version

### 4. Create Services Directory

Create a new `services/` directory and add:

- `services/claude_ai_service.py` - Handles all Claude API interactions
- `services/latex_service.py` - Compiles LaTeX to PDF

### 5. Update Controllers

**Replace** your existing files with the updated versions:

- `controllers/ai_controller.py` → Use `controllers/ai_controller_updated.py`
- `controllers/application_controller.py` → Use `controllers/application_controller_updated.py`

### 6. Update Routes

**Replace**:
- `routes/application_routes.py` → Use `routes/application_routes_updated.py`

This adds new endpoints:
- `/applications/<id>/regenerate` - Regenerate resume
- `/applications/<id>/cover-letter` - Generate cover letter
- `/assets/<id>/download` - Download files

### 7. Update Views

**Replace**:
- `views/applications/detail.html` → Use `views/applications/detail_updated.html`

This adds:
- AI analysis display
- Generated documents list
- Action buttons for regeneration
- Cover letter modal

### 8. Set Up Storage Directory

Create the storage structure:
```bash
mkdir -p storage/base_resumes
mkdir -p storage/generated
```

Add the base resume template:
- Copy `storage/base_resumes/base_resume_template.tex` to your project

### 9. Initialize Database

Run the seeding script to set up collections and indexes:
```bash
python seed_database.py
```

This will:
- Create database indexes for performance
- Add a default base resume entry
- Verify storage directories

### 10. Update app.py (if needed)

Make sure your `app.py` imports the updated routes:

```python
from routes.application_routes_updated import application_routes
```

### 11. Install LaTeX (if not already installed)

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install texlive-full
```

**macOS**:
```bash
brew install --cask mactex
```

**Windows**:
Download and install MiKTeX from: https://miktex.org/

Verify installation:
```bash
pdflatex --version
```

## File Replacement Summary

### Files to ADD (new):
```
models/base_resume.py
models/generated_asset.py
services/claude_ai_service.py
services/latex_service.py
seed_database.py
storage/base_resumes/base_resume_template.tex
```

### Files to REPLACE (updated versions):
```
controllers/ai_controller.py
controllers/application_controller.py
routes/application_routes.py
views/applications/detail.html
requirements.txt
```

### Files to KEEP (no changes needed):
```
app.py (minor import update only)
config.py
db.py
models/user.py
controllers/auth_controller.py
controllers/dashboard_controller.py
controllers/profile_controller.py
middlewares/auth_middleware.py
routes/auth_routes.py
routes/dashboard_routes.py
routes/profile_routes.py
All other views/
```

## Testing the Integration

### 1. Start MongoDB
```bash
# Linux
sudo systemctl start mongod

# macOS
brew services start mongodb-community
```

### 2. Run Database Seeding
```bash
python seed_database.py
```

Expected output:
```
✓ Verified directory: storage
✓ Verified directory: storage/base_resumes
✓ Verified directory: storage/generated
✓ Created index on users.email
✓ Created indexes on applications collection
✓ Created index on base_resumes.user_id
✓ Created indexes on generated_assets collection
✓ Created default base resume
✅ Database seeding completed successfully!
```

### 3. Start the Application
```bash
python app.py
```

### 4. Test the Flow

1. **Login/Signup**: Create an account or login
2. **Create Application**: 
   - Go to Applications
   - Click "New Application"
   - Paste a job description
   - Submit

3. **Watch AI Process**:
   - You'll be redirected to application detail
   - Status should show "processing" → "completed"
   - Generated resume will appear

4. **Test Actions**:
   - Click "Download PDF" to get tailored resume
   - Click "Generate Cover Letter" to create one
   - Click "Regenerate Resume" to create new version

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'anthropic'"
**Solution**: 
```bash
pip install anthropic
```

### Issue: "pdflatex: command not found"
**Solution**: Install LaTeX distribution (see step 11 above)

### Issue: "Application status stuck on 'processing'"
**Solution**:
1. Check logs for errors
2. Verify ANTHROPIC_API_KEY is set correctly
3. Check if LaTeX is installed properly
4. Look at MongoDB for error details in the application document

### Issue: "LaTeX compilation failed"
**Solution**:
1. Check `storage/generated/*.log` files for LaTeX errors
2. System will fallback to base resume automatically
3. Verify base resume template is valid LaTeX

### Issue: MongoDB connection error
**Solution**:
1. Ensure MongoDB is running
2. Check MONGO_URI in `.env` file
3. Verify database permissions

## Architecture Overview

```
User submits job description
         ↓
Application created in DB (status: draft)
         ↓
AI Controller processes application
         ↓
    ┌────────────────────┐
    │ Claude AI Service  │
    │ - Analyze job desc │
    │ - Tailor resume    │
    └────────────────────┘
         ↓
    ┌────────────────────┐
    │  LaTeX Service     │
    │ - Compile to PDF   │
    │ - Fallback if fail │
    └────────────────────┘
         ↓
Generated Asset saved to DB
         ↓
Application status: completed
         ↓
User downloads PDF
```

## Environment Variables Checklist

Make sure your `.env` file has:

```env
✓ SECRET_KEY=...
✓ JWT_SECRET=...
✓ MONGO_URI=...
✓ DB_NAME=...
✓ ANTHROPIC_API_KEY=...  ← NEW!
```

## Next Steps After Integration

1. **Customize Base Resume**: 
   - Edit `storage/base_resumes/base_resume_template.tex`
   - Add your personal information
   - Adjust formatting to your preference

2. **Test with Real Job Postings**:
   - Copy real job descriptions
   - See how Claude tailors your resume
   - Adjust prompts if needed

3. **Monitor AI Usage**:
   - Check Anthropic console for API usage
   - Each application processes = ~2-3 API calls
   - Set up billing alerts if needed

4. **Production Considerations**:
   - Move AI processing to background jobs (Celery)
   - Add rate limiting
   - Implement caching for job analysis
   - Set up error monitoring

## Support

If you encounter issues:

1. Check the main README.md for detailed documentation
2. Review error logs in the console
3. Check MongoDB for application status and errors
4. Verify all environment variables are set

## Success Checklist

Before considering integration complete:

- [ ] All new files added
- [ ] All files updated/replaced
- [ ] Dependencies installed
- [ ] LaTeX installed and working
- [ ] MongoDB seeding completed
- [ ] Environment variables set
- [ ] Application starts without errors
- [ ] Can create account and login
- [ ] Can create new application
- [ ] Application processes with AI successfully
- [ ] Can download generated PDF
- [ ] Can generate cover letter

Congratulations! Your ApplyTailored system now has AI-powered resume tailoring! 🎉

```

### README.md

```markdown
# ApplyTailored - AI-Powered Resume Tailoring System

An intelligent job application management system that uses Claude AI to automatically tailor resumes to job descriptions.

## Features

- 🤖 **AI-Powered Resume Tailoring**: Uses Claude Sonnet 4 to analyze job descriptions and customize your resume
- 📄 **LaTeX Resume Generation**: Compiles professional PDFs from LaTeX templates
- 💼 **Job Application Tracking**: Manage all your job applications in one place
- 📊 **Job Analysis**: Automatically extracts key information from job descriptions
- ✉️ **Cover Letter Generation**: AI-generated cover letters tailored to each position
- 👤 **User Authentication**: Secure JWT-based authentication system
- 📁 **Document Management**: Store and download generated resumes and cover letters

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **AI**: Anthropic Claude API
- **Document Processing**: LaTeX (pdflatex)
- **Authentication**: JWT
- **Frontend**: HTML, Tailwind CSS, Jinja2

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.8+**
2. **MongoDB** (running locally or remote)
3. **LaTeX Distribution**:
   - **Linux**: `sudo apt-get install texlive-full`
   - **macOS**: `brew install --cask mactex`
   - **Windows**: Install MiKTeX from https://miktex.org/
4. **Anthropic API Key**: Sign up at https://console.anthropic.com/

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd applytailored
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET=your-jwt-secret-key-change-this
MONGO_URI=mongodb://localhost:27017
DB_NAME=applytailored
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

### 5. Initialize Database

Run the seeding script to set up initial data and indexes:

```bash
python seed_database.py
```

This will:
- Create necessary MongoDB indexes
- Set up the default base resume template
- Verify storage directories exist

### 6. Verify LaTeX Installation

Test if pdflatex is installed:

```bash
pdflatex --version
```

If you see version information, you're good to go!

## Project Structure

```
applytailored/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── db.py                          # Database connection
├── seed_database.py               # Database initialization script
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
│
├── controllers/
│   ├── ai_controller_updated.py           # AI processing logic
│   ├── application_controller_updated.py  # Application CRUD operations
│   ├── auth_controller.py                 # Authentication logic
│   ├── dashboard_controller.py            # Dashboard logic
│   └── profile_controller.py              # Profile management
│
├── models/
│   ├── user.py                    # User model
│   ├── job_application_updated.py # Enhanced job application model
│   ├── base_resume.py             # Base resume template model
│   └── generated_asset.py         # Generated documents model
│
├── services/
│   ├── claude_ai_service.py       # Claude API integration
│   └── latex_service.py           # LaTeX compilation service
│
├── routes/
│   ├── auth_routes.py             # Authentication routes
│   ├── dashboard_routes.py        # Dashboard routes
│   ├── profile_routes.py          # Profile routes
│   └── application_routes_updated.py  # Application routes with AI features
│
├── middlewares/
│   └── auth_middleware.py         # JWT authentication middleware
│
├── views/                         # HTML templates (Jinja2)
│   ├── layouts/
│   ├── partials/
│   ├── auth/
│   ├── dashboard/
│   ├── profile/
│   └── applications/
│       ├── index.html
│       ├── modal.html
│       └── detail_updated.html    # Enhanced detail view
│
└── storage/
    ├── base_resumes/
    │   └── base_resume_template.tex  # Default resume template
    └── generated/                    # Generated PDFs and LaTeX files
```

## Usage

### 1. Start the Application

```bash
python app.py
```

The application will run on `http://localhost:5000`

### 2. Create an Account

1. Navigate to `http://localhost:5000/signup`
2. Create your account
3. Login with your credentials

### 3. Create a Job Application

1. Go to **Applications** in the sidebar
2. Click **New Application**
3. Paste the job description
4. Click **Create**

The system will automatically:
- Analyze the job description
- Extract key information (company, position, skills)
- Tailor your base resume to match the job
- Compile a professional PDF
- Store everything in your application

### 4. View Generated Documents

1. Click on any application to view details
2. See AI analysis of the job
3. Download generated PDF resume
4. Generate cover letters on demand

### 5. Customize Base Resume

To use your own resume:

1. Create a LaTeX version of your resume
2. Save it in `storage/base_resumes/`
3. Add an entry to the `base_resumes` collection in MongoDB:

```python
db.base_resumes.insert_one({
    "_id": "your-unique-id",
    "user_id": "your-user-id",
    "title": "My Professional Resume",
    "description": "My main resume template",
    "latex_template_path": "my_resume.tex",
    "created_at": datetime.now(timezone.utc),
    "updated_at": datetime.now(timezone.utc)
})
```

## API Endpoints

### Authentication
- `GET /signup` - Signup page
- `POST /signup` - Create account
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - Logout user

### Applications
- `GET /applications` - List all applications
- `POST /applications` - Create new application (triggers AI processing)
- `GET /applications/<id>` - View application details
- `POST /applications/<id>/regenerate` - Regenerate resume
- `POST /applications/<id>/cover-letter` - Generate cover letter

### Assets
- `GET /assets/<id>/download` - Download generated PDF/TEX

## Database Collections

### users
```javascript
{
  _id: ObjectId,
  email: String (unique),
  name: String,
  password: String (hashed),
  role: String (default: "user"),
  created_at: DateTime
}
```

### applications
```javascript
{
  _id: ObjectId,
  user_id: String,
  job_description: String,
  company_name: String (optional),
  position_title: String (optional),
  status: String (draft/processing/completed/failed),
  base_resume_id: String (optional),
  generated_resume_id: String (optional),
  ai_analysis: Object (optional),
  created_at: DateTime,
  updated_at: DateTime
}
```

### base_resumes
```javascript
{
  _id: String,
  user_id: String,
  title: String,
  description: String,
  latex_template_path: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

### generated_assets
```javascript
{
  _id: String,
  job_application_id: String,
  user_id: String,
  type: String (resume/cover_letter/cold_email/followup/question_answer),
  title: String,
  content_text: String,
  pdf_path: String (optional),
  tex_path: String (optional),
  ai_model: String,
  version: Integer,
  created_at: DateTime
}
```

## AI Features

### Resume Tailoring Process

1. **Job Analysis**: Claude analyzes the job description to extract:
   - Company name
   - Position title
   - Required skills
   - Preferred skills
   - Experience level
   - Key responsibilities
   - ATS keywords

2. **Resume Optimization**: Claude modifies the LaTeX resume to:
   - Emphasize relevant experience
   - Highlight matching skills
   - Reorder bullet points for relevance
   - Include ATS-optimized keywords
   - Quantify achievements where possible

3. **LaTeX Compilation**: The system compiles the tailored LaTeX to PDF

4. **Fallback Mechanism**: If compilation fails, the system uses the base resume

### Cover Letter Generation

Claude generates personalized cover letters that:
- Reference specific job requirements
- Highlight relevant achievements
- Show cultural fit
- Include clear call-to-action

## Troubleshooting

### LaTeX Compilation Errors

If you encounter LaTeX errors:

1. **Check LaTeX installation**:
   ```bash
   pdflatex --version
   ```

2. **Install missing packages**:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install texlive-latex-extra texlive-fonts-extra
   ```

3. **Check logs**: Look at `storage/generated/*.log` files

### MongoDB Connection Issues

1. **Verify MongoDB is running**:
   ```bash
   # Check if MongoDB is running
   sudo systemctl status mongod  # Linux
   brew services list            # macOS
   ```

2. **Check connection string** in `.env` file

### API Key Issues

1. Verify your Anthropic API key is valid
2. Check you have sufficient credits
3. Ensure the key has correct permissions

## Production Deployment

For production deployment:

1. **Set environment to production**:
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

2. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

3. **Set up async processing** with Celery for AI jobs:
   ```bash
   pip install celery redis
   ```

4. **Use environment secrets** for API keys and database credentials

5. **Set up HTTPS** for secure communication

## Future Enhancements

- [ ] Async job processing with Celery
- [ ] Multiple resume templates
- [ ] Email integration for application tracking
- [ ] Interview preparation assistant
- [ ] Application analytics dashboard
- [ ] Chrome extension for one-click applications
- [ ] LinkedIn integration
- [ ] Cover letter templates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Credits

Built with:
- [Flask](https://flask.palletsprojects.com/)
- [Anthropic Claude](https://www.anthropic.com/)
- [MongoDB](https://www.mongodb.com/)
- [LaTeX](https://www.latex-project.org/)

```

### requirements.txt

```text
# Core Framework
Flask==3.0.0
Werkzeug==3.0.1

# Database
pymongo==4.6.1

# Authentication
PyJWT==2.8.0

# AI Services
anthropic==0.40.0

# Environment Variables
python-dotenv==1.0.0

# LaTeX Processing (Note: pdflatex must be installed on system)
# Use: sudo apt-get install texlive-full (Linux)
# Or: brew install --cask mactex (macOS)

# Optional: For async processing (recommended for production)
# celery==5.3.4
# redis==5.0.1

# Development
# flask-cors==4.0.0  # If you need CORS

```

### routes/application_routes.py

```python
from flask import Blueprint
from middlewares.auth_middleware import require_auth
from controllers import application_controller

application_routes = Blueprint("application_routes", __name__)


@application_routes.route("/applications", methods=["GET"])
@require_auth
def list_applications():
    return application_controller.list_applications()


@application_routes.route("/applications", methods=["POST"])
@require_auth
def create_application():
    return application_controller.create_application()


@application_routes.route("/applications/<app_id>", methods=["GET"])
@require_auth
def application_detail(app_id):
    return application_controller.application_detail(app_id)


@application_routes.route("/applications/<app_id>/regenerate", methods=["POST"])
@require_auth
def regenerate_resume(app_id):
    return application_controller.regenerate_resume(app_id)


@application_routes.route("/applications/<app_id>/cover-letter", methods=["POST"])
@require_auth
def generate_cover_letter(app_id):
    return application_controller.generate_cover_letter(app_id)


@application_routes.route("/assets/<asset_id>/download", methods=["GET"])
@require_auth
def download_asset(asset_id):
    return application_controller.download_asset(asset_id)


@application_routes.route("/assets/<asset_id>", methods=["DELETE"])
@require_auth
def delete_asset(asset_id):
    return application_controller.delete_asset(asset_id)


@application_routes.route("/applications/<app_id>", methods=["DELETE"])
@require_auth
def delete_application(app_id):
    return application_controller.delete_application(app_id)

```

### routes/auth_routes.py

```python
from flask import Blueprint
from controllers.auth_controller import signup, login, logout
from middlewares.auth_middleware import guest_only

auth_routes = Blueprint("auth", __name__)

auth_routes.route("/login", methods=["GET", "POST"])(guest_only(login))
auth_routes.route("/signup", methods=["GET", "POST"])(guest_only(signup))
auth_routes.route("/logout")(logout)

```

### routes/dashboard_routes.py

```python
from flask import Blueprint, render_template
from middlewares.auth_middleware import require_auth

dashboard_routes = Blueprint("dashboard", __name__)


@dashboard_routes.route("/dashboard")
@require_auth
def dashboard():
    return render_template("dashboard/index.html")

```

### routes/profile_routes.py

```python
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

```

### routes/section_preferences_routes.py

```python
"""
Routes for managing resume section preferences
"""

from flask import Blueprint
from middlewares.auth_middleware import require_auth
from controllers.section_preferences_controller import (
    view_section_preferences,
    load_resume_sections,
    save_section_preferences,
    get_section_preferences,
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

```

### seed_database.py

```python
"""
Database seeding script to initialize base resumes and collections
Run this once to set up the initial data
"""

from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "applytailored")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def seed_base_resume():
    """Create a default base resume entry"""

    # Check if default base resume already exists
    existing = db.base_resumes.find_one({"user_id": "default"})

    if existing:
        print("Default base resume already exists")
        return

    base_resume = {
        "_id": str(ObjectId()),
        "user_id": "default",
        "title": "Default Base Resume",
        "description": "A professional resume template that can be used as a starting point",
        "latex_template_path": "base_resume_template.tex",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    db.base_resumes.insert_one(base_resume)
    print(f"✓ Created default base resume with ID: {base_resume['_id']}")


def create_indexes():
    """Create database indexes for better query performance"""

    # Users collection indexes
    db.users.create_index("email", unique=True)
    print("✓ Created index on users.email")

    # Applications collection indexes
    db.applications.create_index([("user_id", 1), ("created_at", -1)])
    db.applications.create_index("status")
    print("✓ Created indexes on applications collection")

    # Base resumes collection indexes
    db.base_resumes.create_index([("user_id", 1)])
    print("✓ Created index on base_resumes.user_id")

    # Generated assets collection indexes
    db.generated_assets.create_index([("job_application_id", 1)])
    db.generated_assets.create_index([("user_id", 1), ("created_at", -1)])
    db.generated_assets.create_index("type")
    print("✓ Created indexes on generated_assets collection")


def verify_storage_directories():
    """Ensure all necessary storage directories exist"""

    directories = ["storage", "storage/base_resumes", "storage/generated"]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Verified directory: {directory}")


def main():
    print("Starting database seeding...\n")

    try:
        # Verify storage directories
        print("1. Checking storage directories...")
        verify_storage_directories()
        print()

        # Create indexes
        print("2. Creating database indexes...")
        create_indexes()
        print()

        # Seed base resume
        print("3. Seeding default base resume...")
        seed_base_resume()
        print()

        print("✅ Database seeding completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    main()

```

### services/claude_ai_service_backup.py

```python
import os
import anthropic
from typing import Optional, Dict, Any
import json


class ClaudeAIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"

    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job description to extract key information
        """
        prompt = f"""Analyze the following job description and extract structured information.
Return your response in JSON format with these fields:
- company_name: string
- position_title: string
- required_skills: list of strings
- preferred_skills: list of strings
- experience_level: string (entry/mid/senior)
- key_responsibilities: list of strings
- keywords: list of important keywords for ATS

Job Description:
{job_description}

Return only valid JSON, no markdown or additional text."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text

        # Try to parse JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = (
                    response_text.split("```json")[1].split("```")[0].strip()
                )
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "company_name": "Unknown",
                "position_title": "Unknown",
                "required_skills": [],
                "preferred_skills": [],
                "experience_level": "unknown",
                "key_responsibilities": [],
                "keywords": [],
            }

    def tailor_resume(
        self,
        base_resume_latex: str,
        job_description: str,
        job_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Tailor a LaTeX resume to match a job description
        """
        analysis_context = ""
        if job_analysis:
            analysis_context = f"""
Job Analysis:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
- Required Skills: {', '.join(job_analysis.get('required_skills', []))}
- Key Responsibilities: {', '.join(job_analysis.get('key_responsibilities', []))}
- Keywords for ATS: {', '.join(job_analysis.get('keywords', []))}
"""

        prompt = f"""You are an expert resume writer. Your task is to tailor the following LaTeX resume to match the job description below.

IMPORTANT GUIDELINES:
1. Preserve ALL LaTeX formatting, commands, and structure
2. Keep the same document class and packages
3. Maintain professional tone and formatting
4. Optimize for ATS (Applicant Tracking Systems) by including relevant keywords naturally
5. Emphasize experiences and skills that match the job requirements
6. Reorder or rephrase bullet points to highlight relevant achievements
7. Quantify achievements where possible
8. Ensure all LaTeX syntax is valid and compilable
9. Do NOT add fictional experience or skills - only optimize what exists
10. Return ONLY the modified LaTeX code, no explanations or markdown

{analysis_context}

Job Description:
{job_description}

Base Resume (LaTeX):
{base_resume_latex}

Return the tailored LaTeX resume:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        tailored_latex = message.content[0].text

        # Clean up response - remove markdown code blocks if present
        if "```latex" in tailored_latex:
            tailored_latex = tailored_latex.split("```latex")[1].split("```")[0].strip()
        elif "```tex" in tailored_latex:
            tailored_latex = tailored_latex.split("```tex")[1].split("```")[0].strip()
        elif "```" in tailored_latex:
            # Generic code block
            tailored_latex = tailored_latex.split("```")[1].split("```")[0].strip()

        return tailored_latex

    def generate_cover_letter(
        self,
        resume_text: str,
        job_description: str,
        job_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a tailored cover letter
        """
        analysis_context = ""
        if job_analysis:
            analysis_context = f"""
Job Details:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
"""

        prompt = f"""Write a professional cover letter for the following job application.

{analysis_context}

Job Description:
{job_description}

Candidate's Resume/Background:
{resume_text}

Guidelines:
1. Keep it concise (3-4 paragraphs)
2. Show enthusiasm and cultural fit
3. Highlight 2-3 key achievements relevant to the role
4. Demonstrate understanding of the company/role
5. Include a clear call to action
6. Use professional but warm tone
7. Avoid generic phrases

Return only the cover letter text:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text

```

### services/claude_ai_service.py

```python
"""
Enhanced Claude AI Service with selective section regeneration
"""

import os
import anthropic
from typing import Optional, Dict, Any
import json


class ClaudeAIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"

    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job description to extract key information
        """
        prompt = f"""Analyze the following job description and extract structured information.
Return your response in JSON format with these fields:
- company_name: string
- position_title: string
- required_skills: list of strings
- preferred_skills: list of strings
- experience_level: string (entry/mid/senior)
- key_responsibilities: list of strings
- keywords: list of important keywords for ATS

Job Description:
{job_description}

Return only valid JSON, no markdown or additional text."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text

        # Try to parse JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = (
                    response_text.split("```json")[1].split("```")[0].strip()
                )
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "company_name": "Unknown",
                "position_title": "Unknown",
                "required_skills": [],
                "preferred_skills": [],
                "experience_level": "unknown",
                "key_responsibilities": [],
                "keywords": [],
            }

    def regenerate_section(
        self,
        section_content: str,
        section_type: str,
        job_description: str,
        job_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Regenerate a specific section of the resume based on job description

        Args:
            section_content: The original LaTeX content of the section
            section_type: Type of section (experience, education, skills, etc.)
            job_description: Target job description
            job_analysis: Analyzed job information
            context: Additional context about the section

        Returns:
            Regenerated LaTeX content for the section
        """
        context = context or {}

        # Build context information
        analysis_text = f"""
Job Analysis:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
- Required Skills: {', '.join(job_analysis.get('required_skills', [])[:10])}
- Key Responsibilities: {', '.join(job_analysis.get('key_responsibilities', [])[:5])}
- ATS Keywords: {', '.join(job_analysis.get('keywords', [])[:15])}
"""

        # Section-specific instructions
        section_instructions = {
            "experience": """
For the EXPERIENCE section:
- Reorder bullet points to highlight most relevant achievements first
- Emphasize projects and responsibilities that match the job requirements
- Add quantifiable metrics where they exist
- Include ATS keywords naturally in descriptions
- Focus on transferable skills and relevant technologies
- Keep the same job titles and companies (don't fabricate)
""",
            "skills": """
For the SKILLS section:
- Prioritize skills mentioned in the job description
- Group related skills together
- Ensure all required skills are visible if they exist
- Include ATS keywords for technologies mentioned
- Keep the structure clear and scannable
""",
            "education": """
For the EDUCATION section:
- Highlight relevant coursework if it matches job requirements
- Emphasize GPA if strong and relevant
- Include relevant academic projects
- Keep the basic facts unchanged
""",
            "projects": """
For the PROJECTS section:
- Prioritize projects using technologies mentioned in job description
- Emphasize outcomes and impact
- Include relevant technical details
- Highlight teamwork or leadership if relevant
""",
            "summary": """
For the SUMMARY/PROFILE section:
- Tailor the summary to highlight experience relevant to this role
- Include keywords from the job description
- Emphasize the most relevant qualifications
- Keep it concise (2-4 lines)
""",
        }

        instructions = section_instructions.get(
            section_type,
            """
Optimize this section to be more relevant to the job description.
Emphasize relevant content and include appropriate ATS keywords.
""",
        )

        prompt = f"""You are an expert resume writer. Your task is to regenerate ONLY the {section_type.upper()} section of a resume to better match the job description below.

{analysis_text}

Job Description:
{job_description}

CRITICAL GUIDELINES:
1. Preserve ALL LaTeX formatting, commands, and structure EXACTLY
2. Keep the same LaTeX commands (\section, \resumeSubheading, \resumeItem, etc.)
3. Do NOT change dates, company names, job titles, or factual information
4. ONLY modify bullet points and descriptions to emphasize relevant experience
5. Include ATS keywords naturally where appropriate
6. Maintain professional tone and formatting
7. Ensure all LaTeX syntax is valid and compilable
8. Return ONLY the LaTeX code for this section, starting with \section{{{context.get('section_title', section_type)}}}

{instructions}

Original {section_type.upper()} Section (LaTeX):
{section_content}

Return the optimized {section_type.upper()} section in valid LaTeX:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        regenerated_content = message.content[0].text

        # Clean up response - remove markdown code blocks if present
        if "```latex" in regenerated_content:
            regenerated_content = (
                regenerated_content.split("```latex")[1].split("```")[0].strip()
            )
        elif "```tex" in regenerated_content:
            regenerated_content = (
                regenerated_content.split("```tex")[1].split("```")[0].strip()
            )
        elif "```" in regenerated_content:
            regenerated_content = (
                regenerated_content.split("```")[1].split("```")[0].strip()
            )

        return regenerated_content

    def tailor_resume(
        self,
        base_resume_latex: str,
        job_description: str,
        job_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Tailor a LaTeX resume to match a job description
        """
        analysis_context = ""
        if job_analysis:
            analysis_context = f"""
Job Analysis:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
- Required Skills: {', '.join(job_analysis.get('required_skills', []))}
- Key Responsibilities: {', '.join(job_analysis.get('key_responsibilities', []))}
- Keywords for ATS: {', '.join(job_analysis.get('keywords', []))}
"""

        prompt = f"""You are an expert resume writer. Your task is to tailor the following LaTeX resume to match the job description below.

IMPORTANT GUIDELINES:
1. Preserve ALL LaTeX formatting, commands, and structure
2. Keep the same document class and packages
3. Maintain professional tone and formatting
4. Optimize for ATS (Applicant Tracking Systems) by including relevant keywords naturally
5. Emphasize experiences and skills that match the job requirements
6. Reorder or rephrase bullet points to highlight relevant achievements
7. Quantify achievements where possible
8. Ensure all LaTeX syntax is valid and compilable
9. Do NOT add fictional experience or skills - only optimize what exists
10. Return ONLY the modified LaTeX code, no explanations or markdown

{analysis_context}

Job Description:
{job_description}

Base Resume (LaTeX):
{base_resume_latex}

Return the tailored LaTeX resume:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        tailored_latex = message.content[0].text

        # Clean up response - remove markdown code blocks if present
        if "```latex" in tailored_latex:
            tailored_latex = tailored_latex.split("```latex")[1].split("```")[0].strip()
        elif "```tex" in tailored_latex:
            tailored_latex = tailored_latex.split("```tex")[1].split("```")[0].strip()
        elif "```" in tailored_latex:
            # Generic code block
            tailored_latex = tailored_latex.split("```")[1].split("```")[0].strip()

        return tailored_latex

    def generate_cover_letter(
        self,
        resume_text: str,
        job_description: str,
        job_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a tailored cover letter
        """
        analysis_context = ""
        if job_analysis:
            analysis_context = f"""
Job Details:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
"""

        prompt = f"""Write a professional cover letter for the following job application.

{analysis_context}

Job Description:
{job_description}

Candidate's Resume/Background:
{resume_text}

Guidelines:
1. Keep it concise (3-4 paragraphs)
2. Show enthusiasm and cultural fit
3. Highlight 2-3 key achievements relevant to the role
4. Demonstrate understanding of the company/role
5. Include a clear call to action
6. Use professional but warm tone
7. Avoid generic phrases

Return only the cover letter text:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text

```

### services/latex_parser_service.py

```python
"""
LaTeX Parser Service - Extract structured content from LaTeX resume templates
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ResumeSection:
    """Represents a section in the resume"""

    section_type: (
        str  # 'heading', 'experience', 'education', 'skills', 'projects', etc.
    )
    title: str  # Section title
    content: str  # Raw LaTeX content
    start_pos: int  # Position in original document
    end_pos: int  # End position
    subsections: List["ResumeSubsection"] = None

    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []


@dataclass
class ResumeSubsection:
    """Represents a subsection (like individual job, education entry, etc.)"""

    title: str  # e.g., "Senior Software Engineer at Tech Company"
    content: str  # Raw LaTeX content
    lines: List[str]  # Individual bullet points/lines
    start_pos: int
    end_pos: int


class LatexParserService:
    """Parse LaTeX resumes to extract structured content"""

    # Common section headers to look for
    SECTION_PATTERNS = {
        "experience": r"\\section\{.*?(?:experience|employment|work history).*?\}",
        "education": r"\\section\{.*?education.*?\}",
        "skills": r"\\section\{.*?(?:skills|technical skills|competencies).*?\}",
        "projects": r"\\section\{.*?projects.*?\}",
        "summary": r"\\section\{.*?(?:summary|profile|objective).*?\}",
        "certifications": r"\\section\{.*?(?:certifications?|licenses?).*?\}",
        "publications": r"\\section\{.*?publications?.*?\}",
    }

    def parse_resume(self, latex_content: str) -> Dict[str, Any]:
        """
        Parse LaTeX resume into structured sections

        Returns:
            {
                'header': {...},
                'sections': [ResumeSection, ...],
                'raw_content': str
            }
        """
        result = {
            "header": self._extract_header(latex_content),
            "sections": [],
            "raw_content": latex_content,
        }

        # Find all sections
        sections = self._find_sections(latex_content)

        for section_info in sections:
            section = self._parse_section(
                latex_content,
                section_info["type"],
                section_info["title"],
                section_info["start"],
                section_info["end"],
            )
            result["sections"].append(section)

        return result

    def _extract_header(self, latex_content: str) -> Dict[str, str]:
        """Extract resume header information (name, contact, etc.)"""
        header = {"content": "", "name": "", "email": "", "phone": "", "location": ""}

        # Find content before first \section
        section_match = re.search(r"\\section\{", latex_content, re.IGNORECASE)
        if section_match:
            header_content = latex_content[: section_match.start()]
        else:
            # If no sections, take content after \begin{document}
            begin_doc = re.search(r"\\begin\{document\}", latex_content)
            if begin_doc:
                header_content = latex_content[begin_doc.end() :]
            else:
                header_content = latex_content[:500]  # First 500 chars as fallback

        header["content"] = header_content.strip()

        # Try to extract name (usually in \textbf{\Large ...} or similar)
        name_patterns = [
            r"\\textbf\{\\(?:Large|LARGE|huge|Huge)\s+([^}]+)\}",
            r"\\(?:Large|LARGE|huge|Huge)\s+\\textbf\{([^}]+)\}",
            r"\\(?:Large|LARGE)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, header_content)
            if match:
                header["name"] = match.group(1).strip()
                break

        # Extract email
        email_match = re.search(
            r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", header_content
        )
        if email_match:
            header["email"] = email_match.group(1)

        # Extract phone
        phone_match = re.search(
            r"(\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})", header_content
        )
        if phone_match:
            header["phone"] = phone_match.group(1)

        return header

    def _find_sections(self, latex_content: str) -> List[Dict[str, Any]]:
        """Find all section boundaries in the document"""
        sections = []

        # Find all \section{...} commands
        section_matches = list(
            re.finditer(r"\\section\{([^}]+)\}", latex_content, re.IGNORECASE)
        )

        for i, match in enumerate(section_matches):
            section_title = match.group(1)
            start_pos = match.start()

            # End is either the next section or end of document
            if i + 1 < len(section_matches):
                end_pos = section_matches[i + 1].start()
            else:
                # Find \end{document} or use end of content
                end_doc = re.search(r"\\end\{document\}", latex_content[start_pos:])
                if end_doc:
                    end_pos = start_pos + end_doc.start()
                else:
                    end_pos = len(latex_content)

            # Determine section type
            section_type = self._classify_section(section_title)

            sections.append(
                {
                    "type": section_type,
                    "title": section_title,
                    "start": start_pos,
                    "end": end_pos,
                }
            )

        return sections

    def _classify_section(self, section_title: str) -> str:
        """Classify section based on its title"""
        title_lower = section_title.lower()

        for section_type, pattern in self.SECTION_PATTERNS.items():
            if re.search(pattern, f"\\section{{{section_title}}}", re.IGNORECASE):
                return section_type

        # Default classification based on keywords
        if any(word in title_lower for word in ["experience", "work", "employment"]):
            return "experience"
        elif any(word in title_lower for word in ["education", "academic"]):
            return "education"
        elif any(word in title_lower for word in ["skill", "technical", "competenc"]):
            return "skills"
        elif "project" in title_lower:
            return "projects"
        elif any(word in title_lower for word in ["summary", "profile", "objective"]):
            return "summary"
        else:
            return "other"

    def _parse_section(
        self,
        full_content: str,
        section_type: str,
        section_title: str,
        start_pos: int,
        end_pos: int,
    ) -> ResumeSection:
        """Parse a section into structured content"""
        section_content = full_content[start_pos:end_pos]

        section = ResumeSection(
            section_type=section_type,
            title=section_title,
            content=section_content,
            start_pos=start_pos,
            end_pos=end_pos,
        )

        # Parse subsections (like individual jobs, education entries)
        if section_type in ["experience", "education", "projects"]:
            section.subsections = self._parse_subsections(section_content, start_pos)
        elif section_type == "skills":
            section.subsections = self._parse_skills(section_content, start_pos)

        return section

    def _parse_subsections(
        self, section_content: str, base_offset: int
    ) -> List[ResumeSubsection]:
        """Parse subsections like individual job entries"""
        subsections = []

        # Look for \resumeSubheading or similar commands
        patterns = [
            r"\\resumeSubheading\{([^}]+)\}\{([^}]+)\}\{([^}]+)\}\{([^}]+)\}",
            r"\\resumeSubSubheading\{([^}]+)\}\{([^}]+)\}",
            r"\\item\s+\\textbf\{([^}]+)\}",
        ]

        for pattern in patterns:
            matches = list(re.finditer(pattern, section_content))

            for i, match in enumerate(matches):
                # Extract title (usually first group)
                title = match.group(1)
                start = match.start()

                # Find the end of this subsection
                if i + 1 < len(matches):
                    end = matches[i + 1].start()
                else:
                    # Look for next major command or end of section
                    next_section = re.search(
                        r"\\(?:resumeSubHeadingListEnd|end\{itemize\})",
                        section_content[start:],
                    )
                    if next_section:
                        end = start + next_section.start()
                    else:
                        end = len(section_content)

                subsection_content = section_content[start:end]

                # Extract bullet points
                lines = self._extract_bullet_points(subsection_content)

                subsections.append(
                    ResumeSubsection(
                        title=title,
                        content=subsection_content,
                        lines=lines,
                        start_pos=base_offset + start,
                        end_pos=base_offset + end,
                    )
                )

            if subsections:  # If we found matches with this pattern, stop
                break

        return subsections

    def _parse_skills(
        self, section_content: str, base_offset: int
    ) -> List[ResumeSubsection]:
        """Parse skills section"""
        subsections = []

        # Look for \resumeSubItem or individual skill items
        skill_items = re.finditer(
            r"\\resumeSubItem\{([^}]+)\}\{([^}]+)\}", section_content
        )

        for i, match in enumerate(skill_items):
            title = match.group(1)
            content = match.group(2)

            subsections.append(
                ResumeSubsection(
                    title=title,
                    content=match.group(0),
                    lines=[content],
                    start_pos=base_offset + match.start(),
                    end_pos=base_offset + match.end(),
                )
            )

        return subsections

    def _extract_bullet_points(self, content: str) -> List[str]:
        """Extract individual bullet points from content"""
        lines = []

        # Look for \resumeItem{...}
        items = re.finditer(r"\\resumeItem\{([^}]+)\}", content)
        for item in items:
            lines.append(item.group(1))

        # Also look for plain \item commands
        if not lines:
            items = re.finditer(r"\\item\s+([^\n\\]+)", content)
            for item in items:
                lines.append(item.group(1).strip())

        return lines

    def rebuild_latex(
        self,
        original_content: str,
        parsed_structure: Dict[str, Any],
        selected_sections: Dict[str, bool],
        regenerated_sections: Dict[str, str],
    ) -> str:
        """
        Rebuild LaTeX with regenerated sections

        Args:
            original_content: Original LaTeX
            parsed_structure: Parsed structure from parse_resume()
            selected_sections: Dict of section_id -> True/False
            regenerated_sections: Dict of section_id -> new LaTeX content

        Returns:
            Updated LaTeX content
        """
        result = original_content

        # Replace sections from back to front to maintain positions
        sections_to_replace = []

        for section in parsed_structure["sections"]:
            section_id = f"{section.section_type}_{section.start_pos}"

            if section_id in regenerated_sections:
                sections_to_replace.append(
                    {
                        "start": section.start_pos,
                        "end": section.end_pos,
                        "new_content": regenerated_sections[section_id],
                    }
                )

        # Sort by start position (descending) to replace from back to front
        sections_to_replace.sort(key=lambda x: x["start"], reverse=True)

        for replacement in sections_to_replace:
            result = (
                result[: replacement["start"]]
                + replacement["new_content"]
                + result[replacement["end"] :]
            )

        return result

    def get_section_preview(self, section: ResumeSection, max_length: int = 200) -> str:
        """Get a readable preview of a section"""
        # Remove LaTeX commands for preview
        preview = re.sub(r"\\[a-zA-Z]+\*?\{([^}]*)\}", r"\1", section.content)
        preview = re.sub(r"\\[a-zA-Z]+\*?", "", preview)
        preview = preview.strip()

        if len(preview) > max_length:
            preview = preview[:max_length] + "..."

        return preview

```

### services/latex_service.py

```python
import os
import subprocess
from pathlib import Path
from typing import Tuple, Optional


class LatexService:
    def __init__(self, storage_path: str = "storage"):
        self.storage_path = Path(storage_path)
        self.generated_path = self.storage_path / "generated"
        self.base_resumes_path = self.storage_path / "base_resumes"

        # Ensure directories exist
        self.generated_path.mkdir(parents=True, exist_ok=True)
        self.base_resumes_path.mkdir(parents=True, exist_ok=True)

    def compile_latex(
        self, tex_content: str, output_filename: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Compile LaTeX content to PDF

        Returns:
            Tuple of (success: bool, pdf_path: str|None, error_message: str|None)
        """
        # Create unique temporary file path
        tex_path = self.generated_path / f"{output_filename}.tex"
        pdf_path = self.generated_path / f"{output_filename}.pdf"

        try:
            # Write LaTeX content to file
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_content)

            # Compile with pdflatex
            # Run twice to resolve references
            for _ in range(2):
                result = subprocess.run(
                    [
                        "pdflatex",
                        "-interaction=nonstopmode",
                        "-output-directory",
                        str(self.generated_path),
                        str(tex_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

            # Check if PDF was generated
            if pdf_path.exists():
                # Clean up auxiliary files
                self._cleanup_aux_files(output_filename)
                return True, str(pdf_path), None
            else:
                error_msg = result.stderr if result.stderr else "PDF generation failed"
                return False, None, error_msg

        except subprocess.TimeoutExpired:
            return False, None, "LaTeX compilation timeout"
        except Exception as e:
            return False, None, f"Compilation error: {str(e)}"

    def _cleanup_aux_files(self, base_filename: str):
        """Remove auxiliary LaTeX files"""
        aux_extensions = [".aux", ".log", ".out", ".toc"]
        for ext in aux_extensions:
            aux_file = self.generated_path / f"{base_filename}{ext}"
            if aux_file.exists():
                try:
                    aux_file.unlink()
                except:
                    pass

    def read_base_resume(self, latex_template_path: str) -> Optional[str]:
        """Read base resume template from storage"""
        try:
            full_path = self.base_resumes_path / latex_template_path
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error reading base resume: {e}")
            return None

    def save_base_resume(self, content: str, filename: str) -> str:
        """Save a base resume template"""
        file_path = self.base_resumes_path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return filename

    def extract_text_from_latex(self, latex_content: str) -> str:
        """
        Extract plain text from LaTeX (rough approximation)
        For better results, compile to PDF and extract from PDF
        """
        import re

        # Remove comments
        text = re.sub(r"%.*", "", latex_content)

        # Remove common LaTeX commands but keep their content
        text = re.sub(r"\\[a-zA-Z]+\*?\{([^}]*)\}", r"\1", text)
        text = re.sub(r"\\[a-zA-Z]+\*?", "", text)

        # Remove special characters
        text = text.replace("\\\\", "\n")
        text = text.replace("~", " ")
        text = text.replace("&", " ")

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n\s*\n", "\n\n", text)

        return text.strip()

```

### storage/base_resumes/a31e559f-8d9c-4389-a562-2e0b7314bf0e.tex

```
\documentclass[letterpaper,10pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{multicol}
\input{glyphtounicode}

\usepackage[default]{sourcesanspro}
\usepackage[T1]{fontenc}

\pagestyle{fancy}
\fancyhf{} 
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}


\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-4pt}\centering
}{}{0em}{}[\color{black}\titlerule\vspace{-5pt}]


\pdfgentounicode=1

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}



\begin{center}
    {\LARGE John Zlad Doe} \\ \vspace{2pt}
    \begin{multicols}{2}
    \begin{flushleft}
    \href{{your github page link}}{my github}\\
    \href{{your linkedin page link}}{my linkedin}
    \end{flushleft}
    
    \begin{flushright}
    \href{{your personal websit link}}{my personal site}\\
    \href{mailto:{your email adress}}{my email}
    \end{flushright}
    \end{multicols}
\end{center}


%-----------EDUCATION-----------
\vspace{-2pt}
\section{Education}
  \resumeSubHeadingListStart
      \resumeSubheading
      {University of Molvanîa -- UM}{Aug. 2019 -- Present}
      {PhD. Student in Technology}{Molvanîa, Mv}

  \resumeSubHeadingListEnd


%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Ph.D. Researcher}{Sep. 2019 -- Present}
      {Laser beams shooting research}{Molvanîa, Mv}
      \resumeItemListStart
        \resumeItem{Laser beams}
        \resumeItem{Laser cooling techniques}
        \resumeItem{Off blast!}
    \resumeItemListEnd

  \resumeSubHeadingListEnd

%-----------PUBLICATIONS-----------
\section{Publications}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
    \textbf{New techniques for Elektronik supersonik laser shootings. WORKSHOP ON INDUSTRY APPLICATION - Molvanîan Academy o Science, 2020 . p. 225-231.}{\\J. Zlad Doe}\\
        \textbf{Space Rockets . WORKSHOP ON INDUSTRY APPLICATION - Molvanîan Academy o Science, 2021 . p. 25-31.}{\\J. Zlad Doe, Darth Vapor}\\
\ 
}}
 \end{itemize}

%-----------PROGRAMMING SKILLS-----------
\section{Technical Skills, Language Skills, and Interests}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
    \textbf{OS}{: Windows} \\
     \textbf{Programming Languages}{: C/C++} \\
     \textbf{Libraries}{: OpenCV}\\
     \textbf{Version Control}{: Git} \\
     \textbf{Writing}{: \LaTeX, Office} \\
     \textbf{Languages}{: Molvanîan (native), English (fluent)} \\
     \textbf{Interests}{: Lasers and Music}
     
    }}
 \end{itemize}

%-----------CERTIFICATIONS-----------
\section{Extracurricular}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Specialization}{:\href{certification site}{ Course} } 
    }}
    
 \end{itemize}

\end{document}

```

### storage/base_resumes/base_resume_template.tex

```
%-------------------------
% Resume in LaTeX
% Author: Your Name
% License: MIT
%------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

%-------------------------
% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-1pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand{\labelitemii}{$\circ$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=*]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-------------------------------------------
%%%%%%  CV STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

\begin{document}

%----------HEADING-----------------
\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
  \textbf{\href{http://yourwebsite.com/}{\Large John Doe}} & Email: \href{mailto:john.doe@email.com}{john.doe@email.com}\\
  \href{http://yourwebsite.com/}{http://www.yourwebsite.com} & Mobile: +1-123-456-7890 \\
\end{tabular*}

%-----------SUMMARY-----------------
\section{Professional Summary}
  Results-driven software engineer with 5+ years of experience in full-stack development, specializing in Python, JavaScript, and cloud technologies. Proven track record of delivering scalable applications and leading cross-functional teams.

%-----------EXPERIENCE-----------------
\section{Experience}
  \resumeSubHeadingListStart

    \resumeSubheading
      {Senior Software Engineer}{Jan 2021 -- Present}
      {Tech Company Inc.}{San Francisco, CA}
      \resumeItemListStart
        \resumeItem{Led development of microservices architecture serving 1M+ users, improving system reliability by 40\%}
        \resumeItem{Architected and implemented RESTful APIs using Python/Flask, reducing response time by 35\%}
        \resumeItem{Mentored team of 5 junior developers, establishing code review practices and best practices}
        \resumeItem{Implemented CI/CD pipelines using Jenkins and Docker, reducing deployment time from hours to minutes}
        \resumeItem{Collaborated with product managers and designers to deliver 15+ features ahead of schedule}
      \resumeItemListEnd

    \resumeSubheading
      {Software Engineer}{Jun 2019 -- Dec 2020}
      {Startup XYZ}{Remote}
      \resumeItemListStart
        \resumeItem{Developed full-stack web applications using React, Node.js, and MongoDB}
        \resumeItem{Built and deployed machine learning models for recommendation system, increasing user engagement by 25\%}
        \resumeItem{Optimized database queries and indexing strategies, improving query performance by 60\%}
        \resumeItem{Participated in agile development process with bi-weekly sprints and daily standups}
      \resumeItemListEnd

    \resumeSubheading
      {Junior Developer}{May 2018 -- May 2019}
      {Software Solutions Ltd.}{New York, NY}
      \resumeItemListStart
        \resumeItem{Developed responsive web applications using HTML, CSS, JavaScript, and Bootstrap}
        \resumeItem{Contributed to open-source projects and maintained company's technical documentation}
        \resumeItem{Assisted in debugging and resolving production issues, reducing critical bugs by 30\%}
      \resumeItemListEnd

  \resumeSubHeadingListEnd

%-----------EDUCATION-----------------
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {University of California, Berkeley}{Berkeley, CA}
      {Bachelor of Science in Computer Science; GPA: 3.8}{Sep 2014 -- May 2018}
  \resumeSubHeadingListEnd

%-----------SKILLS-----------------
\section{Technical Skills}
  \resumeSubHeadingListStart
    \resumeSubItem{Languages: Python, JavaScript, TypeScript, Java, SQL, HTML/CSS}
    \resumeSubItem{Frameworks: React, Node.js, Flask, Django, Express.js, Vue.js}
    \resumeSubItem{Tools \& Technologies: Git, Docker, Kubernetes, AWS, MongoDB, PostgreSQL, Redis}
    \resumeSubItem{Methodologies: Agile/Scrum, TDD, CI/CD, Microservices Architecture}
  \resumeSubHeadingListEnd

%-----------PROJECTS-----------------
\section{Notable Projects}
  \resumeSubHeadingListStart
    \resumeSubItem{E-commerce Platform}
      {Built a scalable e-commerce platform using MERN stack, handling 10K+ daily transactions}
    \resumeSubItem{AI Chatbot}
      {Developed an AI-powered customer support chatbot using NLP and machine learning, reducing support tickets by 40\%}
    \resumeSubItem{Open Source Contributions}
      {Active contributor to popular open-source projects with 500+ stars on GitHub}
  \resumeSubHeadingListEnd

%-----------CERTIFICATIONS-----------------
\section{Certifications}
  \resumeSubHeadingListStart
    \resumeSubItem{AWS Certified Solutions Architect -- Associate (2022)}
    \resumeSubItem{Certified Kubernetes Administrator (2021)}
  \resumeSubHeadingListEnd

%-------------------------------------------
\end{document}

```

### storage/generated/resume_697b6c657e75610931541e23_1769696371.pdf

(Skipped: binary or unreadable file)


### storage/generated/resume_697b6c657e75610931541e23_1769696371.tex

```
\documentclass[letterpaper,10pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{multicol}
\input{glyphtounicode}

\usepackage[default]{sourcesanspro}
\usepackage[T1]{fontenc}

\pagestyle{fancy}
\fancyhf{} 
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}


\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-4pt}\centering
}{}{0em}{}[\color{black}\titlerule\vspace{-5pt}]


\pdfgentounicode=1

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}



\begin{center}
    {\LARGE John Zlad Doe} \\ \vspace{2pt}
    \begin{multicols}{2}
    \begin{flushleft}
    \href{{your github page link}}{my github}\\
    \href{{your linkedin page link}}{my linkedin}
    \end{flushleft}
    
    \begin{flushright}
    \href{{your personal websit link}}{my personal site}\\
    \href{mailto:{your email adress}}{my email}
    \end{flushright}
    \end{multicols}
\end{center}


%-----------EDUCATION-----------
\vspace{-2pt}
\section{Education}
  \resumeSubHeadingListStart
      \resumeSubheading
      {University of Molvanîa -- UM}{Aug. 2019 -- Present}
      {PhD. Student in Technology}{Molvanîa, Mv}

  \resumeSubHeadingListEnd


%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Ph.D. Researcher}{Sep. 2019 -- Present}
      {Laser beams shooting research}{Molvanîa, Mv}
      \resumeItemListStart
        \resumeItem{Designed and developed distributed software systems for laser beam control using object-oriented programming principles, implementing scalable backend services that process real-time data from multiple laser sources}
        \resumeItem{Built highly available microservices architecture using Java to manage laser cooling techniques, applying systematic problem-solving approach to optimize system performance and reliability across distributed cloud infrastructure}
        \resumeItem{Enhanced RESTful APIs and server-side components for laser control systems, debugging and improving existing software architecture to support mission-critical applications with 99.9\% uptime}
        \resumeItem{Applied software engineering best practices to develop scalable distributed services, collaborating with cross-functional teams to deliver robust solutions using containerized deployments and cloud-native infrastructure}
    \resumeItemListEnd

  \resumeSubHeadingListEnd

%-----------PUBLICATIONS-----------\section{Publications}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
    \textbf{New techniques for Elektronik supersonik laser shootings. WORKSHOP ON INDUSTRY APPLICATION - Molvanîan Academy o Science, 2020 . p. 225-231.}{\\J. Zlad Doe}\\
        \textbf{Space Rockets . WORKSHOP ON INDUSTRY APPLICATION - Molvanîan Academy o Science, 2021 . p. 25-31.}{\\J. Zlad Doe, Darth Vapor}\\
\ 
}}
 \end{itemize}

%-----------PROGRAMMING SKILLS-----------
\section{Technical Skills, Language Skills, and Interests}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
    \textbf{OS}{: Windows} \\
     \textbf{Programming Languages}{: C/C++} \\
     \textbf{Libraries}{: OpenCV}\\
     \textbf{Version Control}{: Git} \\
     \textbf{Writing}{: \LaTeX, Office} \\
     \textbf{Languages}{: Molvanîan (native), English (fluent)} \\
     \textbf{Interests}{: Lasers and Music}
     
    }}
 \end{itemize}

%-----------CERTIFICATIONS-----------
\section{Extracurricular}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Specialization}{:\href{certification site}{ Course} } 
    }}
    
 \end{itemize}

\end{document}

```

### views/applications/detail.html

```html
{% extends "layouts/dashboard.html" %}

{% block content %}
<div class="max-w-5xl">

    <!-- Header with Back Button -->
    <div class="flex items-center justify-between mb-6">
        <a href="/applications" class="text-gray-600 hover:text-black">
            ← Back to Applications
        </a>

        <button onclick="confirmDeleteApplication()"
            class="px-4 py-2 bg-red-600 text-white rounded-md text-sm hover:bg-red-700">
            Delete Application
        </button>
    </div>

    <!-- Application Info Card -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-6">
        <div class="flex justify-between items-start mb-4">
            <div>
                <h1 class="text-2xl font-semibold mb-2">
                    {% if application.position_title %}
                    {{ application.position_title }}
                    {% else %}
                    Job Application
                    {% endif %}
                </h1>

                {% if application.company_name %}
                <p class="text-gray-600">{{ application.company_name }}</p>
                {% endif %}
            </div>

            <!-- Status Badge -->
            <span class="px-3 py-1 rounded-full text-sm font-medium
                {% if application.status == 'completed' %}bg-green-100 text-green-800
                {% elif application.status == 'processing' %}bg-blue-100 text-blue-800
                {% elif application.status == 'failed' %}bg-red-100 text-red-800
                {% else %}bg-gray-100 text-gray-800{% endif %}">
                {{ application.status|capitalize }}
            </span>
        </div>

        <!-- Job Description -->
        <div class="mt-6">
            <h3 class="text-sm font-semibold text-gray-700 mb-2">Job Description</h3>
            <div class="bg-gray-50 rounded-lg p-4 text-sm text-gray-700 max-h-64 overflow-y-auto">
                {{ application.job_description }}
            </div>
        </div>

        <!-- AI Analysis (if available) -->
        {% if application.ai_analysis %}
        <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            {% if application.ai_analysis.required_skills %}
            <div>
                <h4 class="text-sm font-semibold text-gray-700 mb-2">Required Skills</h4>
                <div class="flex flex-wrap gap-2">
                    {% for skill in application.ai_analysis.required_skills[:5] %}
                    <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">{{ skill }}</span>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if application.ai_analysis.experience_level %}
            <div>
                <h4 class="text-sm font-semibold text-gray-700 mb-2">Experience Level</h4>
                <p class="text-sm text-gray-600 capitalize">{{ application.ai_analysis.experience_level }}</p>
            </div>
            {% endif %}
        </div>
        {% endif %}

        <!-- Action Buttons -->
        <div class="mt-6 flex gap-3">
            <button onclick="regenerateResume()"
                class="px-4 py-2 bg-black text-white rounded-md text-sm hover:bg-gray-800">
                Regenerate Resume
            </button>

            <button onclick="generateCoverLetter()"
                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50">
                Generate Cover Letter
            </button>
        </div>
    </div>

    <!-- Generated Assets -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <h2 class="text-lg font-semibold mb-4">Generated Documents</h2>

        {% if generated_assets %}
        <div class="space-y-3">
            {% for asset in generated_assets %}
            <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                <div>
                    <h3 class="font-medium text-gray-900">{{ asset.title }}</h3>
                    <p class="text-sm text-gray-500 mt-1">
                        {{ asset.type|capitalize }} • Version {{ asset.version }} •
                        {{ asset.created_at.strftime('%B %d, %Y at %I:%M %p') }}
                    </p>
                </div>

                <div class="flex gap-2">
                    {% if asset.pdf_path %}
                    <a href="/assets/{{ asset._id }}/download?type=pdf"
                        class="px-3 py-1 bg-black text-white rounded text-sm hover:bg-gray-800">
                        Download PDF
                    </a>
                    {% endif %}

                    {% if asset.tex_path %}
                    <a href="/assets/{{ asset._id }}/download?type=tex"
                        class="px-3 py-1 border border-gray-300 text-gray-700 rounded text-sm hover:bg-gray-50">
                        Download LaTeX
                    </a>
                    {% endif %}

                    {% if asset.type == 'cover_letter' %}
                    <button onclick="viewCoverLetter(this)" data-content="{{ asset.content_text|e }}"
                        class="px-3 py-1 border border-gray-300 text-gray-700 rounded text-sm hover:bg-gray-50">
                        View
                    </button>
                    {% endif %}

                    <button onclick="confirmDeleteAsset('{{ asset._id }}', '{{ asset.title }}')"
                        class="px-3 py-1 border border-red-300 text-red-700 rounded text-sm hover:bg-red-50">
                        Delete
                    </button>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="text-center py-8 text-gray-500">
            <p>No documents generated yet.</p>
            <p class="text-sm mt-2">Click "Regenerate Resume" to create your first tailored resume.</p>
        </div>
        {% endif %}
    </div>

</div>

<!-- Cover Letter Modal -->
<div id="coverLetterModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl w-full max-w-2xl p-6 max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-semibold">Cover Letter</h2>
            <button onclick="closeCoverLetterModal()" class="text-gray-500 hover:text-gray-700">
                ✕
            </button>
        </div>
        <div id="coverLetterContent" class="prose max-w-none whitespace-pre-wrap text-sm text-gray-700">
        </div>
    </div>
</div>

<!-- Loading Modal -->
<div id="loadingModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl p-8 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
        <p class="text-gray-700">Processing with AI...</p>
    </div>
</div>

<!-- Confirmation Modal -->
<div id="confirmModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl w-full max-w-md p-6">
        <h2 class="text-lg font-semibold mb-4">Confirm Delete</h2>
        <p id="confirmMessage" class="text-gray-700 mb-6"></p>
        <div class="flex justify-end gap-3">
            <button onclick="closeConfirmModal()"
                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50">
                Cancel
            </button>
            <button id="confirmButton" onclick="executeDelete()"
                class="px-4 py-2 bg-red-600 text-white rounded-md text-sm hover:bg-red-700">
                Delete
            </button>
        </div>
    </div>
</div>

<script>
    let deleteAction = null;

    function regenerateResume() {
        document.getElementById('loadingModal').classList.remove('hidden');

        fetch('/applications/{{ application._id }}/regenerate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loadingModal').classList.add('hidden');

                if (data.success) {
                    alert('Resume regenerated successfully!');
                    location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                document.getElementById('loadingModal').classList.add('hidden');
                alert('Error: ' + error.message);
            });
    }

    function generateCoverLetter() {
        document.getElementById('loadingModal').classList.remove('hidden');

        fetch('/applications/{{ application._id }}/cover-letter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loadingModal').classList.add('hidden');

                if (data.success) {
                    alert('Cover letter generated successfully!');
                    location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                document.getElementById('loadingModal').classList.add('hidden');
                alert('Error: ' + error.message);
            });
    }

    function viewCoverLetter(button) {
        const content = button.getAttribute('data-content');
        document.getElementById('coverLetterContent').textContent = content;
        document.getElementById('coverLetterModal').classList.remove('hidden');
    }

    function closeCoverLetterModal() {
        document.getElementById('coverLetterModal').classList.add('hidden');
    }

    function confirmDeleteApplication() {
        deleteAction = {
            type: 'application',
            id: '{{ application._id }}'
        };
        document.getElementById('confirmMessage').textContent =
            'Are you sure you want to delete this application? This will also delete all associated documents.';
        document.getElementById('confirmModal').classList.remove('hidden');
    }

    function confirmDeleteAsset(assetId, assetTitle) {
        deleteAction = {
            type: 'asset',
            id: assetId
        };
        document.getElementById('confirmMessage').textContent =
            `Are you sure you want to delete "${assetTitle}"?`;
        document.getElementById('confirmModal').classList.remove('hidden');
    }

    function closeConfirmModal() {
        document.getElementById('confirmModal').classList.add('hidden');
        deleteAction = null;
    }

    function executeDelete() {
        if (!deleteAction) return;

        if (deleteAction.type === 'application') {
            fetch('/applications/' + deleteAction.id, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = '/applications';
                    } else {
                        alert('Error deleting application');
                    }
                })
                .catch(error => {
                    alert('Error: ' + error.message);
                });
        } else if (deleteAction.type === 'asset') {
            fetch('/assets/' + deleteAction.id, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    closeConfirmModal();
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Error deleting document');
                    }
                })
                .catch(error => {
                    alert('Error: ' + error.message);
                });
        }
    }
</script>

{% endblock %}

```

### views/applications/index.html

```html
{% extends "layouts/dashboard.html" %}

{% block content %}
<div class="flex items-center justify-between mb-6">
    <h1 class="text-2xl font-semibold">Applications</h1>

    <button onclick="openModal()" class="px-4 py-2 bg-black text-white rounded-md text-sm">
        Create Application
    </button>
</div>

<table class="w-full bg-white border border-gray-200 rounded-xl text-sm">
    <thead class="border-b bg-gray-50">
        <tr>
            <th class="text-left p-3">Job Title</th>
            <th class="text-left p-3">Company</th>
            <th class="text-left p-3">Status</th>
            <th class="text-left p-3">Created</th>
        </tr>
    </thead>
    <tbody>
        {% for app in applications %}
        <tr onclick="window.location='/applications/{{ app._id }}'" class="cursor-pointer hover:bg-gray-50 border-b">
            <td class="p-3">{{ app.job_title or "—" }}</td>
            <td class="p-3">{{ app.company_name or "—" }}</td>
            <td class="p-3 capitalize">{{ app.status }}</td>
            <td class="p-3">
                {{ app.created_at.strftime('%b %d, %Y') }}
            </td>
        </tr>
        {% else %}
        <tr>
            <td colspan="4" class="p-6 text-center text-gray-500">
                No applications yet
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>

{% include "applications/modal.html" %}
{% endblock %}

```

### views/applications/modal.html

```html
<div id="modal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center">

    <div class="bg-white rounded-xl w-full max-w-xl p-6">

        <h2 class="text-lg font-semibold mb-4">
            New Application
        </h2>

        <form method="post" action="/applications">
            <textarea name="job_description" required rows="8" placeholder="Paste job description here..." class="w-full border border-gray-300 rounded-md p-3 text-sm
                       focus:ring-2 focus:ring-black"></textarea>

            <div class="mt-6 flex justify-end gap-3">
                <button type="button" onclick="closeModal()" class="text-sm text-gray-600">
                    Cancel
                </button>

                <button class="px-4 py-2 bg-black text-white rounded-md text-sm">
                    Create
                </button>
            </div>
        </form>

    </div>
</div>

<script>
    function openModal() {
        document.getElementById("modal").classList.remove("hidden");
    }
    function closeModal() {
        document.getElementById("modal").classList.add("hidden");
    }
</script>

```

### views/auth/login.html

```html
{% extends "layouts/auth.html" %}
{% set heading = "Welcome back" %}

{% block content %}
<form method="post" class="space-y-4">

    <input name="email" type="email" placeholder="Email"
        class="w-full px-4 py-2      border border-zinc-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-white" />

    <input name="password" type="password" placeholder="Password"
        class="w-full px-4 py-2  border border-zinc-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-white" />

    <button class="w-full py-2 rounded-lg bg-black text-white text-black font-medium hover:bg-gray-200 transition">
        Login
    </button>

    <p class="text-sm text-center text-zinc-400">
        New here?
        <a href="/signup" class="text-black underline">Create account</a>
    </p>

</form>
{% endblock %}

```

### views/auth/signup.html

```html
{% extends "layouts/auth.html" %}
{% set heading = "Create your account" %}

{% block content %}
<form method="post" class="space-y-4">

    <input name="name" placeholder="Full name" class="w-full px-4 py-2  border border-zinc-800 rounded-lg" />

    <input name="email" type="email" placeholder="Email" class="w-full px-4 py-2  border border-zinc-800 rounded-lg" />

    <input name="password" type="password" placeholder="Password"
        class="w-full px-4 py-2  border border-zinc-800 rounded-lg" />

    <button class="w-full py-2 bg-black  text-white rounded-lg font-medium">
        Sign up
    </button>

    <p class="text-sm text-center text-zinc-400">
        Already have an account?
        <a href="/login" class="underline text-black">Login</a>
    </p>

</form>
{% endblock %}

```

### views/dashboard/index.html

```html
{% extends "layouts/dashboard.html" %}

{% block content %}
<h1 class="text-2xl font-semibold mb-2">Dashboard</h1>
<p class="text-gray-600">
    Welcome back 👋
</p>
{% endblock %}

```

### views/layouts/auth.html

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <title>{{ title or "ApplyTailored" }}</title>
    <script src="https://cdn.tailwindcss.com"></script>

</head>

<body class="min-h-screen flex items-center justify-center  ">

    <div class="w-full max-w-md  border border-zinc-800 rounded-xl p-8 shadow-xl">
        <h1 class="text-2xl text-black font-semibold text-center mb-6">
            {{ heading }}
        </h1>

        {% if error %}
        <div class="mb-4 text-sm text-red-400 bg-red-950/40 border border-red-900 rounded-lg p-3">
            {{ error }}
        </div>
        {% endif %}

        {% block content %}{% endblock %}
    </div>

</body>

</html>

```

### views/layouts/dashboard.html

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <title>Dashboard • ApplyTailored</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>

<body class="min-h-screen flex bg-gray-50 text-gray-900">

    {% include "partials/sidebar.html" %}

    <main class="flex-1 p-10">
        {% block content %}{% endblock %}
    </main>

</body>


</html>

```

### views/layouts/signup.html

```html
{% extends "layouts/auth.html" %}
{% set heading = "Create your account" %}

{% block content %}
<form method="post" class="space-y-4">

    <input name="name" placeholder="Full name"
        class="w-full px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-white" />

    <input name="email" type="email" placeholder="Email"
        class="w-full px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-white" />

    <input name="password" type="password" placeholder="Password"
        class="w-full px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-white" />

    <button class="w-full py-2 rounded-lg bg-white text-black font-medium hover:bg-gray-200 transition">
        Sign up
    </button>

    <p class="text-sm text-center text-zinc-400">
        Already have an account?
        <a href="/login" class="text-white underline">Login</a>
    </p>

</form>
{% endblock %}

```

### views/partials/navbar.html

```html
<header class="border-b border-zinc-800 bg-zinc-950">
    <div class="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <span class="font-semibold tracking-tight text-white">ApplyTailored</span>

        <div class="flex items-center gap-4 text-sm">
            <a href="/profile" class="text-zinc-400 hover:text-white transition">Profile</a>
            <a href="/logout" class="text-zinc-400 hover:text-white transition">Logout</a>
        </div>
    </div>
</header>

```

### views/partials/sidebar.html

```html
<aside class="w-64 bg-white border-r border-gray-200 p-6 flex flex-col">
    <h2 class="text-sm font-semibold tracking-tight mb-8">
        ApplyTailored
    </h2>

    <nav class="space-y-3 text-sm">
        <a href="/dashboard" class="block px-2 py-1 rounded-md
           {{ 'bg-gray-100 text-black' if request.path == '/dashboard'
           else 'text-gray-600 hover:text-black hover:bg-gray-100' }}">
            Dashboard
        </a>

        <a href="/applications" class="block px-3 py-2 rounded-md
           {{ 'bg-gray-100 text-black'
              if request.path.startswith('/applications')
              else 'text-gray-600 hover:bg-gray-100 hover:text-black' }}">
            Applications
        </a>

        <a href="/profile" class="block px-2 py-1 rounded-md
           {{ 'bg-gray-100 text-black' if request.path == '/profile'
           else 'text-gray-600 hover:text-black hover:bg-gray-100' }}">
            Profile
        </a>
    </nav>

    <div class="mt-auto pt-8">
        <a href="/logout" class="block text-sm text-gray-500 hover:text-black">
            Logout
        </a>
    </div>
</aside>

```

### views/profile/index.html

```html
{% extends "layouts/dashboard.html" %}

{% block content %}
<div class="max-w-4xl">

    <h1 class="text-2xl font-semibold mb-6">Profile</h1>

    <!-- User Information -->
    <div class="bg-white border border-gray-200 rounded-xl shadow-sm divide-y mb-6">

        <!-- Name -->
        <div class="px-6 py-4">
            <p class="text-sm text-gray-500">Name</p>
            <p class="text-base font-medium text-gray-900">
                {{ user.name }}
            </p>
        </div>

        <!-- Email -->
        <div class="px-6 py-4">
            <p class="text-sm text-gray-500">Email</p>
            <p class="text-base text-gray-900">
                {{ user.email }}
            </p>
        </div>

        <!-- Role -->
        <div class="px-6 py-4">
            <p class="text-sm text-gray-500">Role</p>
            <p class="text-base capitalize text-gray-900">
                {{ user.role }}
            </p>
        </div>

        <!-- Created -->
        <div class="px-6 py-4">
            <p class="text-sm text-gray-500">Account created</p>
            <p class="text-base text-gray-900">
                {{ user.created_at.strftime('%B %d, %Y') }}
            </p>
        </div>

    </div>

    <!-- Base Resumes Section -->
    <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold">Base Resume Templates</h2>
            <button onclick="openUploadModal()"
                class="px-4 py-2 bg-black text-white rounded-md text-sm hover:bg-gray-800">
                Upload New Template
            </button>
        </div>

        <p class="text-sm text-gray-600 mb-4">
            Upload your resume in LaTeX format. Configure which sections to regenerate automatically for each job.
        </p>

        {% if base_resumes %}
        <div class="space-y-3">
            {% for resume in base_resumes %}
            <div class="p-4 border border-gray-200 rounded-lg 
                        {% if resume.is_active %}bg-green-50 border-green-200{% else %}hover:bg-gray-50{% endif %}">

                <!-- Resume Header -->
                <div class="flex items-start justify-between mb-3">
                    <div class="flex-1">
                        <div class="flex items-center gap-3">
                            <h3 class="font-medium text-gray-900">{{ resume.title }}</h3>
                            {% if resume.is_active %}
                            <span class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                                Active
                            </span>
                            {% endif %}
                            {% if resume.class_file %}
                            <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                                + Class File
                            </span>
                            {% endif %}

                            <!-- NEW: Selective Regeneration Status Badge -->
                            {% if resume.section_preferences and resume.section_preferences.enabled %}
                            <span
                                class="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium flex items-center gap-1">
                                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                        clip-rule="evenodd"></path>
                                </svg>
                                Selective ({{ resume.section_preferences.selected_sections|length }} sections)
                            </span>
                            {% endif %}
                        </div>
                        {% if resume.description %}
                        <p class="text-sm text-gray-600 mt-1">{{ resume.description }}</p>
                        {% endif %}
                        <p class="text-xs text-gray-500 mt-1">
                            Uploaded {{ resume.created_at.strftime('%B %d, %Y') }}
                            {% if resume.class_file %}
                            • Includes: {{ resume.class_file }}
                            {% endif %}
                        </p>
                    </div>

                    <!-- Toggle Switch -->
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" class="sr-only peer" {% if resume.is_active %}checked{% endif %}
                            onchange="toggleActiveResume('{{ resume._id }}', this.checked)">
                        <div
                            class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600">
                        </div>
                        <span class="ml-3 text-sm font-medium text-gray-900">Active</span>
                    </label>
                </div>

                <!-- Action Buttons -->
                <div class="flex flex-wrap gap-2">
                    <!-- NEW: Section Preferences Button -->
                    <a href="/resume/{{ resume._id }}/preferences"
                        class="px-3 py-1.5 bg-purple-600 text-white rounded-md text-sm hover:bg-purple-700 flex items-center gap-1.5">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4">
                            </path>
                        </svg>
                        Section Preferences
                    </a>

                    <a href="/base-resumes/{{ resume._id }}/download"
                        class="px-3 py-1.5 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50">
                        Download .tex
                    </a>

                    {% if resume.class_file %}
                    <a href="/base-resumes/{{ resume._id }}/download-class"
                        class="px-3 py-1.5 border border-blue-300 text-blue-700 rounded-md text-sm hover:bg-blue-50">
                        Download .cls
                    </a>
                    {% endif %}

                    {% if not resume.is_active %}
                    <button onclick="confirmDeleteResume('{{ resume._id }}', '{{ resume.title }}')"
                        class="px-3 py-1.5 border border-red-300 text-red-700 rounded-md text-sm hover:bg-red-50">
                        Delete
                    </button>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="text-center py-8 text-gray-500">
            <p>No base resume templates uploaded yet.</p>
            <p class="text-sm mt-2">Upload a LaTeX template to get started.</p>
        </div>
        {% endif %}
    </div>

</div>

<!-- Upload Modal -->
<div id="uploadModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-semibold">Upload Base Resume Template</h2>
            <button onclick="closeUploadModal()" class="text-gray-500 hover:text-gray-700">
                ✕
            </button>
        </div>

        <form method="POST" action="/base-resumes" enctype="multipart/form-data" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Template Title
                </label>
                <input type="text" name="title" required placeholder="e.g., Professional Resume 2024"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-black focus:outline-none">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Description (optional)
                </label>
                <textarea name="description" rows="2" placeholder="Brief description of this template"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-black focus:outline-none"></textarea>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    LaTeX File (.tex) *
                </label>
                <input type="file" name="latex" accept=".tex" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-black focus:outline-none">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Class File (.cls) - Optional
                </label>
                <input type="file" name="class_file" accept=".cls"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-black focus:outline-none">
                <p class="text-xs text-gray-500 mt-1">
                    Upload if your resume uses a custom class (e.g., lmdEN.cls, moderncv.cls)
                </p>
            </div>

            <div class="bg-blue-50 border border-blue-200 rounded-md p-3">
                <p class="text-xs text-blue-800">
                    <strong>Tip:</strong> After uploading, click "Section Preferences" to choose which sections to
                    auto-regenerate for each job.
                </p>
            </div>

            <div class="flex justify-end gap-3 mt-6">
                <button type="button" onclick="closeUploadModal()"
                    class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50">
                    Cancel
                </button>
                <button type="submit" class="px-4 py-2 bg-black text-white rounded-md text-sm hover:bg-gray-800">
                    Upload Template
                </button>
            </div>
        </form>
    </div>
</div>

<!-- Confirmation Modal -->
<div id="confirmModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl w-full max-w-md p-6">
        <h2 class="text-lg font-semibold mb-4">Confirm Delete</h2>
        <p id="confirmMessage" class="text-gray-700 mb-6"></p>
        <div class="flex justify-end gap-3">
            <button onclick="closeConfirmModal()"
                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50">
                Cancel
            </button>
            <button id="confirmButton" onclick="executeDelete()"
                class="px-4 py-2 bg-red-600 text-white rounded-md text-sm hover:bg-red-700">
                Delete
            </button>
        </div>
    </div>
</div>

<!-- Loading Modal -->
<div id="loadingModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl p-8 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
        <p class="text-gray-700">Updating...</p>
    </div>
</div>

<script>
    let deleteResumeId = null;

    function openUploadModal() {
        document.getElementById('uploadModal').classList.remove('hidden');
    }

    function closeUploadModal() {
        document.getElementById('uploadModal').classList.add('hidden');
    }

    function toggleActiveResume(resumeId, isChecked) {
        document.getElementById('loadingModal').classList.remove('hidden');

        if (isChecked) {
            fetch('/base-resumes/' + resumeId + '/activate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loadingModal').classList.add('hidden');
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Error: ' + (data.error || 'Failed to activate resume'));
                        location.reload();
                    }
                })
                .catch(error => {
                    document.getElementById('loadingModal').classList.add('hidden');
                    alert('Error: ' + error.message);
                    location.reload();
                });
        } else {
            document.getElementById('loadingModal').classList.add('hidden');
            alert('You must have at least one active resume. Please activate another resume first.');
            location.reload();
        }
    }

    function confirmDeleteResume(resumeId, resumeTitle) {
        deleteResumeId = resumeId;
        document.getElementById('confirmMessage').textContent =
            `Are you sure you want to delete "${resumeTitle}"?`;
        document.getElementById('confirmModal').classList.remove('hidden');
    }

    function closeConfirmModal() {
        document.getElementById('confirmModal').classList.add('hidden');
        deleteResumeId = null;
    }

    function executeDelete() {
        if (!deleteResumeId) return;

        document.getElementById('confirmModal').classList.add('hidden');
        document.getElementById('loadingModal').classList.remove('hidden');

        fetch('/base-resumes/' + deleteResumeId, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loadingModal').classList.add('hidden');
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error: ' + (data.error || 'Failed to delete resume'));
                }
            })
            .catch(error => {
                document.getElementById('loadingModal').classList.add('hidden');
                alert('Error: ' + error.message);
            });
    }
</script>

{% endblock %}

```

### views/resume/section_preferences.html

```html
{% extends "layouts/dashboard.html" %}

{% block content %}
<div class="max-w-5xl mx-auto">

    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
        <div>
            <a href="/profile" class="text-gray-600 hover:text-black mb-2 inline-block">
                ← Back to Profile
            </a>
            <h1 class="text-2xl font-semibold">Section Preferences</h1>
            <p class="text-gray-600 mt-1">
                Choose which sections to automatically regenerate for new job applications
            </p>
        </div>
    </div>

    <!-- Info Card -->
    <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
        <div class="flex gap-3">
            <svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor"
                viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div>
                <p class="text-sm text-blue-800 font-medium mb-1">How this works:</p>
                <ul class="text-sm text-blue-700 space-y-1">
                    <li>• Select which sections you want to be updated for each job application</li>
                    <li>• When you create a new application, only these sections will be regenerated</li>
                    <li>• Other sections will stay exactly as they are in your base resume</li>
                    <li>• This gives you precise control and faster processing</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Left: Controls -->
        <div class="lg:col-span-1">
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 sticky top-6">
                <h2 class="text-lg font-semibold mb-4">Controls</h2>

                <!-- Enable/Disable Toggle -->
                <div class="mb-6">
                    <label class="flex items-center justify-between cursor-pointer">
                        <span class="text-sm font-medium text-gray-700">Enable Selective Regeneration</span>
                        <div class="relative">
                            <input type="checkbox" id="enableSelective" onchange="toggleSelective(this.checked)"
                                class="sr-only peer">
                            <div
                                class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600">
                            </div>
                        </div>
                    </label>
                    <p class="text-xs text-gray-500 mt-2">
                        When enabled, new applications will only regenerate selected sections
                    </p>
                </div>

                <!-- Status Display -->
                <div id="statusDisplay" class="hidden mb-6 p-3 bg-green-50 border border-green-200 rounded-md">
                    <p class="text-sm text-green-800 font-medium mb-1">
                        ✓ Selective regeneration enabled
                    </p>
                    <p class="text-xs text-green-700">
                        <span id="sectionCount">0</span> sections will be regenerated
                    </p>
                </div>

                <!-- Buttons -->
                <div class="space-y-3">
                    <button onclick="loadSections()"
                        class="w-full px-4 py-2 bg-black text-white rounded-md text-sm hover:bg-gray-800">
                        Load Resume Sections
                    </button>

                    <button onclick="selectAllSections()" id="selectAllBtn"
                        class="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50"
                        disabled>
                        Select All Sections
                    </button>

                    <button onclick="clearAllSections()" id="clearAllBtn"
                        class="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50"
                        disabled>
                        Clear All
                    </button>

                    <button onclick="savePreferences()" id="saveBtn"
                        class="w-full px-4 py-2 bg-green-600 text-white rounded-md text-sm hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled>
                        Save Preferences
                    </button>
                </div>
            </div>
        </div>

        <!-- Right: Resume Sections -->
        <div class="lg:col-span-2">
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <h2 class="text-lg font-semibold mb-4">Resume Sections</h2>

                <!-- Loading State -->
                <div id="sectionsLoading" class="text-center py-12">
                    <svg class="animate-spin h-8 w-8 text-gray-400 mx-auto mb-3" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                        </circle>
                        <path class="opacity-75" fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                        </path>
                    </svg>
                    <p class="text-gray-600">Click "Load Resume Sections" to view your resume structure</p>
                </div>

                <!-- Sections Container -->
                <div id="sectionsContainer" class="space-y-3 hidden">
                    <!-- Sections will be loaded here -->
                </div>
            </div>
        </div>

    </div>

</div>

<!-- Success Modal -->
<div id="successModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl p-8 text-center max-w-md">
        <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
        </div>
        <h3 class="text-lg font-semibold mb-2">Preferences Saved!</h3>
        <p class="text-gray-600 mb-6">
            Your section preferences have been saved. New applications will automatically use these settings.
        </p>
        <button onclick="closeSuccessModal()"
            class="px-6 py-2 bg-black text-white rounded-md text-sm hover:bg-gray-800">
            Got it
        </button>
    </div>
</div>

<script>
    const resumeId = '{{ resume_id }}';
    let sectionsData = [];
    let selectedSections = new Set();
    let selectiveEnabled = false;

    // Load existing preferences on page load
    window.addEventListener('DOMContentLoaded', async () => {
        try {
            const response = await fetch(`/resume/${resumeId}/preferences/get`);
            const data = await response.json();

            if (data.success) {
                const prefs = data.preferences;
                selectiveEnabled = prefs.enabled || false;
                selectedSections = new Set(prefs.selected_sections || []);

                document.getElementById('enableSelective').checked = selectiveEnabled;
                updateStatusDisplay();

                // If sections were previously loaded, show them
                if (prefs.parsed_structure) {
                    sectionsData = prefs.parsed_structure;
                    renderSections(sectionsData);
                    document.getElementById('sectionsLoading').classList.add('hidden');
                    document.getElementById('sectionsContainer').classList.remove('hidden');
                    enableButtons();
                }
            }
        } catch (error) {
            console.error('Error loading preferences:', error);
        }
    });

    function toggleSelective(enabled) {
        selectiveEnabled = enabled;
        updateStatusDisplay();

        if (enabled && sectionsData.length === 0) {
            alert('Please load resume sections first');
            document.getElementById('enableSelective').checked = false;
            selectiveEnabled = false;
        }
    }

    function updateStatusDisplay() {
        const statusDisplay = document.getElementById('statusDisplay');
        const sectionCount = document.getElementById('sectionCount');

        if (selectiveEnabled) {
            statusDisplay.classList.remove('hidden');
            sectionCount.textContent = selectedSections.size;
        } else {
            statusDisplay.classList.add('hidden');
        }

        // Enable/disable save button
        document.getElementById('saveBtn').disabled = !selectiveEnabled;
    }

    async function loadSections() {
        document.getElementById('sectionsLoading').innerHTML = `
        <svg class="animate-spin h-8 w-8 text-gray-400 mx-auto mb-3" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-gray-600">Loading resume structure...</p>
    `;

        try {
            const response = await fetch(`/resume/${resumeId}/sections`);
            const data = await response.json();

            if (data.success) {
                sectionsData = data.sections;
                renderSections(sectionsData);
                document.getElementById('sectionsLoading').classList.add('hidden');
                document.getElementById('sectionsContainer').classList.remove('hidden');
                enableButtons();
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            alert('Error loading sections: ' + error.message);
        }
    }

    function renderSections(sections) {
        const container = document.getElementById('sectionsContainer');
        container.innerHTML = '';

        sections.forEach(section => {
            const isSelected = selectedSections.has(section.id);

            const sectionDiv = document.createElement('div');
            sectionDiv.className = `border rounded-lg p-4 transition ${isSelected ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-gray-300'
                }`;

            sectionDiv.innerHTML = `
            <div class="flex items-start gap-3">
                <input 
                    type="checkbox" 
                    id="section_${section.id}"
                    ${isSelected ? 'checked' : ''}
                    onchange="toggleSection('${section.id}', this.checked)"
                    class="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500 mt-1"
                >
                <div class="flex-1">
                    <label for="section_${section.id}" class="cursor-pointer">
                        <div class="flex items-center gap-2 mb-2">
                            <h3 class="font-medium text-gray-900">${section.title}</h3>
                            <span class="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs uppercase">
                                ${section.type}
                            </span>
                        </div>
                        <p class="text-sm text-gray-600 mb-2">${section.preview}</p>
                    </label>
                    
                    ${section.has_subsections ? `
                        <details class="mt-3">
                            <summary class="text-sm text-gray-500 cursor-pointer hover:text-gray-700">
                                ${section.subsections.length} subsection(s) • Click to expand
                            </summary>
                            <div class="mt-2 pl-4 space-y-2">
                                ${section.subsections.map(sub => `
                                    <div class="text-sm border-l-2 border-gray-200 pl-3 py-1">
                                        <p class="font-medium text-gray-700">${sub.title}</p>
                                        <p class="text-xs text-gray-500">${sub.line_count} bullet point(s)</p>
                                    </div>
                                `).join('')}
                            </div>
                        </details>
                    ` : ''}
                </div>
            </div>
        `;

            container.appendChild(sectionDiv);
        });
    }

    function toggleSection(sectionId, isChecked) {
        if (isChecked) {
            selectedSections.add(sectionId);
        } else {
            selectedSections.delete(sectionId);
        }

        updateStatusDisplay();
        renderSections(sectionsData);
    }

    function selectAllSections() {
        sectionsData.forEach(section => {
            selectedSections.add(section.id);
            const checkbox = document.getElementById(`section_${section.id}`);
            if (checkbox) checkbox.checked = true;
        });

        updateStatusDisplay();
        renderSections(sectionsData);
    }

    function clearAllSections() {
        selectedSections.clear();

        sectionsData.forEach(section => {
            const checkbox = document.getElementById(`section_${section.id}`);
            if (checkbox) checkbox.checked = false;
        });

        updateStatusDisplay();
        renderSections(sectionsData);
    }

    function enableButtons() {
        document.getElementById('selectAllBtn').disabled = false;
        document.getElementById('clearAllBtn').disabled = false;
    }

    async function savePreferences() {
        const saveBtn = document.getElementById('saveBtn');
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';

        try {
            const response = await fetch(`/resume/${resumeId}/preferences`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    enabled: selectiveEnabled,
                    selected_sections: Array.from(selectedSections)
                })
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('successModal').classList.remove('hidden');
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            alert('Error saving preferences: ' + error.message);
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save Preferences';
        }
    }

    function closeSuccessModal() {
        document.getElementById('successModal').classList.add('hidden');
    }
</script>

{% endblock %}

```

```

### QUICK_START.md

```markdown
# Quick Start Guide - Updating Your Existing Project

This guide will help you integrate the AI-powered resume tailoring features into your existing ApplyTailored project.

## Step-by-Step Integration

### 1. Install New Dependencies

Add to your `requirements.txt`:
```bash
anthropic==0.40.0
pydantic==2.5.3
```

Install:
```bash
pip install anthropic pydantic
```

### 2. Set Up Environment Variables

Add to your `.env` file:
```env
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

Get your API key from: https://console.anthropic.com/

### 3. Add New Models

Replace/add these files in your `models/` directory:

- `models/base_resume.py` - NEW
- `models/generated_asset.py` - NEW  
- `models/job_application.py` - UPDATE with the enhanced version

### 4. Create Services Directory

Create a new `services/` directory and add:

- `services/claude_ai_service.py` - Handles all Claude API interactions
- `services/latex_service.py` - Compiles LaTeX to PDF

### 5. Update Controllers

**Replace** your existing files with the updated versions:

- `controllers/ai_controller.py` → Use `controllers/ai_controller_updated.py`
- `controllers/application_controller.py` → Use `controllers/application_controller_updated.py`

### 6. Update Routes

**Replace**:
- `routes/application_routes.py` → Use `routes/application_routes_updated.py`

This adds new endpoints:
- `/applications/<id>/regenerate` - Regenerate resume
- `/applications/<id>/cover-letter` - Generate cover letter
- `/assets/<id>/download` - Download files

### 7. Update Views

**Replace**:
- `views/applications/detail.html` → Use `views/applications/detail_updated.html`

This adds:
- AI analysis display
- Generated documents list
- Action buttons for regeneration
- Cover letter modal

### 8. Set Up Storage Directory

Create the storage structure:
```bash
mkdir -p storage/base_resumes
mkdir -p storage/generated
```

Add the base resume template:
- Copy `storage/base_resumes/base_resume_template.tex` to your project

### 9. Initialize Database

Run the seeding script to set up collections and indexes:
```bash
python seed_database.py
```

This will:
- Create database indexes for performance
- Add a default base resume entry
- Verify storage directories

### 10. Update app.py (if needed)

Make sure your `app.py` imports the updated routes:

```python
from routes.application_routes_updated import application_routes
```

### 11. Install LaTeX (if not already installed)

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install texlive-full
```

**macOS**:
```bash
brew install --cask mactex
```

**Windows**:
Download and install MiKTeX from: https://miktex.org/

Verify installation:
```bash
pdflatex --version
```

## File Replacement Summary

### Files to ADD (new):
```
models/base_resume.py
models/generated_asset.py
services/claude_ai_service.py
services/latex_service.py
seed_database.py
storage/base_resumes/base_resume_template.tex
```

### Files to REPLACE (updated versions):
```
controllers/ai_controller.py
controllers/application_controller.py
routes/application_routes.py
views/applications/detail.html
requirements.txt
```

### Files to KEEP (no changes needed):
```
app.py (minor import update only)
config.py
db.py
models/user.py
controllers/auth_controller.py
controllers/dashboard_controller.py
controllers/profile_controller.py
middlewares/auth_middleware.py
routes/auth_routes.py
routes/dashboard_routes.py
routes/profile_routes.py
All other views/
```

## Testing the Integration

### 1. Start MongoDB
```bash
# Linux
sudo systemctl start mongod

# macOS
brew services start mongodb-community
```

### 2. Run Database Seeding
```bash
python seed_database.py
```

Expected output:
```
✓ Verified directory: storage
✓ Verified directory: storage/base_resumes
✓ Verified directory: storage/generated
✓ Created index on users.email
✓ Created indexes on applications collection
✓ Created index on base_resumes.user_id
✓ Created indexes on generated_assets collection
✓ Created default base resume
✅ Database seeding completed successfully!
```

### 3. Start the Application
```bash
python app.py
```

### 4. Test the Flow

1. **Login/Signup**: Create an account or login
2. **Create Application**: 
   - Go to Applications
   - Click "New Application"
   - Paste a job description
   - Submit

3. **Watch AI Process**:
   - You'll be redirected to application detail
   - Status should show "processing" → "completed"
   - Generated resume will appear

4. **Test Actions**:
   - Click "Download PDF" to get tailored resume
   - Click "Generate Cover Letter" to create one
   - Click "Regenerate Resume" to create new version

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'anthropic'"
**Solution**: 
```bash
pip install anthropic
```

### Issue: "pdflatex: command not found"
**Solution**: Install LaTeX distribution (see step 11 above)

### Issue: "Application status stuck on 'processing'"
**Solution**:
1. Check logs for errors
2. Verify ANTHROPIC_API_KEY is set correctly
3. Check if LaTeX is installed properly
4. Look at MongoDB for error details in the application document

### Issue: "LaTeX compilation failed"
**Solution**:
1. Check `storage/generated/*.log` files for LaTeX errors
2. System will fallback to base resume automatically
3. Verify base resume template is valid LaTeX

### Issue: MongoDB connection error
**Solution**:
1. Ensure MongoDB is running
2. Check MONGO_URI in `.env` file
3. Verify database permissions

## Architecture Overview

```
User submits job description
         ↓
Application created in DB (status: draft)
         ↓
AI Controller processes application
         ↓
    ┌────────────────────┐
    │ Claude AI Service  │
    │ - Analyze job desc │
    │ - Tailor resume    │
    └────────────────────┘
         ↓
    ┌────────────────────┐
    │  LaTeX Service     │
    │ - Compile to PDF   │
    │ - Fallback if fail │
    └────────────────────┘
         ↓
Generated Asset saved to DB
         ↓
Application status: completed
         ↓
User downloads PDF
```

## Environment Variables Checklist

Make sure your `.env` file has:

```env
✓ SECRET_KEY=...
✓ JWT_SECRET=...
✓ MONGO_URI=...
✓ DB_NAME=...
✓ ANTHROPIC_API_KEY=...  ← NEW!
```

## Next Steps After Integration

1. **Customize Base Resume**: 
   - Edit `storage/base_resumes/base_resume_template.tex`
   - Add your personal information
   - Adjust formatting to your preference

2. **Test with Real Job Postings**:
   - Copy real job descriptions
   - See how Claude tailors your resume
   - Adjust prompts if needed

3. **Monitor AI Usage**:
   - Check Anthropic console for API usage
   - Each application processes = ~2-3 API calls
   - Set up billing alerts if needed

4. **Production Considerations**:
   - Move AI processing to background jobs (Celery)
   - Add rate limiting
   - Implement caching for job analysis
   - Set up error monitoring

## Support

If you encounter issues:

1. Check the main README.md for detailed documentation
2. Review error logs in the console
3. Check MongoDB for application status and errors
4. Verify all environment variables are set

## Success Checklist

Before considering integration complete:

- [ ] All new files added
- [ ] All files updated/replaced
- [ ] Dependencies installed
- [ ] LaTeX installed and working
- [ ] MongoDB seeding completed
- [ ] Environment variables set
- [ ] Application starts without errors
- [ ] Can create account and login
- [ ] Can create new application
- [ ] Application processes with AI successfully
- [ ] Can download generated PDF
- [ ] Can generate cover letter

Congratulations! Your ApplyTailored system now has AI-powered resume tailoring! 🎉

```

### README.md

```markdown
# ApplyTailored - AI-Powered Resume Tailoring System

An intelligent job application management system that uses Claude AI to automatically tailor resumes to job descriptions.

## Features

- 🤖 **AI-Powered Resume Tailoring**: Uses Claude Sonnet 4 to analyze job descriptions and customize your resume
- 📄 **LaTeX Resume Generation**: Compiles professional PDFs from LaTeX templates
- 💼 **Job Application Tracking**: Manage all your job applications in one place
- 📊 **Job Analysis**: Automatically extracts key information from job descriptions
- ✉️ **Cover Letter Generation**: AI-generated cover letters tailored to each position
- 👤 **User Authentication**: Secure JWT-based authentication system
- 📁 **Document Management**: Store and download generated resumes and cover letters

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **AI**: Anthropic Claude API
- **Document Processing**: LaTeX (pdflatex)
- **Authentication**: JWT
- **Frontend**: HTML, Tailwind CSS, Jinja2

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.8+**
2. **MongoDB** (running locally or remote)
3. **LaTeX Distribution**:
   - **Linux**: `sudo apt-get install texlive-full`
   - **macOS**: `brew install --cask mactex`
   - **Windows**: Install MiKTeX from https://miktex.org/
4. **Anthropic API Key**: Sign up at https://console.anthropic.com/

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd applytailored
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET=your-jwt-secret-key-change-this
MONGO_URI=mongodb://localhost:27017
DB_NAME=applytailored
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

### 5. Initialize Database

Run the seeding script to set up initial data and indexes:

```bash
python seed_database.py
```

This will:
- Create necessary MongoDB indexes
- Set up the default base resume template
- Verify storage directories exist

### 6. Verify LaTeX Installation

Test if pdflatex is installed:

```bash
pdflatex --version
```

If you see version information, you're good to go!

## Project Structure

```
applytailored/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── db.py                          # Database connection
├── seed_database.py               # Database initialization script
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
│
├── controllers/
│   ├── ai_controller_updated.py           # AI processing logic
│   ├── application_controller_updated.py  # Application CRUD operations
│   ├── auth_controller.py                 # Authentication logic
│   ├── dashboard_controller.py            # Dashboard logic
│   └── profile_controller.py              # Profile management
│
├── models/
│   ├── user.py                    # User model
│   ├── job_application_updated.py # Enhanced job application model
│   ├── base_resume.py             # Base resume template model
│   └── generated_asset.py         # Generated documents model
│
├── services/
│   ├── claude_ai_service.py       # Claude API integration
│   └── latex_service.py           # LaTeX compilation service
│
├── routes/
│   ├── auth_routes.py             # Authentication routes
│   ├── dashboard_routes.py        # Dashboard routes
│   ├── profile_routes.py          # Profile routes
│   └── application_routes_updated.py  # Application routes with AI features
│
├── middlewares/
│   └── auth_middleware.py         # JWT authentication middleware
│
├── views/                         # HTML templates (Jinja2)
│   ├── layouts/
│   ├── partials/
│   ├── auth/
│   ├── dashboard/
│   ├── profile/
│   └── applications/
│       ├── index.html
│       ├── modal.html
│       └── detail_updated.html    # Enhanced detail view
│
└── storage/
    ├── base_resumes/
    │   └── base_resume_template.tex  # Default resume template
    └── generated/                    # Generated PDFs and LaTeX files
```

## Usage

### 1. Start the Application

```bash
python app.py
```

The application will run on `http://localhost:5000`

### 2. Create an Account

1. Navigate to `http://localhost:5000/signup`
2. Create your account
3. Login with your credentials

### 3. Create a Job Application

1. Go to **Applications** in the sidebar
2. Click **New Application**
3. Paste the job description
4. Click **Create**

The system will automatically:
- Analyze the job description
- Extract key information (company, position, skills)
- Tailor your base resume to match the job
- Compile a professional PDF
- Store everything in your application

### 4. View Generated Documents

1. Click on any application to view details
2. See AI analysis of the job
3. Download generated PDF resume
4. Generate cover letters on demand

### 5. Customize Base Resume

To use your own resume:

1. Create a LaTeX version of your resume
2. Save it in `storage/base_resumes/`
3. Add an entry to the `base_resumes` collection in MongoDB:

```python
db.base_resumes.insert_one({
    "_id": "your-unique-id",
    "user_id": "your-user-id",
    "title": "My Professional Resume",
    "description": "My main resume template",
    "latex_template_path": "my_resume.tex",
    "created_at": datetime.now(timezone.utc),
    "updated_at": datetime.now(timezone.utc)
})
```

## API Endpoints

### Authentication
- `GET /signup` - Signup page
- `POST /signup` - Create account
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - Logout user

### Applications
- `GET /applications` - List all applications
- `POST /applications` - Create new application (triggers AI processing)
- `GET /applications/<id>` - View application details
- `POST /applications/<id>/regenerate` - Regenerate resume
- `POST /applications/<id>/cover-letter` - Generate cover letter

### Assets
- `GET /assets/<id>/download` - Download generated PDF/TEX

## Database Collections

### users
```javascript
{
  _id: ObjectId,
  email: String (unique),
  name: String,
  password: String (hashed),
  role: String (default: "user"),
  created_at: DateTime
}
```

### applications
```javascript
{
  _id: ObjectId,
  user_id: String,
  job_description: String,
  company_name: String (optional),
  position_title: String (optional),
  status: String (draft/processing/completed/failed),
  base_resume_id: String (optional),
  generated_resume_id: String (optional),
  ai_analysis: Object (optional),
  created_at: DateTime,
  updated_at: DateTime
}
```

### base_resumes
```javascript
{
  _id: String,
  user_id: String,
  title: String,
  description: String,
  latex_template_path: String,
  created_at: DateTime,
  updated_at: DateTime
}
```

### generated_assets
```javascript
{
  _id: String,
  job_application_id: String,
  user_id: String,
  type: String (resume/cover_letter/cold_email/followup/question_answer),
  title: String,
  content_text: String,
  pdf_path: String (optional),
  tex_path: String (optional),
  ai_model: String,
  version: Integer,
  created_at: DateTime
}
```

## AI Features

### Resume Tailoring Process

1. **Job Analysis**: Claude analyzes the job description to extract:
   - Company name
   - Position title
   - Required skills
   - Preferred skills
   - Experience level
   - Key responsibilities
   - ATS keywords

2. **Resume Optimization**: Claude modifies the LaTeX resume to:
   - Emphasize relevant experience
   - Highlight matching skills
   - Reorder bullet points for relevance
   - Include ATS-optimized keywords
   - Quantify achievements where possible

3. **LaTeX Compilation**: The system compiles the tailored LaTeX to PDF

4. **Fallback Mechanism**: If compilation fails, the system uses the base resume

### Cover Letter Generation

Claude generates personalized cover letters that:
- Reference specific job requirements
- Highlight relevant achievements
- Show cultural fit
- Include clear call-to-action

## Troubleshooting

### LaTeX Compilation Errors

If you encounter LaTeX errors:

1. **Check LaTeX installation**:
   ```bash
   pdflatex --version
   ```

2. **Install missing packages**:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install texlive-latex-extra texlive-fonts-extra
   ```

3. **Check logs**: Look at `storage/generated/*.log` files

### MongoDB Connection Issues

1. **Verify MongoDB is running**:
   ```bash
   # Check if MongoDB is running
   sudo systemctl status mongod  # Linux
   brew services list            # macOS
   ```

2. **Check connection string** in `.env` file

### API Key Issues

1. Verify your Anthropic API key is valid
2. Check you have sufficient credits
3. Ensure the key has correct permissions

## Production Deployment

For production deployment:

1. **Set environment to production**:
   ```env
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

2. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

3. **Set up async processing** with Celery for AI jobs:
   ```bash
   pip install celery redis
   ```

4. **Use environment secrets** for API keys and database credentials

5. **Set up HTTPS** for secure communication

## Future Enhancements

- [ ] Async job processing with Celery
- [ ] Multiple resume templates
- [ ] Email integration for application tracking
- [ ] Interview preparation assistant
- [ ] Application analytics dashboard
- [ ] Chrome extension for one-click applications
- [ ] LinkedIn integration
- [ ] Cover letter templates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Credits

Built with:
- [Flask](https://flask.palletsprojects.com/)
- [Anthropic Claude](https://www.anthropic.com/)
- [MongoDB](https://www.mongodb.com/)
- [LaTeX](https://www.latex-project.org/)

```

### requirements.txt

```text
# Core Framework
Flask==3.0.0
Werkzeug==3.0.1

# Database
pymongo==4.6.1

# Authentication
PyJWT==2.8.0

# AI Services
anthropic==0.40.0

# Environment Variables
python-dotenv==1.0.0

# LaTeX Processing (Note: pdflatex must be installed on system)
# Use: sudo apt-get install texlive-full (Linux)
# Or: brew install --cask mactex (macOS)

# Optional: For async processing (recommended for production)
# celery==5.3.4
# redis==5.0.1

# Development
# flask-cors==4.0.0  # If you need CORS

```

### routes/application_routes.py

```python
from flask import Blueprint
from middlewares.auth_middleware import require_auth
from controllers import application_controller

application_routes = Blueprint("application_routes", __name__)


@application_routes.route("/applications", methods=["GET"])
@require_auth
def list_applications():
    return application_controller.list_applications()


@application_routes.route("/applications", methods=["POST"])
@require_auth
def create_application():
    return application_controller.create_application()


@application_routes.route("/applications/<app_id>", methods=["GET"])
@require_auth
def application_detail(app_id):
    return application_controller.application_detail(app_id)


@application_routes.route("/applications/<app_id>/regenerate", methods=["POST"])
@require_auth
def regenerate_resume(app_id):
    return application_controller.regenerate_resume(app_id)


@application_routes.route("/applications/<app_id>/cover-letter", methods=["POST"])
@require_auth
def generate_cover_letter(app_id):
    return application_controller.generate_cover_letter(app_id)


@application_routes.route("/assets/<asset_id>/download", methods=["GET"])
@require_auth
def download_asset(asset_id):
    return application_controller.download_asset(asset_id)


@application_routes.route("/assets/<asset_id>", methods=["DELETE"])
@require_auth
def delete_asset(asset_id):
    return application_controller.delete_asset(asset_id)


@application_routes.route("/applications/<app_id>", methods=["DELETE"])
@require_auth
def delete_application(app_id):
    return application_controller.delete_application(app_id)

```

### routes/auth_routes.py

```python
from flask import Blueprint
from controllers.auth_controller import signup, login, logout
from middlewares.auth_middleware import guest_only

auth_routes = Blueprint("auth", __name__)

auth_routes.route("/login", methods=["GET", "POST"])(guest_only(login))
auth_routes.route("/signup", methods=["GET", "POST"])(guest_only(signup))
auth_routes.route("/logout")(logout)

```

### routes/dashboard_routes.py

```python
from flask import Blueprint, render_template
from middlewares.auth_middleware import require_auth

dashboard_routes = Blueprint("dashboard", __name__)


@dashboard_routes.route("/dashboard")
@require_auth
def dashboard():
    return render_template("dashboard/index.html")

```

### routes/profile_routes.py

```python
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

```

### routes/section_preferences_routes.py

```python
"""
Routes for managing resume section preferences
"""

from flask import Blueprint
from middlewares.auth_middleware import require_auth
from controllers.section_preferences_controller import (
    view_section_preferences,
    load_resume_sections,
    save_section_preferences,
    get_section_preferences,
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

```

### seed_database.py

```python
"""
Database seeding script to initialize base resumes and collections
Run this once to set up the initial data
"""

from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "applytailored")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def seed_base_resume():
    """Create a default base resume entry"""

    # Check if default base resume already exists
    existing = db.base_resumes.find_one({"user_id": "default"})

    if existing:
        print("Default base resume already exists")
        return

    base_resume = {
        "_id": str(ObjectId()),
        "user_id": "default",
        "title": "Default Base Resume",
        "description": "A professional resume template that can be used as a starting point",
        "latex_template_path": "base_resume_template.tex",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    db.base_resumes.insert_one(base_resume)
    print(f"✓ Created default base resume with ID: {base_resume['_id']}")


def create_indexes():
    """Create database indexes for better query performance"""

    # Users collection indexes
    db.users.create_index("email", unique=True)
    print("✓ Created index on users.email")

    # Applications collection indexes
    db.applications.create_index([("user_id", 1), ("created_at", -1)])
    db.applications.create_index("status")
    print("✓ Created indexes on applications collection")

    # Base resumes collection indexes
    db.base_resumes.create_index([("user_id", 1)])
    print("✓ Created index on base_resumes.user_id")

    # Generated assets collection indexes
    db.generated_assets.create_index([("job_application_id", 1)])
    db.generated_assets.create_index([("user_id", 1), ("created_at", -1)])
    db.generated_assets.create_index("type")
    print("✓ Created indexes on generated_assets collection")


def verify_storage_directories():
    """Ensure all necessary storage directories exist"""

    directories = ["storage", "storage/base_resumes", "storage/generated"]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Verified directory: {directory}")


def main():
    print("Starting database seeding...\n")

    try:
        # Verify storage directories
        print("1. Checking storage directories...")
        verify_storage_directories()
        print()

        # Create indexes
        print("2. Creating database indexes...")
        create_indexes()
        print()

        # Seed base resume
        print("3. Seeding default base resume...")
        seed_base_resume()
        print()

        print("✅ Database seeding completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    main()

```

### services/claude_ai_service_backup.py

```python
import os
import anthropic
from typing import Optional, Dict, Any
import json


class ClaudeAIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"

    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job description to extract key information
        """
        prompt = f"""Analyze the following job description and extract structured information.
Return your response in JSON format with these fields:
- company_name: string
- position_title: string
- required_skills: list of strings
- preferred_skills: list of strings
- experience_level: string (entry/mid/senior)
- key_responsibilities: list of strings
- keywords: list of important keywords for ATS

Job Description:
{job_description}

Return only valid JSON, no markdown or additional text."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text

        # Try to parse JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = (
                    response_text.split("```json")[1].split("```")[0].strip()
                )
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "company_name": "Unknown",
                "position_title": "Unknown",
                "required_skills": [],
                "preferred_skills": [],
                "experience_level": "unknown",
                "key_responsibilities": [],
                "keywords": [],
            }

    def tailor_resume(
        self,
        base_resume_latex: str,
        job_description: str,
        job_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Tailor a LaTeX resume to match a job description
        """
        analysis_context = ""
        if job_analysis:
            analysis_context = f"""
Job Analysis:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
- Required Skills: {', '.join(job_analysis.get('required_skills', []))}
- Key Responsibilities: {', '.join(job_analysis.get('key_responsibilities', []))}
- Keywords for ATS: {', '.join(job_analysis.get('keywords', []))}
"""

        prompt = f"""You are an expert resume writer. Your task is to tailor the following LaTeX resume to match the job description below.

IMPORTANT GUIDELINES:
1. Preserve ALL LaTeX formatting, commands, and structure
2. Keep the same document class and packages
3. Maintain professional tone and formatting
4. Optimize for ATS (Applicant Tracking Systems) by including relevant keywords naturally
5. Emphasize experiences and skills that match the job requirements
6. Reorder or rephrase bullet points to highlight relevant achievements
7. Quantify achievements where possible
8. Ensure all LaTeX syntax is valid and compilable
9. Do NOT add fictional experience or skills - only optimize what exists
10. Return ONLY the modified LaTeX code, no explanations or markdown

{analysis_context}

Job Description:
{job_description}

Base Resume (LaTeX):
{base_resume_latex}

Return the tailored LaTeX resume:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        tailored_latex = message.content[0].text

        # Clean up response - remove markdown code blocks if present
        if "```latex" in tailored_latex:
            tailored_latex = tailored_latex.split("```latex")[1].split("```")[0].strip()
        elif "```tex" in tailored_latex:
            tailored_latex = tailored_latex.split("```tex")[1].split("```")[0].strip()
        elif "```" in tailored_latex:
            # Generic code block
            tailored_latex = tailored_latex.split("```")[1].split("```")[0].strip()

        return tailored_latex

    def generate_cover_letter(
        self,
        resume_text: str,
        job_description: str,
        job_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a tailored cover letter
        """
        analysis_context = ""
        if job_analysis:
            analysis_context = f"""
Job Details:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
"""

        prompt = f"""Write a professional cover letter for the following job application.

{analysis_context}

Job Description:
{job_description}

Candidate's Resume/Background:
{resume_text}

Guidelines:
1. Keep it concise (3-4 paragraphs)
2. Show enthusiasm and cultural fit
3. Highlight 2-3 key achievements relevant to the role
4. Demonstrate understanding of the company/role
5. Include a clear call to action
6. Use professional but warm tone
7. Avoid generic phrases

Return only the cover letter text:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text

```

### services/claude_ai_service.py

```python
"""
Enhanced Claude AI Service with selective section regeneration
"""

import os
import anthropic
from typing import Optional, Dict, Any
import json


class ClaudeAIService:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"

    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze job description to extract key information
        """
        prompt = f"""Analyze the following job description and extract structured information.
Return your response in JSON format with these fields:
- company_name: string
- position_title: string
- required_skills: list of strings
- preferred_skills: list of strings
- experience_level: string (entry/mid/senior)
- key_responsibilities: list of strings
- keywords: list of important keywords for ATS

Job Description:
{job_description}

Return only valid JSON, no markdown or additional text."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text

        # Try to parse JSON from response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = (
                    response_text.split("```json")[1].split("```")[0].strip()
                )
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "company_name": "Unknown",
                "position_title": "Unknown",
                "required_skills": [],
                "preferred_skills": [],
                "experience_level": "unknown",
                "key_responsibilities": [],
                "keywords": [],
            }

    def regenerate_section(
        self,
        section_content: str,
        section_type: str,
        job_description: str,
        job_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Regenerate a specific section of the resume based on job description

        Args:
            section_content: The original LaTeX content of the section
            section_type: Type of section (experience, education, skills, etc.)
            job_description: Target job description
            job_analysis: Analyzed job information
            context: Additional context about the section

        Returns:
            Regenerated LaTeX content for the section
        """
        context = context or {}

        # Build context information
        analysis_text = f"""
Job Analysis:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
- Required Skills: {', '.join(job_analysis.get('required_skills', [])[:10])}
- Key Responsibilities: {', '.join(job_analysis.get('key_responsibilities', [])[:5])}
- ATS Keywords: {', '.join(job_analysis.get('keywords', [])[:15])}
"""

        # Section-specific instructions
        section_instructions = {
            "experience": """
For the EXPERIENCE section:
- Reorder bullet points to highlight most relevant achievements first
- Emphasize projects and responsibilities that match the job requirements
- Add quantifiable metrics where they exist
- Include ATS keywords naturally in descriptions
- Focus on transferable skills and relevant technologies
- Keep the same job titles and companies (don't fabricate)
""",
            "skills": """
For the SKILLS section:
- Prioritize skills mentioned in the job description
- Group related skills together
- Ensure all required skills are visible if they exist
- Include ATS keywords for technologies mentioned
- Keep the structure clear and scannable
""",
            "education": """
For the EDUCATION section:
- Highlight relevant coursework if it matches job requirements
- Emphasize GPA if strong and relevant
- Include relevant academic projects
- Keep the basic facts unchanged
""",
            "projects": """
For the PROJECTS section:
- Prioritize projects using technologies mentioned in job description
- Emphasize outcomes and impact
- Include relevant technical details
- Highlight teamwork or leadership if relevant
""",
            "summary": """
For the SUMMARY/PROFILE section:
- Tailor the summary to highlight experience relevant to this role
- Include keywords from the job description
- Emphasize the most relevant qualifications
- Keep it concise (2-4 lines)
""",
        }

        instructions = section_instructions.get(
            section_type,
            """
Optimize this section to be more relevant to the job description.
Emphasize relevant content and include appropriate ATS keywords.
""",
        )

        prompt = f"""You are an expert resume writer. Your task is to regenerate ONLY the {section_type.upper()} section of a resume to better match the job description below.

{analysis_text}

Job Description:
{job_description}

CRITICAL GUIDELINES:
1. Preserve ALL LaTeX formatting, commands, and structure EXACTLY
2. Keep the same LaTeX commands (\section, \resumeSubheading, \resumeItem, etc.)
3. Do NOT change dates, company names, job titles, or factual information
4. ONLY modify bullet points and descriptions to emphasize relevant experience
5. Include ATS keywords naturally where appropriate
6. Maintain professional tone and formatting
7. Ensure all LaTeX syntax is valid and compilable
8. Return ONLY the LaTeX code for this section, starting with \section{{{context.get('section_title', section_type)}}}

{instructions}

Original {section_type.upper()} Section (LaTeX):
{section_content}

Return the optimized {section_type.upper()} section in valid LaTeX:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        regenerated_content = message.content[0].text

        # Clean up response - remove markdown code blocks if present
        if "```latex" in regenerated_content:
            regenerated_content = (
                regenerated_content.split("```latex")[1].split("```")[0].strip()
            )
        elif "```tex" in regenerated_content:
            regenerated_content = (
                regenerated_content.split("```tex")[1].split("```")[0].strip()
            )
        elif "```" in regenerated_content:
            regenerated_content = (
                regenerated_content.split("```")[1].split("```")[0].strip()
            )

        return regenerated_content

    def tailor_resume(
        self,
        base_resume_latex: str,
        job_description: str,
        job_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Tailor a LaTeX resume to match a job description
        """
        analysis_context = ""
        if job_analysis:
            analysis_context = f"""
Job Analysis:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
- Required Skills: {', '.join(job_analysis.get('required_skills', []))}
- Key Responsibilities: {', '.join(job_analysis.get('key_responsibilities', []))}
- Keywords for ATS: {', '.join(job_analysis.get('keywords', []))}
"""

        prompt = f"""You are an expert resume writer. Your task is to tailor the following LaTeX resume to match the job description below.

IMPORTANT GUIDELINES:
1. Preserve ALL LaTeX formatting, commands, and structure
2. Keep the same document class and packages
3. Maintain professional tone and formatting
4. Optimize for ATS (Applicant Tracking Systems) by including relevant keywords naturally
5. Emphasize experiences and skills that match the job requirements
6. Reorder or rephrase bullet points to highlight relevant achievements
7. Quantify achievements where possible
8. Ensure all LaTeX syntax is valid and compilable
9. Do NOT add fictional experience or skills - only optimize what exists
10. Return ONLY the modified LaTeX code, no explanations or markdown

{analysis_context}

Job Description:
{job_description}

Base Resume (LaTeX):
{base_resume_latex}

Return the tailored LaTeX resume:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )

        tailored_latex = message.content[0].text

        # Clean up response - remove markdown code blocks if present
        if "```latex" in tailored_latex:
            tailored_latex = tailored_latex.split("```latex")[1].split("```")[0].strip()
        elif "```tex" in tailored_latex:
            tailored_latex = tailored_latex.split("```tex")[1].split("```")[0].strip()
        elif "```" in tailored_latex:
            # Generic code block
            tailored_latex = tailored_latex.split("```")[1].split("```")[0].strip()

        return tailored_latex

    def generate_cover_letter(
        self,
        resume_text: str,
        job_description: str,
        job_analysis: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a tailored cover letter
        """
        analysis_context = ""
        if job_analysis:
            analysis_context = f"""
Job Details:
- Company: {job_analysis.get('company_name', 'Unknown')}
- Position: {job_analysis.get('position_title', 'Unknown')}
"""

        prompt = f"""Write a professional cover letter for the following job application.

{analysis_context}

Job Description:
{job_description}

Candidate's Resume/Background:
{resume_text}

Guidelines:
1. Keep it concise (3-4 paragraphs)
2. Show enthusiasm and cultural fit
3. Highlight 2-3 key achievements relevant to the role
4. Demonstrate understanding of the company/role
5. Include a clear call to action
6. Use professional but warm tone
7. Avoid generic phrases

Return only the cover letter text:"""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        return message.content[0].text

```

### services/latex_parser_service.py

```python
"""
LaTeX Parser Service - Extract structured content from LaTeX resume templates
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ResumeSection:
    """Represents a section in the resume"""

    section_type: (
        str  # 'heading', 'experience', 'education', 'skills', 'projects', etc.
    )
    title: str  # Section title
    content: str  # Raw LaTeX content
    start_pos: int  # Position in original document
    end_pos: int  # End position
    subsections: List["ResumeSubsection"] = None

    def __post_init__(self):
        if self.subsections is None:
            self.subsections = []


@dataclass
class ResumeSubsection:
    """Represents a subsection (like individual job, education entry, etc.)"""

    title: str  # e.g., "Senior Software Engineer at Tech Company"
    content: str  # Raw LaTeX content
    lines: List[str]  # Individual bullet points/lines
    start_pos: int
    end_pos: int


class LatexParserService:
    """Parse LaTeX resumes to extract structured content"""

    # Common section headers to look for
    SECTION_PATTERNS = {
        "experience": r"\\section\{.*?(?:experience|employment|work history).*?\}",
        "education": r"\\section\{.*?education.*?\}",
        "skills": r"\\section\{.*?(?:skills|technical skills|competencies).*?\}",
        "projects": r"\\section\{.*?projects.*?\}",
        "summary": r"\\section\{.*?(?:summary|profile|objective).*?\}",
        "certifications": r"\\section\{.*?(?:certifications?|licenses?).*?\}",
        "publications": r"\\section\{.*?publications?.*?\}",
    }

    def parse_resume(self, latex_content: str) -> Dict[str, Any]:
        """
        Parse LaTeX resume into structured sections

        Returns:
            {
                'header': {...},
                'sections': [ResumeSection, ...],
                'raw_content': str
            }
        """
        result = {
            "header": self._extract_header(latex_content),
            "sections": [],
            "raw_content": latex_content,
        }

        # Find all sections
        sections = self._find_sections(latex_content)

        for section_info in sections:
            section = self._parse_section(
                latex_content,
                section_info["type"],
                section_info["title"],
                section_info["start"],
                section_info["end"],
            )
            result["sections"].append(section)

        return result

    def _extract_header(self, latex_content: str) -> Dict[str, str]:
        """Extract resume header information (name, contact, etc.)"""
        header = {"content": "", "name": "", "email": "", "phone": "", "location": ""}

        # Find content before first \section
        section_match = re.search(r"\\section\{", latex_content, re.IGNORECASE)
        if section_match:
            header_content = latex_content[: section_match.start()]
        else:
            # If no sections, take content after \begin{document}
            begin_doc = re.search(r"\\begin\{document\}", latex_content)
            if begin_doc:
                header_content = latex_content[begin_doc.end() :]
            else:
                header_content = latex_content[:500]  # First 500 chars as fallback

        header["content"] = header_content.strip()

        # Try to extract name (usually in \textbf{\Large ...} or similar)
        name_patterns = [
            r"\\textbf\{\\(?:Large|LARGE|huge|Huge)\s+([^}]+)\}",
            r"\\(?:Large|LARGE|huge|Huge)\s+\\textbf\{([^}]+)\}",
            r"\\(?:Large|LARGE)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, header_content)
            if match:
                header["name"] = match.group(1).strip()
                break

        # Extract email
        email_match = re.search(
            r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", header_content
        )
        if email_match:
            header["email"] = email_match.group(1)

        # Extract phone
        phone_match = re.search(
            r"(\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})", header_content
        )
        if phone_match:
            header["phone"] = phone_match.group(1)

        return header

    def _find_sections(self, latex_content: str) -> List[Dict[str, Any]]:
        """Find all section boundaries in the document"""
        sections = []

        # Find all \section{...} commands
        section_matches = list(
            re.finditer(r"\\section\{([^}]+)\}", latex_content, re.IGNORECASE)
        )

        for i, match in enumerate(section_matches):
            section_title = match.group(1)
            start_pos = match.start()

            # End is either the next section or end of document
            if i + 1 < len(section_matches):
                end_pos = section_matches[i + 1].start()
            else:
                # Find \end{document} or use end of content
                end_doc = re.search(r"\\end\{document\}", latex_content[start_pos:])
                if end_doc:
                    end_pos = start_pos + end_doc.start()
                else:
                    end_pos = len(latex_content)

            # Determine section type
            section_type = self._classify_section(section_title)

            sections.append(
                {
                    "type": section_type,
                    "title": section_title,
                    "start": start_pos,
                    "end": end_pos,
                }
            )

        return sections

    def _classify_section(self, section_title: str) -> str:
        """Classify section based on its title"""
        title_lower = section_title.lower()

        for section_type, pattern in self.SECTION_PATTERNS.items():
            if re.search(pattern, f"\\section{{{section_title}}}", re.IGNORECASE):
                return section_type

        # Default classification based on keywords
        if any(word in title_lower for word in ["experience", "work", "employment"]):
            return "experience"
        elif any(word in title_lower for word in ["education", "academic"]):
            return "education"
        elif any(word in title_lower for word in ["skill", "technical", "competenc"]):
            return "skills"
        elif "project" in title_lower:
            return "projects"
        elif any(word in title_lower for word in ["summary", "profile", "objective"]):
            return "summary"
        else:
            return "other"

    def _parse_section(
        self,
        full_content: str,
        section_type: str,
        section_title: str,
        start_pos: int,
        end_pos: int,
    ) -> ResumeSection:
        """Parse a section into structured content"""
        section_content = full_content[start_pos:end_pos]

        section = ResumeSection(
            section_type=section_type,
            title=section_title,
            content=section_content,
            start_pos=start_pos,
            end_pos=end_pos,
        )

        # Parse subsections (like individual jobs, education entries)
        if section_type in ["experience", "education", "projects"]:
            section.subsections = self._parse_subsections(section_content, start_pos)
        elif section_type == "skills":
            section.subsections = self._parse_skills(section_content, start_pos)

        return section

    def _parse_subsections(
        self, section_content: str, base_offset: int
    ) -> List[ResumeSubsection]:
        """Parse subsections like individual job entries"""
        subsections = []

        # Look for \resumeSubheading or similar commands
        patterns = [
            r"\\resumeSubheading\{([^}]+)\}\{([^}]+)\}\{([^}]+)\}\{([^}]+)\}",
            r"\\resumeSubSubheading\{([^}]+)\}\{([^}]+)\}",
            r"\\item\s+\\textbf\{([^}]+)\}",
        ]

        for pattern in patterns:
            matches = list(re.finditer(pattern, section_content))

            for i, match in enumerate(matches):
                # Extract title (usually first group)
                title = match.group(1)
                start = match.start()

                # Find the end of this subsection
                if i + 1 < len(matches):
                    end = matches[i + 1].start()
                else:
                    # Look for next major command or end of section
                    next_section = re.search(
                        r"\\(?:resumeSubHeadingListEnd|end\{itemize\})",
                        section_content[start:],
                    )
                    if next_section:
                        end = start + next_section.start()
                    else:
                        end = len(section_content)

                subsection_content = section_content[start:end]

                # Extract bullet points
                lines = self._extract_bullet_points(subsection_content)

                subsections.append(
                    ResumeSubsection(
                        title=title,
                        content=subsection_content,
                        lines=lines,
                        start_pos=base_offset + start,
                        end_pos=base_offset + end,
                    )
                )

            if subsections:  # If we found matches with this pattern, stop
                break

        return subsections

    def _parse_skills(
        self, section_content: str, base_offset: int
    ) -> List[ResumeSubsection]:
        """Parse skills section"""
        subsections = []

        # Look for \resumeSubItem or individual skill items
        skill_items = re.finditer(
            r"\\resumeSubItem\{([^}]+)\}\{([^}]+)\}", section_content
        )

        for i, match in enumerate(skill_items):
            title = match.group(1)
            content = match.group(2)

            subsections.append(
                ResumeSubsection(
                    title=title,
                    content=match.group(0),
                    lines=[content],
                    start_pos=base_offset + match.start(),
                    end_pos=base_offset + match.end(),
                )
            )

        return subsections

    def _extract_bullet_points(self, content: str) -> List[str]:
        """Extract individual bullet points from content"""
        lines = []

        # Look for \resumeItem{...}
        items = re.finditer(r"\\resumeItem\{([^}]+)\}", content)
        for item in items:
            lines.append(item.group(1))

        # Also look for plain \item commands
        if not lines:
            items = re.finditer(r"\\item\s+([^\n\\]+)", content)
            for item in items:
                lines.append(item.group(1).strip())

        return lines

    def rebuild_latex(
        self,
        original_content: str,
        parsed_structure: Dict[str, Any],
        selected_sections: Dict[str, bool],
        regenerated_sections: Dict[str, str],
    ) -> str:
        """
        Rebuild LaTeX with regenerated sections

        Args:
            original_content: Original LaTeX
            parsed_structure: Parsed structure from parse_resume()
            selected_sections: Dict of section_id -> True/False
            regenerated_sections: Dict of section_id -> new LaTeX content

        Returns:
            Updated LaTeX content
        """
        result = original_content

        # Replace sections from back to front to maintain positions
        sections_to_replace = []

        for section in parsed_structure["sections"]:
            section_id = f"{section.section_type}_{section.start_pos}"

            if section_id in regenerated_sections:
                sections_to_replace.append(
                    {
                        "start": section.start_pos,
                        "end": section.end_pos,
                        "new_content": regenerated_sections[section_id],
                    }
                )

        # Sort by start position (descending) to replace from back to front
        sections_to_replace.sort(key=lambda x: x["start"], reverse=True)

        for replacement in sections_to_replace:
            result = (
                result[: replacement["start"]]
                + replacement["new_content"]
                + result[replacement["end"] :]
            )

        return result

    def get_section_preview(self, section: ResumeSection, max_length: int = 200) -> str:
        """Get a readable preview of a section"""
        # Remove LaTeX commands for preview
        preview = re.sub(r"\\[a-zA-Z]+\*?\{([^}]*)\}", r"\1", section.content)
        preview = re.sub(r"\\[a-zA-Z]+\*?", "", preview)
        preview = preview.strip()

        if len(preview) > max_length:
            preview = preview[:max_length] + "..."

        return preview

```

### services/latex_service.py

```python
import os
import subprocess
from pathlib import Path
from typing import Tuple, Optional


class LatexService:
    def __init__(self, storage_path: str = "storage"):
        self.storage_path = Path(storage_path)
        self.generated_path = self.storage_path / "generated"
        self.base_resumes_path = self.storage_path / "base_resumes"

        # Ensure directories exist
        self.generated_path.mkdir(parents=True, exist_ok=True)
        self.base_resumes_path.mkdir(parents=True, exist_ok=True)

    def compile_latex(
        self, tex_content: str, output_filename: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Compile LaTeX content to PDF

        Returns:
            Tuple of (success: bool, pdf_path: str|None, error_message: str|None)
        """
        # Create unique temporary file path
        tex_path = self.generated_path / f"{output_filename}.tex"
        pdf_path = self.generated_path / f"{output_filename}.pdf"

        try:
            # Write LaTeX content to file
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_content)

            # Compile with pdflatex
            # Run twice to resolve references
            for _ in range(2):
                result = subprocess.run(
                    [
                        "pdflatex",
                        "-interaction=nonstopmode",
                        "-output-directory",
                        str(self.generated_path),
                        str(tex_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

            # Check if PDF was generated
            if pdf_path.exists():
                # Clean up auxiliary files
                self._cleanup_aux_files(output_filename)
                return True, str(pdf_path), None
            else:
                error_msg = result.stderr if result.stderr else "PDF generation failed"
                return False, None, error_msg

        except subprocess.TimeoutExpired:
            return False, None, "LaTeX compilation timeout"
        except Exception as e:
            return False, None, f"Compilation error: {str(e)}"

    def _cleanup_aux_files(self, base_filename: str):
        """Remove auxiliary LaTeX files"""
        aux_extensions = [".aux", ".log", ".out", ".toc"]
        for ext in aux_extensions:
            aux_file = self.generated_path / f"{base_filename}{ext}"
            if aux_file.exists():
                try:
                    aux_file.unlink()
                except:
                    pass

    def read_base_resume(self, latex_template_path: str) -> Optional[str]:
        """Read base resume template from storage"""
        try:
            full_path = self.base_resumes_path / latex_template_path
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error reading base resume: {e}")
            return None

    def save_base_resume(self, content: str, filename: str) -> str:
        """Save a base resume template"""
        file_path = self.base_resumes_path / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return filename

    def extract_text_from_latex(self, latex_content: str) -> str:
        """
        Extract plain text from LaTeX (rough approximation)
        For better results, compile to PDF and extract from PDF
        """
        import re

        # Remove comments
        text = re.sub(r"%.*", "", latex_content)

        # Remove common LaTeX commands but keep their content
        text = re.sub(r"\\[a-zA-Z]+\*?\{([^}]*)\}", r"\1", text)
        text = re.sub(r"\\[a-zA-Z]+\*?", "", text)

        # Remove special characters
        text = text.replace("\\\\", "\n")
        text = text.replace("~", " ")
        text = text.replace("&", " ")

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n\s*\n", "\n\n", text)

        return text.strip()

```

### storage/base_resumes/a31e559f-8d9c-4389-a562-2e0b7314bf0e.tex

```
\documentclass[letterpaper,10pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{multicol}
\input{glyphtounicode}

\usepackage[default]{sourcesanspro}
\usepackage[T1]{fontenc}

\pagestyle{fancy}
\fancyhf{} 
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}


\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-4pt}\centering
}{}{0em}{}[\color{black}\titlerule\vspace{-5pt}]


\pdfgentounicode=1

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}



\begin{center}
    {\LARGE John Zlad Doe} \\ \vspace{2pt}
    \begin{multicols}{2}
    \begin{flushleft}
    \href{{your github page link}}{my github}\\
    \href{{your linkedin page link}}{my linkedin}
    \end{flushleft}
    
    \begin{flushright}
    \href{{your personal websit link}}{my personal site}\\
    \href{mailto:{your email adress}}{my email}
    \end{flushright}
    \end{multicols}
\end{center}


%-----------EDUCATION-----------
\vspace{-2pt}
\section{Education}
  \resumeSubHeadingListStart
      \resumeSubheading
      {University of Molvanîa -- UM}{Aug. 2019 -- Present}
      {PhD. Student in Technology}{Molvanîa, Mv}

  \resumeSubHeadingListEnd


%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Ph.D. Researcher}{Sep. 2019 -- Present}
      {Laser beams shooting research}{Molvanîa, Mv}
      \resumeItemListStart
        \resumeItem{Laser beams}
        \resumeItem{Laser cooling techniques}
        \resumeItem{Off blast!}
    \resumeItemListEnd

  \resumeSubHeadingListEnd

%-----------PUBLICATIONS-----------
\section{Publications}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
    \textbf{New techniques for Elektronik supersonik laser shootings. WORKSHOP ON INDUSTRY APPLICATION - Molvanîan Academy o Science, 2020 . p. 225-231.}{\\J. Zlad Doe}\\
        \textbf{Space Rockets . WORKSHOP ON INDUSTRY APPLICATION - Molvanîan Academy o Science, 2021 . p. 25-31.}{\\J. Zlad Doe, Darth Vapor}\\
\ 
}}
 \end{itemize}

%-----------PROGRAMMING SKILLS-----------
\section{Technical Skills, Language Skills, and Interests}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
    \textbf{OS}{: Windows} \\
     \textbf{Programming Languages}{: C/C++} \\
     \textbf{Libraries}{: OpenCV}\\
     \textbf{Version Control}{: Git} \\
     \textbf{Writing}{: \LaTeX, Office} \\
     \textbf{Languages}{: Molvanîan (native), English (fluent)} \\
     \textbf{Interests}{: Lasers and Music}
     
    }}
 \end{itemize}

%-----------CERTIFICATIONS-----------
\section{Extracurricular}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Specialization}{:\href{certification site}{ Course} } 
    }}
    
 \end{itemize}

\end{document}

```

### storage/base_resumes/base_resume_template.tex

```
%-------------------------
% Resume in LaTeX
% Author: Your Name
% License: MIT
%------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

%-------------------------
% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-1pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-5pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand{\labelitemii}{$\circ$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=*]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-------------------------------------------
%%%%%%  CV STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%

\begin{document}

%----------HEADING-----------------
\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
  \textbf{\href{http://yourwebsite.com/}{\Large John Doe}} & Email: \href{mailto:john.doe@email.com}{john.doe@email.com}\\
  \href{http://yourwebsite.com/}{http://www.yourwebsite.com} & Mobile: +1-123-456-7890 \\
\end{tabular*}

%-----------SUMMARY-----------------
\section{Professional Summary}
  Results-driven software engineer with 5+ years of experience in full-stack development, specializing in Python, JavaScript, and cloud technologies. Proven track record of delivering scalable applications and leading cross-functional teams.

%-----------EXPERIENCE-----------------
\section{Experience}
  \resumeSubHeadingListStart

    \resumeSubheading
      {Senior Software Engineer}{Jan 2021 -- Present}
      {Tech Company Inc.}{San Francisco, CA}
      \resumeItemListStart
        \resumeItem{Led development of microservices architecture serving 1M+ users, improving system reliability by 40\%}
        \resumeItem{Architected and implemented RESTful APIs using Python/Flask, reducing response time by 35\%}
        \resumeItem{Mentored team of 5 junior developers, establishing code review practices and best practices}
        \resumeItem{Implemented CI/CD pipelines using Jenkins and Docker, reducing deployment time from hours to minutes}
        \resumeItem{Collaborated with product managers and designers to deliver 15+ features ahead of schedule}
      \resumeItemListEnd

    \resumeSubheading
      {Software Engineer}{Jun 2019 -- Dec 2020}
      {Startup XYZ}{Remote}
      \resumeItemListStart
        \resumeItem{Developed full-stack web applications using React, Node.js, and MongoDB}
        \resumeItem{Built and deployed machine learning models for recommendation system, increasing user engagement by 25\%}
        \resumeItem{Optimized database queries and indexing strategies, improving query performance by 60\%}
        \resumeItem{Participated in agile development process with bi-weekly sprints and daily standups}
      \resumeItemListEnd

    \resumeSubheading
      {Junior Developer}{May 2018 -- May 2019}
      {Software Solutions Ltd.}{New York, NY}
      \resumeItemListStart
        \resumeItem{Developed responsive web applications using HTML, CSS, JavaScript, and Bootstrap}
        \resumeItem{Contributed to open-source projects and maintained company's technical documentation}
        \resumeItem{Assisted in debugging and resolving production issues, reducing critical bugs by 30\%}
      \resumeItemListEnd

  \resumeSubHeadingListEnd

%-----------EDUCATION-----------------
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {University of California, Berkeley}{Berkeley, CA}
      {Bachelor of Science in Computer Science; GPA: 3.8}{Sep 2014 -- May 2018}
  \resumeSubHeadingListEnd

%-----------SKILLS-----------------
\section{Technical Skills}
  \resumeSubHeadingListStart
    \resumeSubItem{Languages: Python, JavaScript, TypeScript, Java, SQL, HTML/CSS}
    \resumeSubItem{Frameworks: React, Node.js, Flask, Django, Express.js, Vue.js}
    \resumeSubItem{Tools \& Technologies: Git, Docker, Kubernetes, AWS, MongoDB, PostgreSQL, Redis}
    \resumeSubItem{Methodologies: Agile/Scrum, TDD, CI/CD, Microservices Architecture}
  \resumeSubHeadingListEnd

%-----------PROJECTS-----------------
\section{Notable Projects}
  \resumeSubHeadingListStart
    \resumeSubItem{E-commerce Platform}
      {Built a scalable e-commerce platform using MERN stack, handling 10K+ daily transactions}
    \resumeSubItem{AI Chatbot}
      {Developed an AI-powered customer support chatbot using NLP and machine learning, reducing support tickets by 40\%}
    \resumeSubItem{Open Source Contributions}
      {Active contributor to popular open-source projects with 500+ stars on GitHub}
  \resumeSubHeadingListEnd

%-----------CERTIFICATIONS-----------------
\section{Certifications}
  \resumeSubHeadingListStart
    \resumeSubItem{AWS Certified Solutions Architect -- Associate (2022)}
    \resumeSubItem{Certified Kubernetes Administrator (2021)}
  \resumeSubHeadingListEnd

%-------------------------------------------
\end{document}

```

### storage/generated/resume_697b6c657e75610931541e23_1769696371.pdf

(Skipped: binary or unreadable file)


### storage/generated/resume_697b6c657e75610931541e23_1769696371.tex

```
\documentclass[letterpaper,10pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\usepackage{multicol}
\input{glyphtounicode}

\usepackage[default]{sourcesanspro}
\usepackage[T1]{fontenc}

\pagestyle{fancy}
\fancyhf{} 
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}


\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-4pt}\centering
}{}{0em}{}[\color{black}\titlerule\vspace{-5pt}]


\pdfgentounicode=1

\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

\begin{document}



\begin{center}
    {\LARGE John Zlad Doe} \\ \vspace{2pt}
    \begin{multicols}{2}
    \begin{flushleft}
    \href{{your github page link}}{my github}\\
    \href{{your linkedin page link}}{my linkedin}
    \end{flushleft}
    
    \begin{flushright}
    \href{{your personal websit link}}{my personal site}\\
    \href{mailto:{your email adress}}{my email}
    \end{flushright}
    \end{multicols}
\end{center}


%-----------EDUCATION-----------
\vspace{-2pt}
\section{Education}
  \resumeSubHeadingListStart
      \resumeSubheading
      {University of Molvanîa -- UM}{Aug. 2019 -- Present}
      {PhD. Student in Technology}{Molvanîa, Mv}

  \resumeSubHeadingListEnd


%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Ph.D. Researcher}{Sep. 2019 -- Present}
      {Laser beams shooting research}{Molvanîa, Mv}
      \resumeItemListStart
        \resumeItem{Designed and developed distributed software systems for laser beam control using object-oriented programming principles, implementing scalable backend services that process real-time data from multiple laser sources}
        \resumeItem{Built highly available microservices architecture using Java to manage laser cooling techniques, applying systematic problem-solving approach to optimize system performance and reliability across distributed cloud infrastructure}
        \resumeItem{Enhanced RESTful APIs and server-side components for laser control systems, debugging and improving existing software architecture to support mission-critical applications with 99.9\% uptime}
        \resumeItem{Applied software engineering best practices to develop scalable distributed services, collaborating with cross-functional teams to deliver robust solutions using containerized deployments and cloud-native infrastructure}
    \resumeItemListEnd

  \resumeSubHeadingListEnd

%-----------PUBLICATIONS-----------\section{Publications}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
    \textbf{New techniques for Elektronik supersonik laser shootings. WORKSHOP ON INDUSTRY APPLICATION - Molvanîan Academy o Science, 2020 . p. 225-231.}{\\J. Zlad Doe}\\
        \textbf{Space Rockets . WORKSHOP ON INDUSTRY APPLICATION - Molvanîan Academy o Science, 2021 . p. 25-31.}{\\J. Zlad Doe, Darth Vapor}\\
\ 
}}
 \end{itemize}

%-----------PROGRAMMING SKILLS-----------
\section{Technical Skills, Language Skills, and Interests}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
    \textbf{OS}{: Windows} \\
     \textbf{Programming Languages}{: C/C++} \\
     \textbf{Libraries}{: OpenCV}\\
     \textbf{Version Control}{: Git} \\
     \textbf{Writing}{: \LaTeX, Office} \\
     \textbf{Languages}{: Molvanîan (native), English (fluent)} \\
     \textbf{Interests}{: Lasers and Music}
     
    }}
 \end{itemize}

%-----------CERTIFICATIONS-----------
\section{Extracurricular}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Specialization}{:\href{certification site}{ Course} } 
    }}
    
 \end{itemize}

\end{document}

```

### views/applications/detail.html

```html
{% extends "layouts/dashboard.html" %}

{% block content %}
<div class="max-w-5xl">

    <!-- Header with Back Button -->
    <div class="flex items-center justify-between mb-6">
        <a href="/applications" class="text-gray-600 hover:text-black">
            ← Back to Applications
        </a>

        <button onclick="confirmDeleteApplication()"
            class="px-4 py-2 bg-red-600 text-white rounded-md text-sm hover:bg-red-700">
            Delete Application
        </button>
    </div>

    <!-- Application Info Card -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-6">
        <div class="flex justify-between items-start mb-4">
            <div>
                <h1 class="text-2xl font-semibold mb-2">
                    {% if application.position_title %}
                    {{ application.position_title }}
                    {% else %}
                    Job Application
                    {% endif %}
                </h1>

                {% if application.company_name %}
                <p class="text-gray-600">{{ application.company_name }}</p>
                {% endif %}
            </div>

            <!-- Status Badge -->
            <span class="px-3 py-1 rounded-full text-sm font-medium
                {% if application.status == 'completed' %}bg-green-100 text-green-800
                {% elif application.status == 'processing' %}bg-blue-100 text-blue-800
                {% elif application.status == 'failed' %}bg-red-100 text-red-800
                {% else %}bg-gray-100 text-gray-800{% endif %}">
                {{ application.status|capitalize }}
            </span>
        </div>

        <!-- Job Description -->
        <div class="mt-6">
            <h3 class="text-sm font-semibold text-gray-700 mb-2">Job Description</h3>
            <div class="bg-gray-50 rounded-lg p-4 text-sm text-gray-700 max-h-64 overflow-y-auto">
                {{ application.job_description }}
            </div>
        </div>

        <!-- AI Analysis (if available) -->
        {% if application.ai_analysis %}
        <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            {% if application.ai_analysis.required_skills %}
            <div>
                <h4 class="text-sm font-semibold text-gray-700 mb-2">Required Skills</h4>
                <div class="flex flex-wrap gap-2">
                    {% for skill in application.ai_analysis.required_skills[:5] %}
                    <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">{{ skill }}</span>
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if application.ai_analysis.experience_level %}
            <div>
                <h4 class="text-sm font-semibold text-gray-700 mb-2">Experience Level</h4>
                <p class="text-sm text-gray-600 capitalize">{{ application.ai_analysis.experience_level }}</p>
            </div>
            {% endif %}
        </div>
        {% endif %}

        <!-- Action Buttons -->
        <div class="mt-6 flex gap-3">
            <button onclick="regenerateResume()"
                class="px-4 py-2 bg-black text-white rounded-md text-sm hover:bg-gray-800">
                Regenerate Resume
            </button>

            <button onclick="generateCoverLetter()"
                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50">
                Generate Cover Letter
            </button>
        </div>
    </div>

    <!-- Generated Assets -->
    <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <h2 class="text-lg font-semibold mb-4">Generated Documents</h2>

        {% if generated_assets %}
        <div class="space-y-3">
            {% for asset in generated_assets %}
            <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                <div>
                    <h3 class="font-medium text-gray-900">{{ asset.title }}</h3>
                    <p class="text-sm text-gray-500 mt-1">
                        {{ asset.type|capitalize }} • Version {{ asset.version }} •
                        {{ asset.created_at.strftime('%B %d, %Y at %I:%M %p') }}
                    </p>
                </div>

                <div class="flex gap-2">
                    {% if asset.pdf_path %}
                    <a href="/assets/{{ asset._id }}/download?type=pdf"
                        class="px-3 py-1 bg-black text-white rounded text-sm hover:bg-gray-800">
                        Download PDF
                    </a>
                    {% endif %}

                    {% if asset.tex_path %}
                    <a href="/assets/{{ asset._id }}/download?type=tex"
                        class="px-3 py-1 border border-gray-300 text-gray-700 rounded text-sm hover:bg-gray-50">
                        Download LaTeX
                    </a>
                    {% endif %}

                    {% if asset.type == 'cover_letter' %}
                    <button onclick="viewCoverLetter(this)" data-content="{{ asset.content_text|e }}"
                        class="px-3 py-1 border border-gray-300 text-gray-700 rounded text-sm hover:bg-gray-50">
                        View
                    </button>
                    {% endif %}

                    <button onclick="confirmDeleteAsset('{{ asset._id }}', '{{ asset.title }}')"
                        class="px-3 py-1 border border-red-300 text-red-700 rounded text-sm hover:bg-red-50">
                        Delete
                    </button>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="text-center py-8 text-gray-500">
            <p>No documents generated yet.</p>
            <p class="text-sm mt-2">Click "Regenerate Resume" to create your first tailored resume.</p>
        </div>
        {% endif %}
    </div>

</div>

<!-- Cover Letter Modal -->
<div id="coverLetterModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl w-full max-w-2xl p-6 max-h-[80vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-semibold">Cover Letter</h2>
            <button onclick="closeCoverLetterModal()" class="text-gray-500 hover:text-gray-700">
                ✕
            </button>
        </div>
        <div id="coverLetterContent" class="prose max-w-none whitespace-pre-wrap text-sm text-gray-700">
        </div>
    </div>
</div>

<!-- Loading Modal -->
<div id="loadingModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl p-8 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
        <p class="text-gray-700">Processing with AI...</p>
    </div>
</div>

<!-- Confirmation Modal -->
<div id="confirmModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl w-full max-w-md p-6">
        <h2 class="text-lg font-semibold mb-4">Confirm Delete</h2>
        <p id="confirmMessage" class="text-gray-700 mb-6"></p>
        <div class="flex justify-end gap-3">
            <button onclick="closeConfirmModal()"
                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50">
                Cancel
            </button>
            <button id="confirmButton" onclick="executeDelete()"
                class="px-4 py-2 bg-red-600 text-white rounded-md text-sm hover:bg-red-700">
                Delete
            </button>
        </div>
    </div>
</div>

<script>
    let deleteAction = null;

    function regenerateResume() {
        document.getElementById('loadingModal').classList.remove('hidden');

        fetch('/applications/{{ application._id }}/regenerate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loadingModal').classList.add('hidden');

                if (data.success) {
                    alert('Resume regenerated successfully!');
                    location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                document.getElementById('loadingModal').classList.add('hidden');
                alert('Error: ' + error.message);
            });
    }

    function generateCoverLetter() {
        document.getElementById('loadingModal').classList.remove('hidden');

        fetch('/applications/{{ application._id }}/cover-letter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loadingModal').classList.add('hidden');

                if (data.success) {
                    alert('Cover letter generated successfully!');
                    location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                document.getElementById('loadingModal').classList.add('hidden');
                alert('Error: ' + error.message);
            });
    }

    function viewCoverLetter(button) {
        const content = button.getAttribute('data-content');
        document.getElementById('coverLetterContent').textContent = content;
        document.getElementById('coverLetterModal').classList.remove('hidden');
    }

    function closeCoverLetterModal() {
        document.getElementById('coverLetterModal').classList.add('hidden');
    }

    function confirmDeleteApplication() {
        deleteAction = {
            type: 'application',
            id: '{{ application._id }}'
        };
        document.getElementById('confirmMessage').textContent =
            'Are you sure you want to delete this application? This will also delete all associated documents.';
        document.getElementById('confirmModal').classList.remove('hidden');
    }

    function confirmDeleteAsset(assetId, assetTitle) {
        deleteAction = {
            type: 'asset',
            id: assetId
        };
        document.getElementById('confirmMessage').textContent =
            `Are you sure you want to delete "${assetTitle}"?`;
        document.getElementById('confirmModal').classList.remove('hidden');
    }

    function closeConfirmModal() {
        document.getElementById('confirmModal').classList.add('hidden');
        deleteAction = null;
    }

    function executeDelete() {
        if (!deleteAction) return;

        if (deleteAction.type === 'application') {
            fetch('/applications/' + deleteAction.id, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = '/applications';
                    } else {
                        alert('Error deleting application');
                    }
                })
                .catch(error => {
                    alert('Error: ' + error.message);
                });
        } else if (deleteAction.type === 'asset') {
            fetch('/assets/' + deleteAction.id, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    closeConfirmModal();
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Error deleting document');
                    }
                })
                .catch(error => {
                    alert('Error: ' + error.message);
                });
        }
    }
</script>

{% endblock %}

```

### views/applications/index.html

```html
{% extends "layouts/dashboard.html" %}

{% block content %}
<div class="flex items-center justify-between mb-6">
    <h1 class="text-2xl font-semibold">Applications</h1>

    <button onclick="openModal()" class="px-4 py-2 bg-black text-white rounded-md text-sm">
        Create Application
    </button>
</div>

<table class="w-full bg-white border border-gray-200 rounded-xl text-sm">
    <thead class="border-b bg-gray-50">
        <tr>
            <th class="text-left p-3">Job Title</th>
            <th class="text-left p-3">Company</th>
            <th class="text-left p-3">Status</th>
            <th class="text-left p-3">Created</th>
        </tr>
    </thead>
    <tbody>
        {% for app in applications %}
        <tr onclick="window.location='/applications/{{ app._id }}'" class="cursor-pointer hover:bg-gray-50 border-b">
            <td class="p-3">{{ app.job_title or "—" }}</td>
            <td class="p-3">{{ app.company_name or "—" }}</td>
            <td class="p-3 capitalize">{{ app.status }}</td>
            <td class="p-3">
                {{ app.created_at.strftime('%b %d, %Y') }}
            </td>
        </tr>
        {% else %}
        <tr>
            <td colspan="4" class="p-6 text-center text-gray-500">
                No applications yet
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>

{% include "applications/modal.html" %}
{% endblock %}

```

### views/applications/modal.html

```html
<div id="modal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center">

    <div class="bg-white rounded-xl w-full max-w-xl p-6">

        <h2 class="text-lg font-semibold mb-4">
            New Application
        </h2>

        <form method="post" action="/applications">
            <textarea name="job_description" required rows="8" placeholder="Paste job description here..." class="w-full border border-gray-300 rounded-md p-3 text-sm
                       focus:ring-2 focus:ring-black"></textarea>

            <div class="mt-6 flex justify-end gap-3">
                <button type="button" onclick="closeModal()" class="text-sm text-gray-600">
                    Cancel
                </button>

                <button class="px-4 py-2 bg-black text-white rounded-md text-sm">
                    Create
                </button>
            </div>
        </form>

    </div>
</div>

<script>
    function openModal() {
        document.getElementById("modal").classList.remove("hidden");
    }
    function closeModal() {
        document.getElementById("modal").classList.add("hidden");
    }
</script>

```

### views/auth/login.html

```html
{% extends "layouts/auth.html" %}
{% set heading = "Welcome back" %}

{% block content %}
<form method="post" class="space-y-4">

    <input name="email" type="email" placeholder="Email"
        class="w-full px-4 py-2      border border-zinc-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-white" />

    <input name="password" type="password" placeholder="Password"
        class="w-full px-4 py-2  border border-zinc-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-white" />

    <button class="w-full py-2 rounded-lg bg-black text-white text-black font-medium hover:bg-gray-200 transition">
        Login
    </button>

    <p class="text-sm text-center text-zinc-400">
        New here?
        <a href="/signup" class="text-black underline">Create account</a>
    </p>

</form>
{% endblock %}

```

### views/auth/signup.html

```html
{% extends "layouts/auth.html" %}
{% set heading = "Create your account" %}

{% block content %}
<form method="post" class="space-y-4">

    <input name="name" placeholder="Full name" class="w-full px-4 py-2  border border-zinc-800 rounded-lg" />

    <input name="email" type="email" placeholder="Email" class="w-full px-4 py-2  border border-zinc-800 rounded-lg" />

    <input name="password" type="password" placeholder="Password"
        class="w-full px-4 py-2  border border-zinc-800 rounded-lg" />

    <button class="w-full py-2 bg-black  text-white rounded-lg font-medium">
        Sign up
    </button>

    <p class="text-sm text-center text-zinc-400">
        Already have an account?
        <a href="/login" class="underline text-black">Login</a>
    </p>

</form>
{% endblock %}

```

### views/dashboard/index.html

```html
{% extends "layouts/dashboard.html" %}

{% block content %}
<h1 class="text-2xl font-semibold mb-2">Dashboard</h1>
<p class="text-gray-600">
    Welcome back 👋
</p>
{% endblock %}

```

### views/layouts/auth.html

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <title>{{ title or "ApplyTailored" }}</title>
    <script src="https://cdn.tailwindcss.com"></script>

</head>

<body class="min-h-screen flex items-center justify-center  ">

    <div class="w-full max-w-md  border border-zinc-800 rounded-xl p-8 shadow-xl">
        <h1 class="text-2xl text-black font-semibold text-center mb-6">
            {{ heading }}
        </h1>

        {% if error %}
        <div class="mb-4 text-sm text-red-400 bg-red-950/40 border border-red-900 rounded-lg p-3">
            {{ error }}
        </div>
        {% endif %}

        {% block content %}{% endblock %}
    </div>

</body>

</html>

```

### views/layouts/dashboard.html

```html
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <title>Dashboard • ApplyTailored</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>

<body class="min-h-screen flex bg-gray-50 text-gray-900">

    {% include "partials/sidebar.html" %}

    <main class="flex-1 p-10">
        {% block content %}{% endblock %}
    </main>

</body>


</html>

```

### views/layouts/signup.html

```html
{% extends "layouts/auth.html" %}
{% set heading = "Create your account" %}

{% block content %}
<form method="post" class="space-y-4">

    <input name="name" placeholder="Full name"
        class="w-full px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-white" />

    <input name="email" type="email" placeholder="Email"
        class="w-full px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-white" />

    <input name="password" type="password" placeholder="Password"
        class="w-full px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-white" />

    <button class="w-full py-2 rounded-lg bg-white text-black font-medium hover:bg-gray-200 transition">
        Sign up
    </button>

    <p class="text-sm text-center text-zinc-400">
        Already have an account?
        <a href="/login" class="text-white underline">Login</a>
    </p>

</form>
{% endblock %}

```

### views/partials/navbar.html

```html
<header class="border-b border-zinc-800 bg-zinc-950">
    <div class="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <span class="font-semibold tracking-tight text-white">ApplyTailored</span>

        <div class="flex items-center gap-4 text-sm">
            <a href="/profile" class="text-zinc-400 hover:text-white transition">Profile</a>
            <a href="/logout" class="text-zinc-400 hover:text-white transition">Logout</a>
        </div>
    </div>
</header>

```

### views/partials/sidebar.html

```html
<aside class="w-64 bg-white border-r border-gray-200 p-6 flex flex-col">
    <h2 class="text-sm font-semibold tracking-tight mb-8">
        ApplyTailored
    </h2>

    <nav class="space-y-3 text-sm">
        <a href="/dashboard" class="block px-2 py-1 rounded-md
           {{ 'bg-gray-100 text-black' if request.path == '/dashboard'
           else 'text-gray-600 hover:text-black hover:bg-gray-100' }}">
            Dashboard
        </a>

        <a href="/applications" class="block px-3 py-2 rounded-md
           {{ 'bg-gray-100 text-black'
              if request.path.startswith('/applications')
              else 'text-gray-600 hover:bg-gray-100 hover:text-black' }}">
            Applications
        </a>

        <a href="/profile" class="block px-2 py-1 rounded-md
           {{ 'bg-gray-100 text-black' if request.path == '/profile'
           else 'text-gray-600 hover:text-black hover:bg-gray-100' }}">
            Profile
        </a>
    </nav>

    <div class="mt-auto pt-8">
        <a href="/logout" class="block text-sm text-gray-500 hover:text-black">
            Logout
        </a>
    </div>
</aside>

```

### views/profile/index.html

```html
{% extends "layouts/dashboard.html" %}

{% block content %}
<div class="max-w-4xl">

    <h1 class="text-2xl font-semibold mb-6">Profile</h1>

    <!-- User Information -->
    <div class="bg-white border border-gray-200 rounded-xl shadow-sm divide-y mb-6">

        <!-- Name -->
        <div class="px-6 py-4">
            <p class="text-sm text-gray-500">Name</p>
            <p class="text-base font-medium text-gray-900">
                {{ user.name }}
            </p>
        </div>

        <!-- Email -->
        <div class="px-6 py-4">
            <p class="text-sm text-gray-500">Email</p>
            <p class="text-base text-gray-900">
                {{ user.email }}
            </p>
        </div>

        <!-- Role -->
        <div class="px-6 py-4">
            <p class="text-sm text-gray-500">Role</p>
            <p class="text-base capitalize text-gray-900">
                {{ user.role }}
            </p>
        </div>

        <!-- Created -->
        <div class="px-6 py-4">
            <p class="text-sm text-gray-500">Account created</p>
            <p class="text-base text-gray-900">
                {{ user.created_at.strftime('%B %d, %Y') }}
            </p>
        </div>

    </div>

    <!-- Base Resumes Section -->
    <div class="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold">Base Resume Templates</h2>
            <button onclick="openUploadModal()"
                class="px-4 py-2 bg-black text-white rounded-md text-sm hover:bg-gray-800">
                Upload New Template
            </button>
        </div>

        <p class="text-sm text-gray-600 mb-4">
            Upload your resume in LaTeX format. Configure which sections to regenerate automatically for each job.
        </p>

        {% if base_resumes %}
        <div class="space-y-3">
            {% for resume in base_resumes %}
            <div class="p-4 border border-gray-200 rounded-lg 
                        {% if resume.is_active %}bg-green-50 border-green-200{% else %}hover:bg-gray-50{% endif %}">

                <!-- Resume Header -->
                <div class="flex items-start justify-between mb-3">
                    <div class="flex-1">
                        <div class="flex items-center gap-3">
                            <h3 class="font-medium text-gray-900">{{ resume.title }}</h3>
                            {% if resume.is_active %}
                            <span class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                                Active
                            </span>
                            {% endif %}
                            {% if resume.class_file %}
                            <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                                + Class File
                            </span>
                            {% endif %}

                            <!-- NEW: Selective Regeneration Status Badge -->
                            {% if resume.section_preferences and resume.section_preferences.enabled %}
                            <span
                                class="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium flex items-center gap-1">
                                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                        clip-rule="evenodd"></path>
                                </svg>
                                Selective ({{ resume.section_preferences.selected_sections|length }} sections)
                            </span>
                            {% endif %}
                        </div>
                        {% if resume.description %}
                        <p class="text-sm text-gray-600 mt-1">{{ resume.description }}</p>
                        {% endif %}
                        <p class="text-xs text-gray-500 mt-1">
                            Uploaded {{ resume.created_at.strftime('%B %d, %Y') }}
                            {% if resume.class_file %}
                            • Includes: {{ resume.class_file }}
                            {% endif %}
                        </p>
                    </div>

                    <!-- Toggle Switch -->
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" class="sr-only peer" {% if resume.is_active %}checked{% endif %}
                            onchange="toggleActiveResume('{{ resume._id }}', this.checked)">
                        <div
                            class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600">
                        </div>
                        <span class="ml-3 text-sm font-medium text-gray-900">Active</span>
                    </label>
                </div>

                <!-- Action Buttons -->
                <div class="flex flex-wrap gap-2">
                    <!-- NEW: Section Preferences Button -->
                    <a href="/resume/{{ resume._id }}/preferences"
                        class="px-3 py-1.5 bg-purple-600 text-white rounded-md text-sm hover:bg-purple-700 flex items-center gap-1.5">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4">
                            </path>
                        </svg>
                        Section Preferences
                    </a>

                    <a href="/base-resumes/{{ resume._id }}/download"
                        class="px-3 py-1.5 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50">
                        Download .tex
                    </a>

                    {% if resume.class_file %}
                    <a href="/base-resumes/{{ resume._id }}/download-class"
                        class="px-3 py-1.5 border border-blue-300 text-blue-700 rounded-md text-sm hover:bg-blue-50">
                        Download .cls
                    </a>
                    {% endif %}

                    {% if not resume.is_active %}
                    <button onclick="confirmDeleteResume('{{ resume._id }}', '{{ resume.title }}')"
                        class="px-3 py-1.5 border border-red-300 text-red-700 rounded-md text-sm hover:bg-red-50">
                        Delete
                    </button>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div class="text-center py-8 text-gray-500">
            <p>No base resume templates uploaded yet.</p>
            <p class="text-sm mt-2">Upload a LaTeX template to get started.</p>
        </div>
        {% endif %}
    </div>

</div>

<!-- Upload Modal -->
<div id="uploadModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl w-full max-w-md p-6 max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-lg font-semibold">Upload Base Resume Template</h2>
            <button onclick="closeUploadModal()" class="text-gray-500 hover:text-gray-700">
                ✕
            </button>
        </div>

        <form method="POST" action="/base-resumes" enctype="multipart/form-data" class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Template Title
                </label>
                <input type="text" name="title" required placeholder="e.g., Professional Resume 2024"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-black focus:outline-none">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Description (optional)
                </label>
                <textarea name="description" rows="2" placeholder="Brief description of this template"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-black focus:outline-none"></textarea>
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    LaTeX File (.tex) *
                </label>
                <input type="file" name="latex" accept=".tex" required
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-black focus:outline-none">
            </div>

            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    Class File (.cls) - Optional
                </label>
                <input type="file" name="class_file" accept=".cls"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-black focus:outline-none">
                <p class="text-xs text-gray-500 mt-1">
                    Upload if your resume uses a custom class (e.g., lmdEN.cls, moderncv.cls)
                </p>
            </div>

            <div class="bg-blue-50 border border-blue-200 rounded-md p-3">
                <p class="text-xs text-blue-800">
                    <strong>Tip:</strong> After uploading, click "Section Preferences" to choose which sections to
                    auto-regenerate for each job.
                </p>
            </div>

            <div class="flex justify-end gap-3 mt-6">
                <button type="button" onclick="closeUploadModal()"
                    class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50">
                    Cancel
                </button>
                <button type="submit" class="px-4 py-2 bg-black text-white rounded-md text-sm hover:bg-gray-800">
                    Upload Template
                </button>
            </div>
        </form>
    </div>
</div>

<!-- Confirmation Modal -->
<div id="confirmModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl w-full max-w-md p-6">
        <h2 class="text-lg font-semibold mb-4">Confirm Delete</h2>
        <p id="confirmMessage" class="text-gray-700 mb-6"></p>
        <div class="flex justify-end gap-3">
            <button onclick="closeConfirmModal()"
                class="px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50">
                Cancel
            </button>
            <button id="confirmButton" onclick="executeDelete()"
                class="px-4 py-2 bg-red-600 text-white rounded-md text-sm hover:bg-red-700">
                Delete
            </button>
        </div>
    </div>
</div>

<!-- Loading Modal -->
<div id="loadingModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl p-8 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-black mx-auto mb-4"></div>
        <p class="text-gray-700">Updating...</p>
    </div>
</div>

<script>
    let deleteResumeId = null;

    function openUploadModal() {
        document.getElementById('uploadModal').classList.remove('hidden');
    }

    function closeUploadModal() {
        document.getElementById('uploadModal').classList.add('hidden');
    }

    function toggleActiveResume(resumeId, isChecked) {
        document.getElementById('loadingModal').classList.remove('hidden');

        if (isChecked) {
            fetch('/base-resumes/' + resumeId + '/activate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loadingModal').classList.add('hidden');
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Error: ' + (data.error || 'Failed to activate resume'));
                        location.reload();
                    }
                })
                .catch(error => {
                    document.getElementById('loadingModal').classList.add('hidden');
                    alert('Error: ' + error.message);
                    location.reload();
                });
        } else {
            document.getElementById('loadingModal').classList.add('hidden');
            alert('You must have at least one active resume. Please activate another resume first.');
            location.reload();
        }
    }

    function confirmDeleteResume(resumeId, resumeTitle) {
        deleteResumeId = resumeId;
        document.getElementById('confirmMessage').textContent =
            `Are you sure you want to delete "${resumeTitle}"?`;
        document.getElementById('confirmModal').classList.remove('hidden');
    }

    function closeConfirmModal() {
        document.getElementById('confirmModal').classList.add('hidden');
        deleteResumeId = null;
    }

    function executeDelete() {
        if (!deleteResumeId) return;

        document.getElementById('confirmModal').classList.add('hidden');
        document.getElementById('loadingModal').classList.remove('hidden');

        fetch('/base-resumes/' + deleteResumeId, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loadingModal').classList.add('hidden');
                if (data.success) {
                    location.reload();
                } else {
                    alert('Error: ' + (data.error || 'Failed to delete resume'));
                }
            })
            .catch(error => {
                document.getElementById('loadingModal').classList.add('hidden');
                alert('Error: ' + error.message);
            });
    }
</script>

{% endblock %}

```

### views/resume/section_preferences.html

```html
{% extends "layouts/dashboard.html" %}

{% block content %}
<div class="max-w-5xl mx-auto">

    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
        <div>
            <a href="/profile" class="text-gray-600 hover:text-black mb-2 inline-block">
                ← Back to Profile
            </a>
            <h1 class="text-2xl font-semibold">Section Preferences</h1>
            <p class="text-gray-600 mt-1">
                Choose which sections to automatically regenerate for new job applications
            </p>
        </div>
    </div>

    <!-- Info Card -->
    <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
        <div class="flex gap-3">
            <svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor"
                viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div>
                <p class="text-sm text-blue-800 font-medium mb-1">How this works:</p>
                <ul class="text-sm text-blue-700 space-y-1">
                    <li>• Select which sections you want to be updated for each job application</li>
                    <li>• When you create a new application, only these sections will be regenerated</li>
                    <li>• Other sections will stay exactly as they are in your base resume</li>
                    <li>• This gives you precise control and faster processing</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Left: Controls -->
        <div class="lg:col-span-1">
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 sticky top-6">
                <h2 class="text-lg font-semibold mb-4">Controls</h2>

                <!-- Enable/Disable Toggle -->
                <div class="mb-6">
                    <label class="flex items-center justify-between cursor-pointer">
                        <span class="text-sm font-medium text-gray-700">Enable Selective Regeneration</span>
                        <div class="relative">
                            <input type="checkbox" id="enableSelective" onchange="toggleSelective(this.checked)"
                                class="sr-only peer">
                            <div
                                class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600">
                            </div>
                        </div>
                    </label>
                    <p class="text-xs text-gray-500 mt-2">
                        When enabled, new applications will only regenerate selected sections
                    </p>
                </div>

                <!-- Status Display -->
                <div id="statusDisplay" class="hidden mb-6 p-3 bg-green-50 border border-green-200 rounded-md">
                    <p class="text-sm text-green-800 font-medium mb-1">
                        ✓ Selective regeneration enabled
                    </p>
                    <p class="text-xs text-green-700">
                        <span id="sectionCount">0</span> sections will be regenerated
                    </p>
                </div>

                <!-- Buttons -->
                <div class="space-y-3">
                    <button onclick="loadSections()"
                        class="w-full px-4 py-2 bg-black text-white rounded-md text-sm hover:bg-gray-800">
                        Load Resume Sections
                    </button>

                    <button onclick="selectAllSections()" id="selectAllBtn"
                        class="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50"
                        disabled>
                        Select All Sections
                    </button>

                    <button onclick="clearAllSections()" id="clearAllBtn"
                        class="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-md text-sm hover:bg-gray-50"
                        disabled>
                        Clear All
                    </button>

                    <button onclick="savePreferences()" id="saveBtn"
                        class="w-full px-4 py-2 bg-green-600 text-white rounded-md text-sm hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled>
                        Save Preferences
                    </button>
                </div>
            </div>
        </div>

        <!-- Right: Resume Sections -->
        <div class="lg:col-span-2">
            <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                <h2 class="text-lg font-semibold mb-4">Resume Sections</h2>

                <!-- Loading State -->
                <div id="sectionsLoading" class="text-center py-12">
                    <svg class="animate-spin h-8 w-8 text-gray-400 mx-auto mb-3" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                        </circle>
                        <path class="opacity-75" fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                        </path>
                    </svg>
                    <p class="text-gray-600">Click "Load Resume Sections" to view your resume structure</p>
                </div>

                <!-- Sections Container -->
                <div id="sectionsContainer" class="space-y-3 hidden">
                    <!-- Sections will be loaded here -->
                </div>
            </div>
        </div>

    </div>

</div>

<!-- Success Modal -->
<div id="successModal" class="fixed inset-0 bg-black/30 hidden flex items-center justify-center z-50">
    <div class="bg-white rounded-xl p-8 text-center max-w-md">
        <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
        </div>
        <h3 class="text-lg font-semibold mb-2">Preferences Saved!</h3>
        <p class="text-gray-600 mb-6">
            Your section preferences have been saved. New applications will automatically use these settings.
        </p>
        <button onclick="closeSuccessModal()"
            class="px-6 py-2 bg-black text-white rounded-md text-sm hover:bg-gray-800">
            Got it
        </button>
    </div>
</div>

<script>
    const resumeId = '{{ resume_id }}';
    let sectionsData = [];
    let selectedSections = new Set();
    let selectiveEnabled = false;

    // Load existing preferences on page load
    window.addEventListener('DOMContentLoaded', async () => {
        try {
            const response = await fetch(`/resume/${resumeId}/preferences/get`);
            const data = await response.json();

            if (data.success) {
                const prefs = data.preferences;
                selectiveEnabled = prefs.enabled || false;
                selectedSections = new Set(prefs.selected_sections || []);

                document.getElementById('enableSelective').checked = selectiveEnabled;
                updateStatusDisplay();

                // If sections were previously loaded, show them
                if (prefs.parsed_structure) {
                    sectionsData = prefs.parsed_structure;
                    renderSections(sectionsData);
                    document.getElementById('sectionsLoading').classList.add('hidden');
                    document.getElementById('sectionsContainer').classList.remove('hidden');
                    enableButtons();
                }
            }
        } catch (error) {
            console.error('Error loading preferences:', error);
        }
    });

    function toggleSelective(enabled) {
        selectiveEnabled = enabled;
        updateStatusDisplay();

        if (enabled && sectionsData.length === 0) {
            alert('Please load resume sections first');
            document.getElementById('enableSelective').checked = false;
            selectiveEnabled = false;
        }
    }

    function updateStatusDisplay() {
        const statusDisplay = document.getElementById('statusDisplay');
        const sectionCount = document.getElementById('sectionCount');

        if (selectiveEnabled) {
            statusDisplay.classList.remove('hidden');
            sectionCount.textContent = selectedSections.size;
        } else {
            statusDisplay.classList.add('hidden');
        }

        // Enable/disable save button
        document.getElementById('saveBtn').disabled = !selectiveEnabled;
    }

    async function loadSections() {
        document.getElementById('sectionsLoading').innerHTML = `
        <svg class="animate-spin h-8 w-8 text-gray-400 mx-auto mb-3" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-gray-600">Loading resume structure...</p>
    `;

        try {
            const response = await fetch(`/resume/${resumeId}/sections`);
            const data = await response.json();

            if (data.success) {
                sectionsData = data.sections;
                renderSections(sectionsData);
                document.getElementById('sectionsLoading').classList.add('hidden');
                document.getElementById('sectionsContainer').classList.remove('hidden');
                enableButtons();
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            alert('Error loading sections: ' + error.message);
        }
    }

    function renderSections(sections) {
        const container = document.getElementById('sectionsContainer');
        container.innerHTML = '';

        sections.forEach(section => {
            const isSelected = selectedSections.has(section.id);

            const sectionDiv = document.createElement('div');
            sectionDiv.className = `border rounded-lg p-4 transition ${isSelected ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-gray-300'
                }`;

            sectionDiv.innerHTML = `
            <div class="flex items-start gap-3">
                <input 
                    type="checkbox" 
                    id="section_${section.id}"
                    ${isSelected ? 'checked' : ''}
                    onchange="toggleSection('${section.id}', this.checked)"
                    class="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500 mt-1"
                >
                <div class="flex-1">
                    <label for="section_${section.id}" class="cursor-pointer">
                        <div class="flex items-center gap-2 mb-2">
                            <h3 class="font-medium text-gray-900">${section.title}</h3>
                            <span class="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs uppercase">
                                ${section.type}
                            </span>
                        </div>
                        <p class="text-sm text-gray-600 mb-2">${section.preview}</p>
                    </label>
                    
                    ${section.has_subsections ? `
                        <details class="mt-3">
                            <summary class="text-sm text-gray-500 cursor-pointer hover:text-gray-700">
                                ${section.subsections.length} subsection(s) • Click to expand
                            </summary>
                            <div class="mt-2 pl-4 space-y-2">
                                ${section.subsections.map(sub => `
                                    <div class="text-sm border-l-2 border-gray-200 pl-3 py-1">
                                        <p class="font-medium text-gray-700">${sub.title}</p>
                                        <p class="text-xs text-gray-500">${sub.line_count} bullet point(s)</p>
                                    </div>
                                `).join('')}
                            </div>
                        </details>
                    ` : ''}
                </div>
            </div>
        `;

            container.appendChild(sectionDiv);
        });
    }

    function toggleSection(sectionId, isChecked) {
        if (isChecked) {
            selectedSections.add(sectionId);
        } else {
            selectedSections.delete(sectionId);
        }

        updateStatusDisplay();
        renderSections(sectionsData);
    }

    function selectAllSections() {
        sectionsData.forEach(section => {
            selectedSections.add(section.id);
            const checkbox = document.getElementById(`section_${section.id}`);
            if (checkbox) checkbox.checked = true;
        });

        updateStatusDisplay();
        renderSections(sectionsData);
    }

    function clearAllSections() {
        selectedSections.clear();

        sectionsData.forEach(section => {
            const checkbox = document.getElementById(`section_${section.id}`);
            if (checkbox) checkbox.checked = false;
        });

        updateStatusDisplay();
        renderSections(sectionsData);
    }

    function enableButtons() {
        document.getElementById('selectAllBtn').disabled = false;
        document.getElementById('clearAllBtn').disabled = false;
    }

    async function savePreferences() {
        const saveBtn = document.getElementById('saveBtn');
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';

        try {
            const response = await fetch(`/resume/${resumeId}/preferences`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    enabled: selectiveEnabled,
                    selected_sections: Array.from(selectedSections)
                })
            });

            const data = await response.json();

            if (data.success) {
                document.getElementById('successModal').classList.remove('hidden');
            } else {
                alert('Error: ' + data.error);
            }
        } catch (error) {
            alert('Error saving preferences: ' + error.message);
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save Preferences';
        }
    }

    function closeSuccessModal() {
        document.getElementById('successModal').classList.add('hidden');
    }
</script>

{% endblock %}

```