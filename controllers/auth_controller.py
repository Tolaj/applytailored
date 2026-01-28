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
