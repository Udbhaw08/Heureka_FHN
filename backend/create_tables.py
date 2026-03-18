"""
Create all database tables using SQLAlchemy models directly
This bypasses Alembic migrations
"""
import asyncio
from app.database import engine
from app.models import Base

async def create_tables():
    print("Creating database tables...")
    print("=" * 50)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("\n✓ All tables created successfully!")
    print("\n" + "=" * 50)
    
    # Verify tables
    from sqlalchemy import text
    async with engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name != 'alembic_version'
            ORDER BY table_name
        """))
        
        tables = [row[0] for row in result]
        
        if tables:
            print(f"\n✓ Created {len(tables)} tables:\n")
            for table in tables:
                print(f"  ✓ {table}")
        else:
            print("\n✗ No tables created!")
            return False
    
    # Now stamp the database with current migration
    print("\n" + "=" * 50)
    print("Marking database as up-to-date...")
    import subprocess
    result = subprocess.run(["alembic", "stamp", "head"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Database marked as up-to-date!")
    else:
        print("⚠ Could not stamp database, but tables are created")
    
    print("\n" + "=" * 50)
    print("✓ Database setup complete!")
    return True

if __name__ == "__main__":
    success = asyncio.run(create_tables())
    exit(0 if success else 1)
