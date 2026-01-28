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
