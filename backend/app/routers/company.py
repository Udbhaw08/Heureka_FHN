# pyright: reportMissingImports=false
from fastapi import APIRouter, Depends, HTTPException # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.database import get_db # type: ignore
from app.models import Job, Application, Candidate, Credential, AgentRun, ReviewCase, Company, Blacklist # type: ignore
from app.agents.jd_bias import JobBiasAgent # type: ignore
from app.agents.job_extraction import JobExtractionAgent # type: ignore
from sqlalchemy import select, func # type: ignore
from app.agent_client import AgentClient # type: ignore
from app.audit import log_event # type: ignore
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/company", tags=["company"])

async def call_match_agent(payload: dict) -> Dict[str, Any]:
    """Helper to call matching agent service"""
    client = AgentClient()
    res = await client.match_candidate(
        payload.get("credential", {}),
        payload.get("job_description", {})
    )
    if not res.get("success"):
        raise Exception(res.get("error", "Matching failed"))
    return res.get("data", {})

# Simplified endpoints - Company model doesn't exist yet

@router.get("/{company_id}/jobs")
async def list_company_jobs(company_id: str, db: AsyncSession = Depends(get_db)):
    """List all jobs for a company"""
    logger.info(f"Fetching jobs for company_id: {company_id}")
    # Return jobs with aggregated application counts for dashboard cards.
    q = await db.execute(
        select(
            Job,
            func.count(Application.id).label("candidates_count"),
        )
        .outerjoin(Application, Application.job_id == Job.id)
        .where(Job.company_id == company_id)
        .group_by(Job.id)
        .order_by(Job.id.desc())
    )
    rows = q.all()
    out = []
    for job, cand_count in rows:
        out.append({
            "id": job.id,
            "company_id": job.company_id,
            "title": job.title,
            "description": job.description,
            "published": job.published,
            "max_participants": job.max_participants,
            "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None,
            "fairness_status": job.fairness_status or "VERIFIED",
            "fairness_score": job.fairness_score,
            "fairness_findings": job.fairness_findings,
            "required_skills": job.required_skills,
            "candidates_count": int(cand_count or 0),
        })
    return out


@router.post("/analyze_bias")
async def analyze_jd_bias(payload: dict):
    """Real-time AI bias audit for Job Description"""
    description = payload.get("description", "")
    if not description:
        return {"bias_score": 0, "findings": [], "reasoning": "Empty description"}
        
    try:
        bias_agent = JobBiasAgent()
        result = bias_agent.analyze(description)
        return result
    except Exception as e:
        logger.error(f"Real-time Bias Audit Error: {e}")
        return {"bias_score": 0, "findings": [], "error": str(e)}


