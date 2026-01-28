"""
Database seeding script to initialize base resumes and collections
Run this once to set up the initial data
"""

from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "applytailored")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]


def seed_base_resume():
    """Create a default base resume entry"""

    # Check if default base resume already exists
    existing = db.base_resumes.find_one({"user_id": "default"})

    if existing:
        print("Default base resume already exists")
        return

    base_resume = {
        "_id": str(ObjectId()),
        "user_id": "default",
        "title": "Default Base Resume",
        "description": "A professional resume template that can be used as a starting point",
        "latex_template_path": "base_resume_template.tex",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    db.base_resumes.insert_one(base_resume)
    print(f"✓ Created default base resume with ID: {base_resume['_id']}")


def create_indexes():
    """Create database indexes for better query performance"""

    # Users collection indexes
    db.users.create_index("email", unique=True)
    print("✓ Created index on users.email")

    # Applications collection indexes
    db.applications.create_index([("user_id", 1), ("created_at", -1)])
    db.applications.create_index("status")
    print("✓ Created indexes on applications collection")

    # Base resumes collection indexes
    db.base_resumes.create_index([("user_id", 1)])
    print("✓ Created index on base_resumes.user_id")

    # Generated assets collection indexes
    db.generated_assets.create_index([("job_application_id", 1)])
    db.generated_assets.create_index([("user_id", 1), ("created_at", -1)])
    db.generated_assets.create_index("type")
    print("✓ Created indexes on generated_assets collection")


def verify_storage_directories():
    """Ensure all necessary storage directories exist"""

    directories = ["storage", "storage/base_resumes", "storage/generated"]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Verified directory: {directory}")


def main():
    print("Starting database seeding...\n")

    try:
        # Verify storage directories
        print("1. Checking storage directories...")
        verify_storage_directories()
        print()

        # Create indexes
        print("2. Creating database indexes...")
        create_indexes()
        print()

        # Seed base resume
        print("3. Seeding default base resume...")
        seed_base_resume()
        print()

        print("✅ Database seeding completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        raise
    finally:
        client.close()


if __name__ == "__main__":
    main()
