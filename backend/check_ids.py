
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
if not DATABASE_URL:
    print("DATABASE_URL not set")
    exit(1)

async def check_ids():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        print("Checking Credentials table for IDs 35, 36:")
        try:
            res = await conn.execute(text("SELECT id, candidate_id, application_id FROM credentials WHERE id IN (35, 36)"))
            creds = res.fetchall()
            for c in creds:
                print(f"Credential ID: {c.id}, Candidate ID: {c.candidate_id}, Application ID: {c.application_id}")
                
            print("\nChecking Applications table for IDs 35, 36:")
            res = await conn.execute(text("SELECT id, candidate_id, job_id, resume_text FROM applications WHERE id IN (35, 36)"))
            apps = res.fetchall()
            for a in apps:
                snippet = a.resume_text[:50].replace('\n', ' ') if a.resume_text else "None"
                print(f"Application ID: {a.id}, Candidate ID: {a.candidate_id}, Job ID: {a.job_id}, Resume: {snippet}...")

            candidate_ids = set([c.candidate_id for c in creds] + [a.candidate_id for a in apps])
            if candidate_ids:
                print("\nChecking Candidates table:")
                res = await conn.execute(text(f"SELECT id, anon_id, email, name FROM candidates WHERE id IN ({','.join(map(str, candidate_ids))})"))
                cands = res.fetchall()
                for cand in cands:
                    print(f"Candidate ID: {cand.id}, Anon ID: {cand.anon_id}, Email: {cand.email}, Name: {cand.name}")

        except Exception as e:
            print(f"Error: {e}")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_ids())
