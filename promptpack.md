# PromptPack Output

**Root:** `/Users/swapnil/Documents/Projects/applytailored`
**Generated:** 2026-01-28T08:08:39.073Z

---

## 1) Folder Structure

```txt
.
├─ __pycache__/
│  ├─ config.cpython-312.pyc
│  └─ db.cpython-312.pyc
├─ app.py
├─ config.py
├─ controllers/
│  ├─ __pycache__/
│  │  ├─ ai_controller.cpython-312.pyc
│  │  ├─ application_controller.cpython-312.pyc
│  │  ├─ auth_controller.cpython-312.pyc
│  │  └─ profile_controller.cpython-312.pyc
│  ├─ ai_controller.py
│  ├─ application_controller.py
│  ├─ auth_controller.py
│  ├─ dashboard_controller.py
│  └─ profile_controller.py
├─ db.py
├─ middlewares/
│  ├─ __pycache__/
│  │  └─ auth_middleware.cpython-312.pyc
│  └─ auth_middleware.py
├─ models/
│  ├─ __pycache__/
│  │  ├─ generated_asset.cpython-312.pyc
│  │  ├─ job_application.cpython-312.pyc
│  │  └─ user.cpython-312.pyc
│  ├─ base_resume.py
│  ├─ generated_asset.py
│  ├─ job_application.py
│  └─ user.py
├─ public/
├─ QUICK_START.md
├─ README.md
├─ requirements.txt
├─ routes/
│  ├─ __pycache__/
│  │  ├─ application_routes.cpython-312.pyc
│  │  ├─ auth_routes.cpython-312.pyc
│  │  ├─ dashboard_routes.cpython-312.pyc
│  │  └─ profile_routes.cpython-312.pyc
│  ├─ application_routes.py
│  ├─ auth_routes.py
│  ├─ dashboard_routes.py
│  └─ profile_routes.py
├─ seed_database.py
├─ services/
│  ├─ __pycache__/
│  │  ├─ claude_ai_service.cpython-312.pyc
│  │  └─ latex_service.cpython-312.pyc
│  ├─ claude_ai_service.py
│  └─ latex_service.py
├─ storage/
│  ├─ base_resumes/
│  ├─ generated/
│  └─ resumes/
│     └─ base_resume_template.tex
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
   ├─ job/
   ├─ layouts/
   │  ├─ auth.html
   │  ├─ dashboard.html
   │  └─ signup.html
   ├─ partials/
   │  ├─ navbar.html
   │  └─ sidebar.html
   └─ profile/
      └─ index.html
```

<!-- PAGE BREAK: FILE CONTENTS BELOW -->

## 2) File Contents


### __pycache__/config.cpython-312.pyc

(Skipped: binary or unreadable file)


### __pycache__/db.cpython-312.pyc

(Skipped: binary or unreadable file)


### app.py

```python
from flask import Flask
from config import Config
from routes.auth_routes import auth_routes
from routes.dashboard_routes import dashboard_routes
from routes.application_routes import application_routes

from routes.profile_routes import profile_routes


def create_app():
    app = Flask(__name__, template_folder="views")  # <--- specify template folder
    app.config.from_object(Config)

    app.register_blueprint(auth_routes)
    app.register_blueprint(dashboard_routes)
    app.register_blueprint(profile_routes)
    app.register_blueprint(application_routes)

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

### controllers/__pycache__/ai_controller.cpython-312.pyc

(Skipped: binary or unreadable file)


### controllers/__pycache__/application_controller.cpython-312.pyc

(Skipped: binary or unreadable file)


### controllers/__pycache__/auth_controller.cpython-312.pyc

(Skipped: binary or unreadable file)


### controllers/__pycache__/profile_controller.cpython-312.pyc

(Skipped: binary or unreadable file)


### controllers/ai_controller.py

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
                {"_id": application["_id"]},
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
                {"_id": application["_id"]},
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
                {"_id": application["_id"]},
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

### controllers/application_controller.py

```python
from flask import render_template, request, redirect, g, jsonify
from bson.objectid import ObjectId
from db import db
from models.job_application import job_application_model
from controllers.ai_controller import AIController


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
    app = db.applications.find_one(
        {"_id": ObjectId(app_id), "user_id": g.user["user_id"]}
    )

    if not app:
        return redirect("/applications")

    # Get generated assets for this application
    generated_assets = list(
        db.generated_assets.find(
            {"job_application_id": app_id, "user_id": g.user["user_id"]}
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
    """Download a generated asset (PDF/TEX)"""
    from flask import send_file

    asset = db.generated_assets.find_one(
        {"_id": ObjectId(asset_id), "user_id": g.user["user_id"]}
    )

    if not asset:
        return "Asset not found", 404

    file_path = asset.get("pdf_path") or asset.get("tex_path")

    if not file_path:
        return "No file available", 404

    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{asset['title']}.{'pdf' if asset.get('pdf_path') else 'tex'}",
        )
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

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

    return render_template("profile/index.html", user=user)

```

### db.py

```python
from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]

