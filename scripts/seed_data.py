import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app.database as database
from app.models.user import User
from app.models.job_application import JobApplication
from app.utils.security import hash_password


async def seed_data():
    """Seed the database with test data."""
    await database.connect_db()

    # Access db from the module AFTER connection
    db = database.db
    if db is None:
        raise Exception("DB connection failed!")

    # Create a test user
    test_user = User(
        email="test2@example.com",  # Different email to avoid conflicts
        name="Test User 2",
        password_hash=hash_password("password123"),
        role="user",
    )
    await db.users.insert_one(test_user.model_dump(by_alias=True))
    print(f"✓ Test user created with ID: {test_user.id}")

    # Create a sample job application
    job_app = JobApplication(
        user_id=test_user.id,
        company_name="Tech Corp",
        job_title="Software Engineer",
        job_description="Develop amazing software with cutting-edge technologies",
        status="draft",
    )
    await db.job_applications.insert_one(job_app.model_dump(by_alias=True))
    print(f"✓ Job application created with ID: {job_app.id}")

    print("✓ Seed data inserted successfully!")
    await database.close_db()


if __name__ == "__main__":
    asyncio.run(seed_data())
