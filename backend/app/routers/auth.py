from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets

from app.database import get_db
from app.models import Candidate
from app.schemas import (
    CandidateRegister, CandidateLogin, CandidateResponse
)
from app.auth_utils import hash_password, verify_password
from app.auth0_verifier import get_current_user_claims

router = APIRouter(prefix="/auth", tags=["auth"])

def _new_anon_id() -> str:
    return "ANON-" + secrets.token_hex(6).upper()

@router.post("/candidate/signup", response_model=CandidateResponse)
async def candidate_signup(
    payload: CandidateRegister,
    db: AsyncSession = Depends(get_db),
):
    q = await db.execute(
        select(Candidate).where(Candidate.email == payload.email.lower().strip())
    )
    if q.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    try:
        pw_hash = hash_password(payload.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    cand = Candidate(
        anon_id=_new_anon_id(),
        email=payload.email.lower().strip(),
        password_hash=pw_hash,
        name=payload.name,
        gender=payload.gender,
        college=payload.college,
        engineer_level=payload.engineer_level,
    )

    db.add(cand)
    await db.commit()
    await db.refresh(cand)

    return CandidateResponse(
        id=cand.id,
        anon_id=cand.anon_id,
        email=cand.email,
        name=cand.name,
        gender=cand.gender,
        college=cand.college,
        engineer_level=cand.engineer_level,
        created_at=cand.created_at
    )

@router.post("/candidate/login", response_model=CandidateResponse)
async def candidate_login(payload: CandidateLogin, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(Candidate).where(Candidate.email == payload.email.lower().strip()))
    cand = q.scalar_one_or_none()
    
    print(f"[AUTH-DEBUG] Login attempt for: {payload.email}")
    if not cand:
        print(f"[AUTH-DEBUG] Candidate not found: {payload.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not verify_password(payload.password, cand.password_hash):
        print(f"[AUTH-DEBUG] Password verification failed for: {payload.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    print(f"[AUTH-DEBUG] Login successful: {payload.email}")

    return CandidateResponse(
        id=cand.id,
        anon_id=cand.anon_id,
        email=cand.email,
        name=cand.name,
        gender=cand.gender,
        college=cand.college,
        engineer_level=cand.engineer_level,
        created_at=cand.created_at
    )


# ==================== COMPANY AUTH ====================

@router.post("/company/signup")
async def company_signup(payload: dict, db: AsyncSession = Depends(get_db)):
    """
    Company signup - simplified version
    Expects: {name, email, password}
    """
    email = payload.get("email", "").lower().strip()
    name = payload.get("name", "").strip()
    password = payload.get("password", "")
    
    if not email or not name or not password:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # For now, store company_id as email (simplified - no Company table)
    # In production, you'd create a Company table
    company_id = email.replace("@", "_").replace(".", "_")
    
    return {
        "company_id": company_id,
        "name": name,
        "email": email
    }


@router.post("/company/login")
async def company_login(payload: dict, db: AsyncSession = Depends(get_db)):
    """
    Company login - simplified version
    Expects: {email, password}
    """
    email = payload.get("email", "").lower().strip()
    password = payload.get("password", "")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Simplified - just return company_id based on email
    company_id = email.replace("@", "_").replace(".", "_")
    
    return {
        "company_id": company_id,
        "name": "Company Name",  # Placeholder
        "email": email
    }


# ==================== AUTH0 INTEGRATION ====================

@router.post("/candidate/auth0-sync", response_model=CandidateResponse)
async def candidate_auth0_sync(
    payload: dict,
    db: AsyncSession = Depends(get_db),
):
    """
    Auth0 Sync Endpoint.
    Called by the frontend immediately after Auth0 login.
    Accepts {sub, email, name} from the Auth0 user object (already authenticated client-side).
    Creates or retrieves the Candidate DB row and returns the anon_id.
    """
    auth0_id: str = payload.get("sub", "")
    email: str = payload.get("email", "").lower().strip()
    name: str = payload.get("name") or email.split("@")[0] or "candidate"

    if not auth0_id:
        raise HTTPException(status_code=400, detail="Missing 'sub' field")

    # 1. Try to find by auth0_id first (most accurate)
    q = await db.execute(select(Candidate).where(Candidate.auth0_id == auth0_id))
    cand = q.scalar_one_or_none()

    # 2. Fallback: find by email (links existing old-system accounts to Auth0)
    if not cand and email:
        q = await db.execute(select(Candidate).where(Candidate.email == email))
        cand = q.scalar_one_or_none()
        if cand and cand.auth0_id is None:
            cand.auth0_id = auth0_id
            await db.commit()
            await db.refresh(cand)

    # 3. Create new candidate if not found
    if not cand:
        anon_id = "ANON-" + secrets.token_hex(6).upper()
        cand = Candidate(
            anon_id=anon_id,
            auth0_id=auth0_id,
            email=email,
            name=name,
            password_hash=None,
        )
        db.add(cand)
        await db.commit()
        await db.refresh(cand)

    return CandidateResponse(
        id=cand.id,
        anon_id=cand.anon_id,
        email=cand.email,
        name=cand.name,
        gender=cand.gender,
        college=cand.college,
        engineer_level=cand.engineer_level,
        created_at=cand.created_at,
    )
