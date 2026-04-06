import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
import shutil
from dotenv import load_dotenv

# Load environment variables (ensure it picks up your DATABASE_URL)
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1234@localhost:5432/fair_hiring")

async def reset_candidates():
    print(f"Connecting to Database: {DATABASE_URL}")
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        try:
            # Executes the DELETE on candidates. 
            # Thanks to SQLAlchemy 'ON DELETE CASCADE' constraints:
            # it will recursively delete 'applications', 'credentials', 'agent_runs', and 'review_cases'
            result = await conn.execute(text("DELETE FROM candidates;"))
            
            # Clear data directory
            data_dir = os.path.join(os.path.dirname(__file__), "data")
            if os.path.exists(data_dir):
                shutil.rmtree(data_dir)
                os.makedirs(os.path.join(data_dir, "resumes"), exist_ok=True)
                os.makedirs(os.path.join(data_dir, "linkedin"), exist_ok=True)
                print("✅ Cleared all downloaded resumes and LinkedIn profiles from backend/data")
                
            print("\n---------------------------------------------------------")
            print(f"✅ Successfully wiped {result.rowcount} candidates from the system.")
            print("✅ All associated Applications, Credentials, Passports, and Reviews were cleared.")
            print("🚀 The Job & Company database is completely untouched!")
            print("---------------------------------------------------------\n")
            
            print("You can now safely reuse your email/Auth0 account to test matching algorithms again.")
        except Exception as e:
            print(f"❌ Error during candidate reset: {e}")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_candidates())
