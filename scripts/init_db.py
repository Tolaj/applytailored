import asyncio
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app.database as database
from app.models.user import User
from app.utils.security import hash_password
from app.utils.ids import generate_id


async def init_indexes_and_seed():
    """Initialize database indexes and seed with test data."""
    # Connect to DB
    await database.connect_db()

    # Access db from the module AFTER connection
    db = database.db
    if db is None:
        raise Exception("DB connection failed!")

    print("✓ Connected to MongoDB")

    # ------------------------
    # 1) Create Indexes
    # ------------------------
    print("Creating indexes...")
    await db.users.create_index("email", unique=True)
    await db.job_applications.create_index("user_id")
    await db.generated_assets.create_index("job_application_id")
    await db.generated_assets.create_index("user_id")
    await db.outreach_contacts.create_index("job_application_id")
    await db.followups.create_index("outreach_contact_id")
    await db.application_questions.create_index("job_application_id")
    await db.calendar_events.create_index("job_application_id")
    await db.base_resumes.create_index("user_id")
    await db.experience_responses.create_index("job_application_id")
    print("✓ Indexes created")

    # ------------------------
    # 2) Seed Data
    # ------------------------
    print("Seeding data...")

    # Check if test user already exists
    existing = await db.users.find_one({"email": "test@example.com"})

    if not existing:
        # Create test user
        test_user = User(
            email="test@example.com",
            name="Test User",
            password_hash=hash_password("password123"),
        )
        await db.users.insert_one(test_user.model_dump(by_alias=True))
        user_id = test_user.id
        print(f"✓ Test user created with ID: {user_id}")
        print(f"  Email: test@example.com")
        print(f"  Password: password123")
    else:
        user_id = existing["_id"]
        print(f"✓ Test user already exists with ID: {user_id}")

    # Example: Base Resume for test user
    if await db.base_resumes.count_documents({"user_id": user_id}) == 0:
        await db.base_resumes.insert_one(
            {
                "_id": generate_id(),
                "user_id": user_id,
                "title": "Default Resume",
                "description": "Seeded default resume",
                "latex_template_path": "storage/base_resumes/resume_v1.tex",
            }
        )
        print("✓ Default base resume created")
    else:
        print("✓ Default base resume already exists")

    # Close DB
    await database.close_db()
    print("\n✓ Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_indexes_and_seed())
