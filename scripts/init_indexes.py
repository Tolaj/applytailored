import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app.database as database


async def init_indexes():
    """Initialize database indexes."""
    # Connect to DB
    await database.connect_db()

    # Access the database AFTER connection
    db = database.db
    if db is None:
        raise Exception("DB connection failed!")

    # Create indexes
    print("Creating indexes...")
    await db.users.create_index("email", unique=True)
    await db.job_applications.create_index("user_id")
    await db.generated_assets.create_index("job_application_id")
    await db.outreach_contacts.create_index("job_application_id")

    print("✓ Indexes initialized successfully!")

    # Close DB connection
    await database.close_db()


if __name__ == "__main__":
    asyncio.run(init_indexes())
