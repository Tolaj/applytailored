import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "job_platform")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
GENERATED_DIR = os.path.join(STORAGE_DIR, "generated")

# Ensure directories exist
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)
