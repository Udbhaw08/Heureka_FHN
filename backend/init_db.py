"""
Initialize Database Tables

Run this script to create all database tables.
This is needed before running the application for the first time.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import init_db, engine
from app.models import Base

async def main():
    print("Initializing database...")
    print(f"Database URL: {engine.url}")
    
    try:
        await init_db()
        print("✅ Database tables created successfully!")
        print("\nTables created:")
        print("  - candidates")
        print("  - companies")
        print("  - jobs")
        print("  - applications")
        print("  - passports")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
