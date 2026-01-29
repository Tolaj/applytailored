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
