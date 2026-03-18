# Fair Hiring Network - Backend

**FastAPI-powered backend for AI-driven recruitment with Zynd agent orchestration**

---

## Overview

The FHN backend is a FastAPI application that orchestrates the 9 Zynd agents for candidate verification, bias detection, and evidence-based matching. It provides RESTful APIs for candidate management, company operations, job postings, and the complete hiring pipeline.

### Key Capabilities

- **RESTful API** - Full CRUD operations for candidates, companies, jobs, and applications
- **Pipeline Orchestration** - 10-stage agent pipeline for comprehensive candidate evaluation
- **Zynd Integration** - Agent discovery and synchronous communication via Zynd SDK
- **Async Architecture** - High-concurrency async/await patterns
- **Database Abstraction** - SQLAlchemy with asyncpg for PostgreSQL

---

## Architecture

### Backend Architecture (ASCII)

```
+-----------------------------------------------------------------------------+
|                              BACKEND SERVICE LAYER                           |
+-----------------------------------------------------------------------------+
|                                                                             |
|  +----------------------------------------------------------------------+   |
|  |                        FASTAPI APPLICATION (main.py)              |   |
|  |  +-------------+-------------+-------------+-------------+------+ |   |
|  |  |   CORS      |  Lifecycle  |  Exception  |   Health    | Docs | |   |
|  |  |   Config    |   Manager   |  Handlers   |   Check    |(Swagger)| |   |
|  |  +-------------+-------------+-------------+-------------+------+ |   |
|  +----------------------------------------------------------------------+   |
|                                        |                                      |
|  +--------------------------------------+------------------------------------+  |
|  |                                      ▼                                    |  |
|  |  +----------------------------------------------------------------------+ |  |
|  |  |                          API ROUTERS                               | |  |
|  |  |  +---------+ +---------+ +---------+ +---------+ +--------+        | |  |
|  |  |  |  auth   | |candidate| | company | |   job   | |  app   |        | |  |
|  |  |  | /auth   | |/candidate| |/company | |  /job   | |/app     |        | |  |
|  |  |  +----+----+ +----+----+ +----+----+ +----+----+ +----+---+        | |  |
|  |  |       |          |          |          |          |     |          | |  |
|  |  |  +----+----+ +----+----+ +----+----+ +----+----+ +----+---+        | |  |
|  |  |  |pipeline| | passport| |candidate| | health  | |  agent |        | |  |
|  |  |  |/pipeline||/passport||_public   | | /health | | /agent  |        | |  |
|  |  |  +---------+ +---------+ +---------+ +---------+ +--------+        | |  |
|  |  +----------------------------------------------------------------------+ |  |
|  +----------------------------------------------------------------------------+  |
|                                        |                                       |
|  +--------------------------------------+------------------------------------+  |
|  |                                      ▼                                    |  |
|  |  +----------------------------------------------------------------------+ |  |
|  |  |                       SERVICES LAYER                               | |  |
|  |  |  +------------------------+  +---------------------------+          | |  |
|  |  |  |    PipelineService    |  |  PipelineOrchestrator    |          | |  |
|  |  |  |    High-level ops      |  |    10-stage execution   |          | |  |
|  |  |  +------------------------+  +---------------------------+          | |  |
|  |  +----------------------------------------------------------------------+ |  |
|  +----------------------------------------------------------------------------+  |
|                                        |                                       |
|  +--------------------------------------+------------------------------------+  |
|  |                                      ▼                                    |  |
|  |  +----------------------------------------------------------------------+ |  |
|  |  |                    AGENT COMMUNICATION                             | |  |
|  |  |  +------------------------+  +---------------------------+          | |  |
|  |  |  |      AgentClient       |  |    ZyndOrchestrator      |          | |  |
|  |  |  |      Direct HTTP       |  |    Agent Discovery       |          | |  |
|  |  |  |      Retry + Timeout   |  |    Capability Mapping   |          | |  |
|  |  |  +------------------------+  +---------------------------+          | |  |
|  |  +----------------------------------------------------------------------+ |  |
|  +----------------------------------------------------------------------------+  |
|                                        |                                       |
|  +--------------------------------------+------------------------------------+  |
|  |                                      ▼                                    |  |
|  |  +----------------------------------------------------------------------+ |  |
|  |  |                      DATA ACCESS LAYER                             | |  |
|  |  |  +-------------+  +-------------+  +-------------+                 | |  |
|  |  |  |   Config    |  |   Database  |  |   Models    |                 | |  |
|  |  |  |  .env vars  |  |   asyncpg    |  |  SQLAlchemy |                 | |  |
|  |  |  +-------------+  +-------------+  +-------------+                 | |  |
|  |  +----------------------------------------------------------------------+ |  |
|  +----------------------------------------------------------------------------+  |
+-------------------------------------------------------------------------------+
                                        |
                                        v
                             +-------------------+
                             |    PostgreSQL     |
                             |    (Port 5432)    |
                             +-------------------+
```

### Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── models_new.py           # SQLAlchemy models
│   ├── schemas_new.py          # Pydantic schemas
│   ├── agent_client.py         # Agent HTTP client
│   ├── zynd_orchestrator.py    # Zynd SDK integration
│   │
│   ├── agents/                 # Local agent implementations
│   │   ├── __init__.py
│   │   ├── jd_bias.py          # Job description bias detection
│   │   └── job_extraction.py  # Job description intelligence
│   │
│   ├── routers/                # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── candidate.py       # Candidate management
│   │   ├── candidate_public.py# Public candidate endpoints
│   │   ├── company.py         # Company management
│   │   ├── job.py             # Job postings
│   │   ├── application.py     # Application processing
│   │   ├── pipeline.py        # Pipeline execution
│   │   ├── passport.py        # Skill passport
│   │   ├── agent.py           # Agent orchestration
│   │   └── health.py          # Health check
│   │
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── pipeline_service.py     # High-level pipeline
│   │   └── pipeline_orchestrator.py # Stage execution
│   │
│   └── utils/                 # Utilities
│       ├── __init__.py
│       └── ...
│
├── alembic/                   # Database migrations
├── data/                      # Sample data
├── requirements.txt           # Python dependencies
├── create_database.py         # DB creation script
├── init_db.py                 # DB initialization
├── seed_db.py                 # Seed data script
└── README.md                  # This file
```

---

## API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/candidate/signup` | Register candidate |
| POST | `/api/auth/candidate/login` | Candidate login |
| POST | `/api/auth/company/signup` | Register company |
| POST | `/api/auth/company/login` | Company login |
| POST | `/api/auth/sync` | Sync Auth0 user to backend |

### Candidates (`/api/candidate`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/candidate/profile` | Get candidate profile |
| PUT | `/api/candidate/profile` | Update candidate profile |
| GET | `/api/candidate/stats` | Get candidate statistics |
| GET | `/api/candidate/applications` | List applications |
| GET | `/api/candidate/passport` | Get skill passport |

### Companies (`/api/company`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/company/profile` | Get company profile |
| PUT | `/api/company/profile` | Update company profile |
| GET | `/api/company/stats` | Get company statistics |
| GET | `/api/company/jobs` | List company jobs |
| POST | `/api/company/review` | Review candidate |
| GET | `/api/company/review-queue` | Get review queue |

### Jobs (`/api/jobs`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs` | List published jobs |
| GET | `/api/jobs/{id}` | Get job details |
| POST | `/api/jobs` | Create job posting |
| PUT | `/api/jobs/{id}` | Update job |
| DELETE | `/api/jobs/{id}` | Delete job |
| POST | `/api/jobs/analyze` | Analyze job for bias |

### Applications (`/api/applications`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/applications` | Submit application |
| GET | `/api/applications/{id}` | Get application |
| GET | `/api/applications/job/{job_id}` | List job applications |
| PUT | `/api/applications/{id}/status` | Update status |
| GET | `/api/applications/{id}/results` | Get agent results |

### Pipeline (`/api/pipeline`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/pipeline/run` | Run pipeline for application |
| GET | `/api/pipeline/status/{app_id}` | Get pipeline status |
| GET | `/api/pipeline/credential/{app_id}` | Get credential |
| GET | `/api/pipeline/history/{app_id}` | Get pipeline history |

### Passport (`/api/passport`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/passport/{candidate_id}` | Get passport |
| POST | `/api/passport/verify` | Verify passport signature |

### Health (`/health`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

---

## Database Schema

### Entity Relationship Diagram (ASCII)

