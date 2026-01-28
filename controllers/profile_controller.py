from flask import render_template, g
from bson.objectid import ObjectId
from db import db


def profile():
    user_id = g.user["user_id"]

    user = db.users.find_one(
        {"_id": ObjectId(user_id)}, {"password": 0}  # never send password to view
    )

    return render_template("profile/index.html", user=user)
