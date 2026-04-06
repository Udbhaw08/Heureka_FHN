# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Fair Hiring Network (FHN)** — an AI-driven recruitment platform that verifies candidate skills via 9 specialized agents, detects bias in job descriptions, and produces cryptographically signed skill passports for evidence-based hiring.

Stack: React 18 + Vite (frontend) | FastAPI + SQLAlchemy async + PostgreSQL (backend) | Zynd SDK (agent orchestration) | Google Gemini + Ollama (LLM)

---

## Development Commands

### Frontend
```powershell
cd fair-hiring-frontend
npm install
npm run dev      # Dev server on http://localhost:5173
npm run build    # Production build
```

### Backend
```powershell
cd backend

# Virtual environment
python -m venv .venv
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Database setup
python init_db.py           # Create + migrate tables

# Run dev server (port 8012 by default from start_demo.ps1)
$env:PYTHONPATH = "$PWD;$PWD\.."
python -m uvicorn app.main:app --reload --port 8012 --log-level info
```

### Full Demo (all services)
```powershell
.\start_demo.ps1   # Starts backend (8012) + 8 Zynd agents (5101-5109) in separate windows
# Then separately: cd fair-hiring-frontend && npm run dev
```

---

## Architecture

### Dual-Layer Agent System (Critical Concept)

There are **two parallel agent implementations** that serve the same 9 agent roles:

| Layer | Location | How It Runs | Port Range |
|-------|----------|-------------|------------|
| **Zynd Agents** | `zynd_integration/agents/*.py` | `start_demo.ps1` via `python -m zynd_integration.agents.<name>` | 5101–5109 |
| **Service Agents** | `agents_services/*.py` | Standalone FastAPI processes | 8001–8011 |

The `USE_ZYND` env var controls routing:
- `USE_ZYND=1` → `agent_client.py` uses `ZyndOrchestrator` to discover and call agents via `/webhook/sync`
- `USE_ZYND=0` → Direct HTTP calls to service agent ports

Zynd agents use `ZyndAIAgent` from `zyndai_agent` SDK, register with the Zynd registry, and communicate via synchronous webhooks (`/webhook/sync`). The Zynd orchestrator (`backend/app/zynd_orchestrator.py`) has a **local-first discovery fallback** — it maps capabilities to local ports before querying the remote registry, so local dev works without Zynd network access.

### 10-Stage Pipeline

The `PipelineOrchestrator` (`backend/app/services/pipeline_orchestrator.py`) executes these stages sequentially for each application. State is persisted after every stage to the `Credential` table (resume-able on restart).

| # | Stage | Agent | Endpoint Called | Gate Condition |
|---|-------|-------|-----------------|----------------|
| 1 | ATS | `ats` | `/webhook/sync` | `action == "BLACKLIST"` stops pipeline entirely |
| 2 | GitHub | `github` | `/scrape` | Skipped if no `github_url` |
| 3 | LeetCode | `leetcode` | `/scrape` | Skipped if no `leetcode_url` |
| 4 | Codeforces | `codeforces` | `/scrape` | Skipped if no `codeforces_url` |
| 5 | LinkedIn | `linkedin` | `/parse` | Skipped if no `linkedin_pdf_path` |
| 6 | Skills | `skill` | `/run` | Core skill extraction from aggregated evidence |
| 7 | Matching | `matching` | `/run` | Evidence-based match score against job |
| 8 | Bias | `bias` | `/run` | Fairness audit |
| 9 | Passport | `passport` | `/issue` | Generates Ed25519-signed credential |
| 10 | Persist | — | DB write | Credential saved to `credentials` table |

**Security gate**: If ATS returns `action == "BLACKLIST"`, the pipeline stops immediately and the candidate is blacklisted. If `action == "NEEDS_REVIEW"`, the pipeline pauses and creates a `ReviewCase`.

### Backend Structure (`backend/app/`)

```
main.py                  # FastAPI app, CORS (allow_all for dev), lifespan (DB init + Zynd init)
config.py                # Pydantic Settings — all env vars, agent URLs, Ed25519 keys
database.py              # asyncpg connection, get_db() dependency
agent_client.py          # Unified agent caller — handles Zynd vs direct HTTP routing
zynd_orchestrator.py     # Zynd SDK client — discover() + call_sync(), local-first fallback
passport.py              # Ed25519 sign/verify: sha256_hex + Ed25519PrivateKey.sign()

routers/
  auth.py                # /api/auth/candidate/{signup,login} | /api/auth/company/{signup,login}
  candidate.py           # /api/candidate/profile | /api/candidate/stats | /api/candidate/applications | /api/candidate/passport
  company.py             # /api/company/profile | /api/company/jobs | /api/company/review-queue | /api/company/review
  job.py                 # /api/jobs | /api/jobs/{id} | /api/jobs/analyze (bias analysis)
  application.py         # /api/applications | /api/applications/{id}/status | /api/applications/{id}/results
  pipeline.py            # /api/pipeline/run | /api/pipeline/status/{id} | /api/pipeline/credential/{id}
  passport.py            # /api/passport/{candidate_id} | /api/passport/verify
  candidate_public.py    # Public endpoints (no auth)

services/
  pipeline_service.py     # High-level: fetches app, calls orchestrator, stores results
  pipeline_orchestrator.py # Executes 10 stages, logs to AgentRun, persists Credential state

models_new.py            # SQLAlchemy declarative models: Company, Candidate, Job, Application,
                          #   Credential, AgentRun, ReviewCase, Blacklist
```

### Frontend Routes (`fair-hiring-frontend/src/App.jsx`)

