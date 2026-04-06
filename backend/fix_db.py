# pyright: reportMissingImports=false
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine # type: ignore
from sqlalchemy import text # type: ignore
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1234@localhost:5432/fair_hiring")

async def fix():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE companies ADD COLUMN password_hash VARCHAR(255) DEFAULT '';"))
            print("✅ Added password_hash to companies")
        except Exception as e:
            print(f"Error: {e}")
    await engine.dispose()

asyncio.run(fix())