```

### middlewares/__pycache__/auth_middleware.cpython-312.pyc

(Skipped: binary or unreadable file)


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

### models/__pycache__/generated_asset.cpython-312.pyc

(Skipped: binary or unreadable file)


### models/__pycache__/job_application.cpython-312.pyc

(Skipped: binary or unreadable file)


### models/__pycache__/user.cpython-312.pyc

(Skipped: binary or unreadable file)


### models/base_resume.py

```python
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

```

### models/generated_asset.py

```python
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

```

### models/job_application.py

```python
# models/job_application_updated.py
from datetime import datetime
from bson import ObjectId


def job_application_model(
    user_id, job_description, company_name=None, position_title=None
):
    """Factory function to create a new JobApplication instance"""
    return {
        "_id": str(ObjectId()),
        "user_id": user_id,
        "job_description": job_description,
        "company_name": company_name,
        "position_title": position_title,
        "status": "draft",  # draft / processing / completed / failed
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

### routes/__pycache__/application_routes.cpython-312.pyc

(Skipped: binary or unreadable file)


### routes/__pycache__/auth_routes.cpython-312.pyc

(Skipped: binary or unreadable file)


### routes/__pycache__/dashboard_routes.cpython-312.pyc

(Skipped: binary or unreadable file)


### routes/__pycache__/profile_routes.cpython-312.pyc

(Skipped: binary or unreadable file)


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
from flask import Blueprint
from controllers.profile_controller import profile
from middlewares.auth_middleware import require_auth

profile_routes = Blueprint("profile", __name__)


@profile_routes.route("/profile")
@require_auth
def profile_page():
    return profile()

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

### services/__pycache__/claude_ai_service.cpython-312.pyc

(Skipped: binary or unreadable file)


### services/__pycache__/latex_service.cpython-312.pyc

(Skipped: binary or unreadable file)


### services/claude_ai_service.py

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

### storage/resumes/base_resume_template.tex

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

### views/applications/detail.html

```html
{% extends "layouts/dashboard.html" %}

{% block content %}
<div class="max-w-5xl">

    <!-- Header with Back Button -->
    <div class="flex items-center gap-4 mb-6">
        <a href="/applications" class="text-gray-600 hover:text-black">
            ← Back to Applications
        </a>
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
                    <a href="/assets/{{ asset._id }}/download"
                        class="px-3 py-1 bg-black text-white rounded text-sm hover:bg-gray-800">
                        Download PDF
                    </a>
                    {% endif %}

                    {% if asset.type == 'cover_letter' %}
                    <button onclick="viewCoverLetter('{{ asset.content_text|e }}')"
                        class="px-3 py-1 border border-gray-300 text-gray-700 rounded text-sm hover:bg-gray-50">
                        View
                    </button>
                    {% endif %}
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

<script>
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

    function viewCoverLetter(content) {
        document.getElementById('coverLetterContent').textContent = content;
        document.getElementById('coverLetterModal').classList.remove('hidden');
    }

    function closeCoverLetterModal() {
        document.getElementById('coverLetterModal').classList.add('hidden');
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
<div class="max-w-3xl">

    <h1 class="text-2xl font-semibold mb-6">Profile</h1>

    <div class="bg-white border border-gray-200 rounded-xl shadow-sm divide-y">

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

</div>
{% endblock %}

```