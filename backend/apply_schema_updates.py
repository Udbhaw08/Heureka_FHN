
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:1234@localhost:5432/fair_hiring"
)

async def update_schema():
    print(f"🔄 Updating database schema: {DATABASE_URL}")
    engine = create_async_engine(DATABASE_URL)
    
    # Import models to register them with Base
    import sys
    sys.path.append(os.getcwd())
    from app.models import Base
    
    async with engine.begin() as conn:
        # This will create tables that don't exist
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database schema updated successfully.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(update_schema())