```
+------------------+         +------------------+
|    companies     |         |   candidates     |
+------------------+         +------------------+
| id (PK)          |         | id (PK)          |
| email            |         | anon_id          |
| password_hash    |         | email            |
| company_name     |         | gender           |
| created_at       |         | college          |
| updated_at       |         | engineer_level   |
+--------+---------+         | auth0_id         |
         |                   | created_at       |
         |                   +--------+---------+
         |                            |
         |                            |
         v                            v
+------------------         +------------------+
|      jobs        |         |  applications    |
+------------------+         +------------------+
| id (PK)          |         | id (PK)          |
| company_id (FK)  |---------| job_id (FK)      |
| title            |         | candidate_id (FK)|
| description      |         | status           |
| required_skills  |         | resume_url       |
| fairness_score   |         | pipeline_status  |
| seniority        |         | match_score      |
| created_at       |         | created_at       |
+--------+---------+         +--------+---------+
         |                            |
         |                            v
         |                   +------------------+
         |                   |    credentials    |
         |                   +------------------+
         |                   | id (PK)          |
         |                   | application_id   |
         |                   | skill_graph (JSON)|
         |                   | hash_sha256      |
         |                   | signature_b64    |
         |                   | created_at       |
         |                   +--------+---------+
         |                            |
         v                            v
+------------------+         +------------------+
|   agent_runs     |         |   review_cases   |
+------------------+         +------------------+
| id (PK)          |         | id (PK)          |
| application_id  |         | application_id   |
| agent_name       |         | severity         |
| input_payload    |         | reason           |
| output_payload   |         | status           |
| status           |         | reviewed_by      |
| duration_ms      |         | created_at       |
| created_at       |         +------------------+
+------------------+
```

### Table Details

| Table | Description | Key Fields |
|-------|-------------|-------------|
| `companies` | Employer accounts | email, password_hash, company_name |
| `candidates` | Job seeker profiles | anon_id, gender, college, engineer_level |
| `jobs` | Job postings | company_id, title, required_skills, fairness_score |
| `applications` | Applications | job_id, candidate_id, status, pipeline_status |
| `credentials` | Skill passports | application_id, skill_graph, hash_sha256, signature_b64 |
| `agent_runs` | Agent execution logs | agent_name, input_payload, output_payload, duration_ms |
| `review_cases` | Human review queue | application_id, severity, reason, status |

---

## Agent Services

| # | Service | Port | Purpose |
|---|---------|------|---------|
| 1 | ATS Agent | 8004 | Resume fraud detection, blacklist checking |
| 2 | Skill Agent | 8003 | Skill extraction and verification |
| 3 | GitHub Agent | 8005 | Code repository analysis |
| 4 | Bias Agent | 8002 | Bias detection in job descriptions |
| 5 | Matching Agent | 8001 | Candidate-job matching |
| 6 | Passport Agent | 8008 | Credential generation and signing |
| 7 | LinkedIn Agent | 8007 | Professional history verification |
| 8 | LeetCode Agent | 8006 | Algorithm problem-solving verification |
| 9 | Codeforces Agent | 8011 | Competitive programming verification |

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql+asyncpg://user:pass@localhost:5432/fhn` |
| `PORT` | Backend server port | `8010` |
| `USE_ZYND` | Enable Zynd orchestration | `0` |
| `ZYND_API_KEY` | Zynd API key | - |
| `ZYND_WEBHOOK_HOST` | Zynd webhook host | `http://localhost:5100` |
| `POSTGRES_USER` | DB username | `postgres` |
| `POSTGRES_PASSWORD` | DB password | - |
| `POSTGRES_HOST` | DB host | `localhost` |
| `POSTGRES_PORT` | DB port | `5432` |
| `POSTGRES_DB` | Database name | `fhn` |

### Agent URLs

| Agent | Environment Variable | Default |
|-------|---------------------|---------|
| Matching | `MATCHING_AGENT_URL` | `http://localhost:8001` |
| Bias | `BIAS_AGENT_URL` | `http://localhost:8002` |
| Skill | `SKILL_AGENT_URL` | `http://localhost:8003` |
| ATS | `ATS_AGENT_URL` | `http://localhost:8004` |
| GitHub | `GITHUB_AGENT_URL` | `http://localhost:8005` |
| LeetCode | `LEETCODE_AGENT_URL` | `http://localhost:8006` |
| Codeforces | `CODEFORCES_AGENT_URL` | `http://localhost:8011` |
| LinkedIn | `LINKEDIN_AGENT_URL` | `http://localhost:8007` |
| Passport | `PASSPORT_AGENT_URL` | `http://localhost:8008` |

