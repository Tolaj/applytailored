import uuid


def generate_id() -> str:
    """Generate a unique ID for database documents."""
    return str(uuid.uuid4())
