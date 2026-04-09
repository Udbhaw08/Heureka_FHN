
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from root directory
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
RESUME_DIR = BASE_DIR / "data" / "resumes"

async def remove_data():
    if not DATABASE_URL:
        print("DATABASE_URL not set")
        return

    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        try:
            # 1. Identify files to delete before records are gone
            # Application 35 -> Job 17, Candidate ANON-EF8FF1E4D612
            # Application 36 -> Job 15, Candidate ANON-EF8FF1E4D612
            # Based on previous check
            
            app_35_file = RESUME_DIR / "ANON-EF8FF1E4D612_17.pdf"
            app_36_file = RESUME_DIR / "ANON-EF8FF1E4D612_15.pdf"

            # 2. Delete application records
            # CASCADE will take care of credentials, agent_runs, review_cases
            result = await conn.execute(text("DELETE FROM applications WHERE id IN (35, 36)"))
            print(f"✅ Deleted {result.rowcount} application records.")

            # 3. Delete files if they exist
            files_to_delete = [app_35_file, app_36_file]
            for file_path in files_to_delete:
                if file_path.exists():
                    os.remove(file_path)
                    print(f"✅ Deleted resume file: {file_path.name}")
                else:
                    print(f"⚠️ Resume file not found: {file_path.name}")

        except Exception as e:
            print(f"❌ Error during removal: {e}")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(remove_data())