---

## Pipeline Orchestration

### 10-Stage Pipeline Flow

```
+-------------------------------------------------------------------------------+
|                           PIPELINE ORCHESTRATION                              |
+-------------------------------------------------------------------------------+

Stage 1: ATS Agent (Resume Fraud Detection)
+---------------------------------------------------------------------------+
|  Input: resume_url, candidate_data                                        |
|  Output: {fraud_score, blacklist_match, policy_gating}                    |
|  Checks: Resume authenticity, blacklist database, policy compliance       |
+---------------------------------------------------------------------------+
                                    |
Stage 2: GitHub Agent (Code Repository Analysis)
+---------------------------------------------------------------------------+
|  Input: github_username                                                    |
|  Output: {repo_count, stars, forks, language_skills, contribution_score}  |
|  Checks: Code quality, activity, language diversity                       |
+---------------------------------------------------------------------------+
                                    |
Stage 3: LeetCode Agent (Algorithm Skills)
+---------------------------------------------------------------------------+
|  Input: leetcode_username                                                  |
|  Output: {problems_solved, easy/medium/hard, rating, percentile}          |
|  Checks: Problem-solving ability, algorithm knowledge                     |
+---------------------------------------------------------------------------+
                                    |
Stage 4: Codeforces Agent (Competitive Programming)
+---------------------------------------------------------------------------+
|  Input: codeforces_username                                               |
|  Output: {rating, max_rating, contests, problems_solved}                  |
|  Checks: Competitive programming skills, contest participation            |
+---------------------------------------------------------------------------+
                                    |
Stage 5: LinkedIn Agent (Professional History)
+---------------------------------------------------------------------------+
|  Input: linkedin_url                                                      |
|  Output: {verified, job_history, education, skills, endorsements}        |
|  Checks: Profile authenticity, work history, skills                        |
+---------------------------------------------------------------------------+
                                    |
Stage 6: Skill Agent (Skill Extraction)
+---------------------------------------------------------------------------+
|  Input: resume_text, profile_data                                         |
|  Output: {skills: [], confidence_scores: {}, evidence_sources: []}         |
|  Extraction: Skills taxonomy from all sources                             |
+---------------------------------------------------------------------------+
                                    |
Stage 7: Test Agent (Practical Skills)
+---------------------------------------------------------------------------+
|  Input: skill_areas                                                       |
|  Output: {test_scores: {}, time_taken: {}, anti_cheat: {}}               |
|  Verification: Hands-on skills testing                                    |
+---------------------------------------------------------------------------+
                                    |
Stage 8: Bias Agent (Fairness Audit)
+---------------------------------------------------------------------------+
|  Input: job_description, company_profile                                  |
|  Output: {bias_score: {}, flagged_terms: [], fairness_eligibility}        |
|  Checks: Gender, college, demographic biases                              |
+---------------------------------------------------------------------------+
                                    |
Stage 9: Matching Agent (Evidence-Based Matching)
+---------------------------------------------------------------------------+
|  Input: candidate_profile, job_requirements                               |
|  Output: {match_score: {}, evidence_weights: {}, recommendations: []}     |
|  Scoring: Evidence-based, not resume-based                                |
+---------------------------------------------------------------------------+
                                    |
Stage 10: Passport Agent (Credential Generation)
+---------------------------------------------------------------------------+
|  Input: all_agent_outputs                                                 |
|  Output: {credential_id, skill_graph, hash_sha256, signature_b64}         |
|  Signing: Cryptographic credential with verified skills                   |
+---------------------------------------------------------------------------+
```

---

## Agent Communication

### AgentClient Architecture

