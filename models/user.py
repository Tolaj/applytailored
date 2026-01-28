from datetime import datetime


def user_model(email, name, password_hash, role="user"):
    return {
        "email": email.lower(),
        "name": name,
        "password": password_hash,
        "role": role,
        "created_at": datetime.utcnow(),
    }