| Route | Component | Auth Guard |
|-------|-----------|------------|
| `/` | Landing page (Hero, Vision, Capabilities, Studio, Contact) | None |
| `/company` | CompanyAuth → CompanyHiringFlow → CompanyDashboard → CompanyRolePipeline → CompanyCandidateReview | `localStorage.fhn_company_id` |
| `/candidate` | CandidateAuth → CandidateExperience | `localStorage.fhn_candidate_anon_id` |
| `/reviewer` | ReviewerExperience | None |
| `/candidate/interview` | ProtocallApp (AI interview with Gemini + ElevenLabs) | — |
| `/passport/:id` | SkillPassport (public, standalone) | None |
| `/system-flow` | SystemFlow | None |

Frontend uses React Router v7, lazy-loaded components, Lenis smooth scroll, GSAP custom cursor, and Auth0 for identity.

### Database Tables

- **companies** — `id, name, email, password_hash`
- **candidates** — `id, anon_id, email, name, gender, college, engineer_level`
- **jobs** — `id, company_id, title, description, required_skills (JSON), fairness_score, fairness_status, published`
- **applications** — `id, candidate_id, job_id, resume_text, github_url, leetcode_url, codeforces_url, status, pipeline_status, match_score`
- **credentials** — `id, candidate_id, application_id, credential_json, hash_sha256, signature_b64, issued_at` (this is the pipeline state AND the final passport)
- **agent_runs** — `id, application_id, agent_name, input_payload, output_payload, status, execution_time_ms`
- **review_cases** — `id, application_id, triggered_by, severity, reason, evidence, status`
- **blacklist** — `id, candidate_id, reason, blacklisted_by_company_id`

### Credential Signing (Ed25519)

Credentials are signed in `backend/app/passport.py`:
1. Canonical JSON of `credential_json` (sorted keys, no whitespace)
2. SHA-256 hash of the bytes
3. Ed25519 signature using the private key from `SIGNING_PRIVATE_KEY_B64`
4. Both `hash_sha256` and `signature_b64` stored in the `credentials` table

Verification inverts the process. The same private key pair is referenced in `config.py`.

---

## Key Patterns

### Agent Response Wrapping

`agent_client.py` wraps all responses: `{success: bool, data: dict, status_code: int}`. The pipeline orchestrator reads from `.data` field. **Exception**: Zynd mode returns the raw parsed response directly.

### Schema Adaptation in `agent_client.run_full_pipeline()`

The method does runtime normalization because agent versions output different shapes:
- Flattens `verified_skills` tiered dict (`{tier: [skills]}`) into `[{skill, tier}]` for the matching agent
- Injects `identity` block with `anon_id` and `public_links` into the credential
- Adds boolean flags (`ats`, `github`, `leetcode`, etc.) based on agent call success

### Resume Path Convention

Pipeline service reconstructs resume path deterministically: `backend/data/resumes/{anon_id}_{job_id}.pdf`. Same pattern for LinkedIn: `backend/data/linkedin/{anon_id}_{job_id}.pdf`. Files are optional — pipeline continues with `resume_text` if PDF not found.

### `required_skills` Can Be Dict or List

`Job.required_skills` is a JSON column. Older code stores it as a list of strings; newer code stores it as a dict with keys like `languages`, `frameworks`, `matching_philosophy`. `pipeline_service._prepare_job_data()` handles both.

### Duplicate Exception Handler

`pipeline_service.py` has a duplicate `except Exception` block (lines 106–118 appear to be dead code after the first one at 98). When debugging pipeline failures, check the first handler's logic first.

### Environment Variable Loading

`backend/app/main.py` loads `.env` from the **project root** (`BASE_DIR = backend/app/../../.env`), not from `backend/`. The `PYTHONPATH` must include both `backend/` and the repo root for imports like `zynd_integration` to resolve.

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/fhn

# Signing keys (Ed25519, base64 raw 32 bytes)
SIGNING_PRIVATE_KEY_B64=<base64>
SIGNING_PUBLIC_KEY_B64=<base64>

# Routing
USE_ZYND=1                        # 1 = Zynd agents, 0 = direct HTTP
ZYND_API_KEY=<key>
ZYND_REGISTRY_URL=https://registry.zynd.ai
ZYND_WEBHOOK_HOST=127.0.0.1
ORCH_ZYND_PORT=5100               # Backend's Zynd orchestrator port

# Zynd agent ports (used by orchestrator's local discovery)
MATCHING_ZYND_PORT=5101
BIAS_ZYND_PORT=5102
SKILL_ZYND_PORT=5103
ATS_ZYND_PORT=5104
PASSPORT_ZYND_PORT=5105
GITHUB_ZYND_PORT=5106
LINKEDIN_ZYND_PORT=5107
LEETCODE_ZYND_PORT=5108
CODEFORCES_ZYND_PORT=5109

# Agent credential paths (relative to repo root)
ORCH_ZYND_VC=credentials/orchestrator_vc.json
MATCHING_ZYND_VC=credentials/matching_vc.json
# ... (same pattern for each agent)

# Agent service URLs (direct HTTP fallback)
MATCHING_SERVICE_URL=http://localhost:5101
BIAS_SERVICE_URL=http://localhost:5102
SKILL_SERVICE_URL=http://localhost:5103
ATS_SERVICE_URL=http://localhost:5104
PASSPORT_SERVICE_URL=http://localhost:8012
GITHUB_SERVICE_URL=http://localhost:5106
LINKEDIN_SERVICE_URL=http://localhost:5107
LEETCODE_SERVICE_URL=http://localhost:5108
CODEFORCES_SERVICE_URL=http://localhost:5109
```
