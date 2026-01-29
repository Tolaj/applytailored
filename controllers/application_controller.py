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