```
+-------------------------------------------------------------------------------+
|                              AGENT CLIENT LAYER                              |
+-------------------------------------------------------------------------------+

   +---------------------------------------------------------------------+
   |                         AgentClient                                 |
   |  +-----------------------------------------------------------------+ |
   |  |                      call_agent()                             | |
   |  |                                                                 | |
   |  |  1. Validate capability                                        | |
   |  |  2. Select transport (Direct HTTP / Zynd)                    | |
   |  |  3. Build request (method, url, body, timeout)                | |
   |  |  4. Execute with retry (3 attempts, exponential backoff)     | |
   |  |  5. Parse response                                            | |
   |  |  6. Return result or raise exception                         | |
   |  +-----------------------------------------------------------------+ |
   +---------------------------------------------------------------------+
                    |                                         |
                    v                                         v
   +---------------------------+       +-----------------------------------+
   |     DIRECT HTTP MODE      |       |       ZYND MODE                  |
   |                           |       |                                   |
   |  agent_client.py         |       |  zynd_orchestrator.py             |
   |                           |       |                                   |
   |  http://localhost:{port} |       |  1. search_agents_by_capability   |
   |  /webhook/sync           |       |  2. discover target agent          |
   |                           |       |  3. call /webhook/sync            |
   |  Timeout: 500ms          |       |  4. return JSON response          |
   |  Retry: 3x              |       |                                   |
   +---------------------------+       +-----------------------------------+
```

### Capability Mapping

| Capability | Zynd Tags |
|------------|-----------|
| Matching | `["fair_hiring", "matching"]` |
| Bias Detection | `["fair_hiring", "bias_detection"]` |
| Skill Verification | `["fair_hiring", "skill_verification"]` |
| ATS | `["fair_hiring", "ats"]` |
| Passport | `["fair_hiring", "passport"]` |

---

## Running the Backend

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Node.js 18+ (for frontend)

### Development

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate   # Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**:
   ```bash
   python init_db.py
   # or
   python create_database.py
   ```

5. **Start backend**:
   ```bash
   uvicorn app.main:app --reload --port 8010
   # or
   python start_backend.ps1
   ```

### Production

1. **Build**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run with gunicorn**:
   ```bash
   gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8010 app.main:app
   ```

3. **Or use Docker** (create Dockerfile if needed)

The API will be available at:
- API: http://localhost:8010
- Swagger Docs: http://localhost:8010/docs
- ReDoc: http://localhost:8010/redoc

---

## Testing

### Health Check
```bash
curl http://localhost:8010/health
```

### Run Pipeline Test
```bash
# Create a test application, then run:
curl -X POST http://localhost:8010/api/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"application_id": "<app_id>"}'
```

### Manual Testing with Swagger
1. Open http://localhost:8010/docs
2. Register a candidate via `/api/auth/candidate/signup`
3. Create a job via `/api/jobs` (or use existing)
4. Submit application via `/api/applications`
5. Run pipeline via `/api/pipeline/run`
6. Check results via `/api/pipeline/status/{app_id}`

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused to agents | Ensure all agent services are running on their designated ports |
| Database connection failed | Verify PostgreSQL is running and credentials in `.env` are correct |
| Zynd discovery failed | Check `ZYND_API_KEY` and ensure Zynd registry is accessible |
| Agent timeout | Increase timeout in `agent_client.py` or check agent logs |
| CORS errors | Verify frontend URL is in allowed origins in `main.py` |

### Database Connection Failed

1. Ensure PostgreSQL is running
2. Check DATABASE_URL in .env
3. Verify database exists: `psql -l`

### Agent Services Not Responding

1. Check if agent services are running: `netstat -an | grep 800[1-8]`
2. Check agent service logs
3. Verify agent service URLs in .env

### Pipeline Timeout

1. Increase AGENT_TIMEOUT in .env
2. Check if agent services are processing requests
3. Review agent service logs for errors

### CORS Errors

1. Verify FRONTEND_URL matches your frontend URL
2. Check browser console for specific error
3. Ensure backend is running on correct port

---

## Production Deployment

### Security Checklist

- [ ] Change SECRET_KEY in .env
- [ ] Set DEBUG=false
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable request logging
- [ ] Configure rate limiting

### Docker Deployment

```bash
# Build image
docker build -t fair-hiring-backend .

# Run container
docker run -p 8010:8010 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/fhn \
  fair-hiring-backend
```

---

## Related Documentation

- [Main README](../README.md) - Project overview
- [Frontend README](../fair-hiring-frontend/README.md) - React dashboard
- [Agent Services README](../agents_services/README.md) - Agent microservices
- [Zynd Integration README](../zynd_integration/README.md) - Zynd SDK setup

---

*Built with FastAPI + SQLAlchemy + Zynd SDK*