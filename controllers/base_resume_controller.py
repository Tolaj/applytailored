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
