import os
from app.config import GENERATED_DIR
import uuid


def save_text_file(content: str, subfolder: str, prefix: str) -> str:
    """Save text content to a file."""
    folder = os.path.join(GENERATED_DIR, subfolder)
    os.makedirs(folder, exist_ok=True)
    filename = f"{prefix}_{uuid.uuid4().hex}.txt"
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