@router.post("/job")
async def create_job(payload: dict, db: AsyncSession = Depends(get_db)):
    """Create a new job posting with AI bias audit"""
    logger.debug(f"create_job payload: {payload}")
    company_id = payload.get("company_id")
    title = payload.get("title")
    description = payload.get("description")
    published = payload.get("published", False)
    max_participants = payload.get("max_participants", 5)
    required_skills = payload.get("required_skills", {})
    
    logger.info(f"Processing job creation: {title} for {company_id}")
    
    if not company_id or not title or not description:
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # ensure company exists to avoid foreign key violation
    try:
        q_comp = await db.execute(select(Company).where(Company.id == company_id))
        company = q_comp.scalar_one_or_none()
        if not company:
            company = Company(
                id=company_id,
                name=f"Company {company_id}",
                email=f"contact@{company_id}.com"
            )
            db.add(company)
            await db.flush()
    except Exception as e:
        # If it failed due to concurrency, we don't care, as long as it exists now
        logger.warning(f"Company {company_id} creation conflict or error: {e}")
        await db.rollback()
        q_comp = await db.execute(select(Company).where(Company.id == company_id))
        company = q_comp.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=500, detail="Failed to ensure company existence")
    
    # 1. AI BIAS AUDIT (Stage 0)
    # Using JobBiasAgent instead of hardcoded keywords
    logger.info(f"Starting Bias Audit for: {title}")
    try:
        bias_agent = JobBiasAgent()
        bias_result = bias_agent.analyze(description)
        
        fairness_score = 100 - (bias_result.get("bias_score", 0) * 10)
        fairness_status = "VERIFIED" if fairness_score >= 80 else "FLAGGED"
        fairness_findings = bias_result.get("findings", [])
        logger.info(f"Bias Audit Completed. Score: {fairness_score}")
    except Exception as e:
        logger.error(f"Bias Audit Failed: {e}")
        # Fallback to neutral if AI fails
        fairness_score = 100
        fairness_status = "VERIFIED"
        fairness_findings = []

    # 2. AI SKILL/INTENT EXTRACTION (Stage 0.5)
    logger.info(f"Starting Skill Extraction for: {title}")
    intelligence_spec = {}
    try:
        jd_agent = JobExtractionAgent()
        intelligence_spec = jd_agent.extract(description, title=title)
        logger.debug(f"JD Intelligence v2 extracted: {intelligence_spec.get('role', 'Unknown')}")
    except Exception as e:
        logger.error(f"JD Intelligence Error: {e}")
        intelligence_spec = {"required_skills": []}

    # 3. CREATE JOB
    logger.info(f"Committing job to DB...")
    
    # FAVOR user-provided required_skills if they are non-empty, merge with AI extraction if success
    final_skills = required_skills or {}
    if intelligence_spec and not intelligence_spec.get("error"):
        # If AI worked, we can either merge or prefer AI. 
        # Here we prioritize AI extraction as it's "v2 intelligence", but keep user skills if AI failed.
        final_skills = intelligence_spec
    elif not final_skills:
        # If both fail/empty, keep the error object for debugging
        final_skills = intelligence_spec

    job = Job(
        company_id=company_id,
        title=title,
        description=description,
        required_skills=final_skills,
        fairness_score=fairness_score,
        fairness_status=fairness_status,
        fairness_findings=fairness_findings,
        published=published,
        max_participants=max_participants,
        created_at=datetime.utcnow()
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    logger.info(f"Job persisted successfully with ID: {job.id}")
    
    return {
        "job_id": job.id, 
        "published": job.published,
        "fairness_score": fairness_score,
        "fairness_status": fairness_status,
        "extraction_status": "ok" if intelligence_spec and not intelligence_spec.get("error") else "error",
        "extraction_error": intelligence_spec.get("error") if intelligence_spec else None
    }


@router.get("/{company_id}/stats")
async def company_stats(company_id: str, db: AsyncSession = Depends(get_db)):
    """Get company statistics"""
    q_jobs = await db.execute(select(Job).where(Job.company_id == company_id, Job.published == True))
    jobs = q_jobs.scalars().all()
    active_roles = len(jobs)

    # candidates in flow = distinct candidates across all apps for this company's jobs
    job_ids = [j.id for j in jobs]
    if not job_ids:
        return {"active_roles": 0, "candidates_in_flow": 0, "fairness_status": "VERIFIED"}
    q_apps = await db.execute(select(Application.candidate_id).where(Application.job_id.in_(job_ids)).distinct())
    candidates_in_flow = len(q_apps.scalars().all())
    return {"active_roles": active_roles, "candidates_in_flow": candidates_in_flow, "fairness_status": "VERIFIED"}



@router.post("/{company_id}/jobs/{job_id}/run-matching")
async def run_matching(company_id: str, job_id: int, db: AsyncSession = Depends(get_db)):
    # Fetch job
    qj = await db.execute(select(Job).where(Job.id == job_id, Job.company_id == company_id))
    job = qj.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Pull verified applications
    qa = await db.execute(select(Application).where(Application.job_id == job_id))
    apps = qa.scalars().all()
    if not apps:
        return {"selected": 0, "total": 0}

    # Build a simple per-candidate match payload based on latest credential for that application
    # If external matching agent is unavailable, fall back to confidence score.
    scored = []
    for a in apps:
        qc = await db.execute(select(Credential).where(Credential.application_id == a.id).order_by(Credential.issued_at.desc()))
        cred = qc.scalars().first()
        if not cred:
            continue
            
        # Also need candidate for anon_id
        q_cand = await db.execute(select(Candidate).where(Candidate.id == a.candidate_id))
        candidate_obj = q_cand.scalar_one_or_none()
        if not candidate_obj:
            continue
            
        # Transform credential to match Matching Agent's expected format
        credential = cred.credential_json.copy()
        
        # 1. Flatten verified_skills (tiered dict) into 'skills' list for MatchNormalizer
        if "skills" not in credential and "verified_skills" in credential:
            verified_skills = credential.get("verified_skills", {})
            flat_skills = []
            
            if isinstance(verified_skills, dict):
                for tier, skills in verified_skills.items():
                    for skill in skills:
                        flat_skills.append({"skill": skill, "tier": tier})
            elif isinstance(verified_skills, list):
                flat_skills = [{"skill": s} for s in verified_skills]
                
            credential["skills"] = flat_skills
        
        # 2. Ensure identity field exists
        if "identity" not in credential:
            # Note: candidate was undefined, now using candidate_obj
            credential["identity"] = {
                "anon_id": candidate_obj.anon_id,
                "public_links": []
            }
        
        # 3. Handle failed job extraction (error object in required_skills)
        job_skills = job.required_skills
        if isinstance(job_skills, dict) and "error" in job_skills:
            logger.warning(f"Job {job.id} has extraction error, using empty requirements")
            job_skills = {
                "strict_requirements": [],
                "languages": [],
                "matching_philosophy": {"learning_velocity_weight": 0.2}
            }
        
        payload = {
            "credential": credential, 
            "job_description": {
                "title": job.title, 
                "description": job.description,
                **job_skills  # Spread the job skills into the payload
            }
        }
        try:
            logger.debug(f"Calling matching agent for app_id: {a.id}")
            res: Dict[str, Any] = await call_match_agent(payload)
            logger.debug(f"Matching agent result: {res}")
            score = int(res.get("match_score", res.get("output", {}).get("match_score", 0)) or 0)
            breakdown = res.get("breakdown") or res.get("output", {}).get("breakdown")
            analysis = res.get("analysis") or res.get("output", {}).get("analysis") or {}
        except Exception as e:
            logger.error(f"Matching agent failed for app_id {a.id}: {e}")
            score = int(cred.credential_json.get("confidence", 0))
            breakdown = None
            analysis = {}
        scored.append((a, score, breakdown, analysis))

    scored.sort(key=lambda t: t[1], reverse=True)
    k = int(job.max_participants or 5)
    selected = set(x[0].id for x in scored[:k]) # type: ignore

    for a, score, breakdown, analysis in scored:
        a.match_score = score
        # Re-map analysis to what frontend expects
        fb = {
            "breakdown": breakdown,
            "matched_skills": analysis.get("matched_skills", []),
            "missing_skills": analysis.get("missing_skills", [])
        }
        
        if a.id in selected:
            a.status = "selected"
            fb["message"] = "You are selected. The company will contact you shortly."
            a.feedback_json = fb
        else:
            a.status = "rejected"
            fb["message"] = "Not selected this time. Here is developmental feedback."
            a.feedback_json = fb

    await db.commit()
    return {"selected": len(selected), "total": len(scored)}


@router.get("/{company_id}/jobs/{job_id}/selected")
async def list_selected(company_id: str, job_id: int, db: AsyncSession = Depends(get_db)):
    qj = await db.execute(select(Job).where(Job.id == job_id, Job.company_id == company_id))
    job = qj.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    q = await db.execute(
        select(Application, Candidate)
        .join(Candidate, Application.candidate_id == Candidate.id)
        .where(Application.job_id == job_id, Application.status == "selected")
        .order_by(Application.match_score.desc().nullslast())
    )
    rows = q.all()
    return [{"anon_id": cand.anon_id, "match_score": app.match_score or 0, "breakdown": (app.feedback_json or {}).get("breakdown")} for app, cand in rows]



@router.get("/{company_id}/jobs/{job_id}/applications")
async def list_job_applications(company_id: str, job_id: int, db: AsyncSession = Depends(get_db)):
    # Verify job belongs to company
    qj = await db.execute(select(Job).where(Job.id == job_id, Job.company_id == company_id))
    job = qj.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    q = await db.execute(
        select(Application, Candidate)
        .join(Candidate, Application.candidate_id == Candidate.id)
        .where(Application.job_id == job_id)
        .order_by(Application.created_at.desc())
    )
    rows = q.all()
    return [
        {
            "application_id": app.id,
            "anon_id": cand.anon_id,
            "status": app.status,
            "match_score": app.match_score,
            "feedback": app.feedback_json,
            "created_at": app.created_at.isoformat() if app.created_at else None,
            "candidate_details": {
                "name": cand.name,
                "email": cand.email,
                "college": cand.college
            }
        }
        for app, cand in rows
    ]


@router.get("/{company_id}/review-queue")
async def review_queue(company_id: str, db: AsyncSession = Depends(get_db)):
    # company sees review cases for jobs they own
    q = await db.execute(
        select(ReviewCase, Candidate, Application, Job)
        .join(Application, ReviewCase.application_id == Application.id)
        .join(Job, Application.job_id == Job.id)
        .join(Candidate, ReviewCase.candidate_id == Candidate.id)
        .where(Job.company_id == company_id, ReviewCase.status == "pending")
        .order_by(ReviewCase.created_at.desc())
    )
    rows = q.all()
    out = []
    for rc, cand, app, job in rows:
        # Fetch credential for enriched evidence data
        cred_q = await db.execute(
            select(Credential)
            .where(Credential.application_id == rc.application_id)
            .order_by(Credential.issued_at.desc())
        )
        cred = cred_q.scalars().first()
        cred_json = cred.credential_json if cred else {}

        # Extract verified skills from credential
        derived = cred_json.get("derived", {}) if isinstance(cred_json, dict) else {}
        verified_skills = derived.get("verified_skills", {})
        
        # Flatten skills for display
        flat_skills = []
        if isinstance(verified_skills, dict):
            for tier, skills in verified_skills.items():
                for s in skills:
                    name = s.get("name", s) if isinstance(s, dict) else s
                    flat_skills.append(name)
        elif isinstance(verified_skills, list):
            flat_skills = [s.get("name", s) if isinstance(s, dict) else s for s in verified_skills]

        # Extract evidence signals from credential
        evidence_data = cred_json.get("evidence", {}) if isinstance(cred_json, dict) else {}
        evidence_sources = [str(k).upper() for k in evidence_data.keys() if evidence_data.get(k)]

        out.append({
            "id": rc.id,
            "application_id": rc.application_id,
            "job_id": rc.job_id,
            "role": job.title,
            "candidate_anon_id": cand.anon_id,
            "candidate_name": cand.name,
            "candidate_email": cand.email,
            "severity": rc.severity,
            "reason": rc.reason,
            "status": rc.status,
            "created_at": rc.created_at.isoformat(),
            "triggered_by": rc.triggered_by,
            "evidence_json": rc.evidence,
            "skills": flat_skills,
            "evidence_sources": evidence_sources,
            "confidence": derived.get("confidence", 0),
            "match_score": derived.get("match_score", 0),
            "feedback": app.feedback_json,
        })
    return out


@router.post("/{company_id}/review-queue/{case_id}/action")
async def review_action(company_id: str, case_id: int, payload: dict, db: AsyncSession = Depends(get_db)):
    action = payload.get("action")
    note = payload.get("note") or ""

    q = await db.execute(select(ReviewCase).where(ReviewCase.id == case_id))
    rc = q.scalar_one_or_none()
    if not rc:
        raise HTTPException(status_code=404, detail="Case not found")

    # Ensure case belongs to this company via job ownership
    qj = await db.execute(select(Job).where(Job.id == rc.job_id, Job.company_id == company_id))
    if not qj.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not allowed")

    if action == "clear":
        rc.status = "cleared"
        # Mark application as verified so it can proceed
        qa = await db.execute(select(Application).where(Application.id == rc.application_id))
        app = qa.scalar_one_or_none()
        if app and app.status == "needs_review":
            app.status = "verified"
    elif action == "blacklist":
        rc.status = "blacklisted"
        # Add to blacklist and reject application
        qa = await db.execute(select(Application).where(Application.id == rc.application_id))
        app = qa.scalar_one_or_none()
        if app:
            app.status = "rejected"
        qb = await db.execute(select(Blacklist).where(Blacklist.candidate_id == rc.candidate_id))
        if not qb.scalar_one_or_none():
            db.add(Blacklist(candidate_id=rc.candidate_id, reason=note or rc.reason))
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use clear|blacklist")

    await db.commit()
    await log_event(db, "company", "review_action", {"case_id": case_id, "action": action})
    return {"ok": True}


@router.get("/reviewer/queue")
async def global_review_queue(db: AsyncSession = Depends(get_db)):
    """Global review queue for the reviewer role — returns all pending cases across all companies."""
    q = await db.execute(
        select(ReviewCase, Candidate, Application, Job)
        .join(Application, ReviewCase.application_id == Application.id)
        .join(Job, Application.job_id == Job.id)
        .join(Candidate, ReviewCase.candidate_id == Candidate.id)
        .where(ReviewCase.status == "pending")
        .order_by(ReviewCase.created_at.desc())
    )
    rows = q.all()
    out = []
    for rc, cand, app, job in rows:
        cred_q = await db.execute(
            select(Credential)
            .where(Credential.application_id == rc.application_id)
            .order_by(Credential.issued_at.desc())
        )
        cred = cred_q.scalars().first()
        cred_json = cred.credential_json if cred else {}

        derived = cred_json.get("derived", {}) if isinstance(cred_json, dict) else {}
        verified_skills = derived.get("verified_skills", {})

        flat_skills = []
        if isinstance(verified_skills, dict):
            for tier, skills in verified_skills.items():
                for s in skills:
                    name = s.get("name", s) if isinstance(s, dict) else s
                    flat_skills.append(name)
        elif isinstance(verified_skills, list):
            flat_skills = [s.get("name", s) if isinstance(s, dict) else s for s in verified_skills]

        evidence_data = cred_json.get("evidence", {}) if isinstance(cred_json, dict) else {}
        evidence_sources = [str(k).upper() for k in evidence_data.keys() if evidence_data.get(k)]

        # Build fraud flags list from ATS evidence for display
        ats_evidence = rc.evidence or {}
        fraud_flags = ats_evidence.get("flags", []) + ats_evidence.get("manipulation_signals", {}).get("patterns", []) if isinstance(ats_evidence, dict) else []

        out.append({
            "id": rc.id,
            "application_id": rc.application_id,
            "job_id": rc.job_id,
            "role": job.title,
            "company_name": job.company_id,
            "candidate_anon_id": cand.anon_id,
            "candidate_name": cand.name,
            "candidate_email": cand.email,
            "severity": rc.severity,
            "reason": rc.reason,
            "status": rc.status,
            "created_at": rc.created_at.isoformat(),
            "triggered_by": rc.triggered_by,
            "evidence_json": rc.evidence,
            "fraud_flags": list(set(fraud_flags)),
            "skills": flat_skills,
            "evidence_sources": evidence_sources,
            "confidence": derived.get("confidence", 0),
            "match_score": derived.get("match_score", 0),
            "feedback": app.feedback_json,
        })
    return out


@router.post("/reviewer/queue/{case_id}/action")
async def global_review_action(case_id: int, payload: dict, db: AsyncSession = Depends(get_db)):
    """Reviewer action on any case — no company scoping needed."""
    action = payload.get("action")
    note = payload.get("note") or ""

    q = await db.execute(select(ReviewCase).where(ReviewCase.id == case_id))
    rc = q.scalar_one_or_none()
    if not rc:
        raise HTTPException(status_code=404, detail="Case not found")

    if action == "clear":
        rc.status = "cleared"
        qa = await db.execute(select(Application).where(Application.id == rc.application_id))
        app = qa.scalar_one_or_none()
        if app and app.status == "needs_review":
            app.status = "verified"
    elif action == "blacklist":
        rc.status = "blacklisted"
        qa = await db.execute(select(Application).where(Application.id == rc.application_id))
        app = qa.scalar_one_or_none()
        if app:
            app.status = "rejected"
        qb = await db.execute(select(Blacklist).where(Blacklist.candidate_id == rc.candidate_id))
        if not qb.scalar_one_or_none():
            db.add(Blacklist(candidate_id=rc.candidate_id, reason=note or rc.reason))
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use clear|blacklist")

    await db.commit()
    return {"ok": True}
