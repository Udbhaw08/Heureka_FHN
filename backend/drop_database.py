import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to postgres database (not the target database)
DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/postgres"

async def drop_database():
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    # Connect with AUTOCOMMIT mode (DROP DATABASE cannot run inside a transaction)
    async with engine.connect() as conn:
        await conn.execute(text("COMMIT"))  # Ensure no transaction is active
        
        # Terminate all connections to the database
        await conn.execute(text("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'Udbhaw_Db'
            AND pid <> pg_backend_pid();
        """))
        
        # Drop the database (must be in AUTOCOMMIT mode)
        await conn.execute(text("DROP DATABASE IF EXISTS \"Udbhaw_Db\""))
        print("✅ Database 'Udbhaw_Db' dropped successfully")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(drop_database())