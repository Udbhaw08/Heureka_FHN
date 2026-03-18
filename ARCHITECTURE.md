# Fair Hiring Network - Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Flow Architecture](#data-flow-architecture)
5. [Security Architecture](#security-architecture)
6. [Deployment Architecture](#deployment-architecture)
7. [Technology Stack](#technology-stack)

---

## System Overview

The **Fair Hiring Network (FHN)** is an AI-driven recruitment platform designed to eliminate bias in hiring through evidence-based skill verification. The system uses a constellation of 9 specialized AI agents to verify candidate skills, detect bias, and match candidates to jobs based on verified evidence rather than traditional resumes.

### Core Principles

1. **Bias-Free Hiring** - AI-powered bias detection in job descriptions
2. **Evidence-Based Verification** - Multi-source skill verification
3. **Cryptographic Credentials** - Blockchain-backed skill passports
4. **Transparency** - Auditable decision-making process

---

## High-Level Architecture

### System Architecture Diagram

```
+-------------------------------------------------------------------------------+
|                          FAIR HIRING NETWORK                                 |
+-------------------------------------------------------------------------------+

                           +-------------------+
                           |   END USERS       |
                           |   - Candidates    |
                           |   - Companies    |
                           |   - Reviewers    |
                           +--------+----------+
                                    |
                                    v
+-------------------------------------------------------------------------------+
|                         PRESENTATION LAYER                                    |
+-------------------------------------------------------------------------------+
|                                                                               |
|  +-------------------------+    +-------------------------+                   |
|  |   React Dashboard       |    |   Auth0                 |                   |
|  |   (Port 5173)           |    |   Authentication       |                   |
|  |                         |    |   (OAuth2/OIDC)         |                   |
|  |   - Landing Page        |    +-------------------------+                   |
|  |   - Company Dashboard   |                                                 |
|  |   - Candidate Portal    |                                                 |
|  |   - AI Protocall        |                                                 |
|  +------------+-------------+                                                 |
|               |                                                               |
|               v                                                               |
+-------------------------------------------------------------------------------+
|                          API GATEWAY LAYER                                    |
+-------------------------------------------------------------------------------+
|                                                                               |
|  +-------------------------------------------------------------------------+  |
|  |                      FASTAPI BACKEND (Port 8010)                       |  |
|  |                                                                         |  |
|  |  +------------------+  +------------------+  +----------------------+   |  |
|  |  |   REST API       |  |  Pipeline        |  |   Zynd              |   |  |
|  |  |   Endpoints      |  |  Orchestrator    |  |   Orchestrator      |   |  |
|  |  +------------------+  +------------------+  +----------------------+   |  |
|  |         |                    |                     |                      |  |
|  |         v                    v                     v                      |  |
|  |  +-------------------------------------------------------------------------+  |
|  |  |                    AGENT CLIENT LAYER                               |  |
|  |  |   Direct HTTP / Zynd Protocol / Retry Logic / Timeout Handling     |  |
|  |  +-------------------------------------------------------------------------+  |
|  +-------------------------------------------------------------------------+  |
|                                    |                                           |
+-------------------------------------+-------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------------+
|                         AGENT SERVICES LAYER                                  |
+-------------------------------------------------------------------------------+
|                                                                               |
|  +----------+  +----------+  +----------+  +----------+  +----------+        |
|  | MATCHING |  |  BIAS   |  |  SKILL   |  |   ATS    |  |PASSPORT  |        |
|  | Agent    |  | Agent    |  | Agent    |  | Agent    |  | Agent    |        |
|  | :8001    |  | :8002    |  | :8003    |  | :8004    |  | :8008    |        |
|  +----------+  +----------+  +----------+  +----------+  +----------+        |
|                                                                               |
|  +----------+  +----------+  +----------+  +----------+                       |
|  | GITHUB   |  |LINKEDIN |  |LEETCODE  |  |CODEFORCES|                       |
|  | Agent    |  | Agent    |  | Agent    |  | Agent    |                       |
|  | :8005    |  | :8007    |  | :8006    |  | :8011    |                       |
|  +----------+  +----------+  +----------+  +----------+                       |
|                                                                               |
+-------------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------------+
|                         EXTERNAL SERVICES                                     |
+-------------------------------------------------------------------------------+
|                                                                               |
|  +-------------+  +-------------+  +-------------+  +-------------+             |
|  |  Google     |  | ElevenLabs  |  |   Ollama    |  |  Auth0      |             |
|  |  Gemini 2.0 |  |    TTS      |  |  (Local LLM)|  |             |             |
|  +-------------+  +-------------+  +-------------+  +-------------+             |
|                                                                               |
+-------------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------------+
|                         DATA LAYER                                            |
+-------------------------------------------------------------------------------+
|                                                                               |
|  +-------------------------------------------------------------------------+  |
|  |                      POSTGRESQL DATABASE                               |  |
|  |                      (Port 5432)                                       |  |
|  |                                                                         |  |
|  |  +------------+  +------------+  +------------+  +------------+          |  |
|  |  | companies  |  | candidates |  |    jobs    |  │applications|          |  |
|  |  +------------+  +------------+  +------------+  +------------+          |  |
|  |                                                                         |  |
|  |  +------------+  +------------+  +------------+                          |  |
|  |  |credentials |  | agent_runs |  | review_cases|                         |  |
|  |  +------------+  +------------+  +------------+                          |  |
|  +-------------------------------------------------------------------------+  |
+-------------------------------------------------------------------------------+
```

---

## Component Architecture

### Frontend Component Architecture

```
React Application
├── App.jsx (Root Component)
│   ├── BrowserRouter
│   │   ├── LandingPage (/)
│   │   ├── CompanyPage (/company)
│   │   │   ├── CompanyAuth
│   │   │   ├── CompanyDashboard
│   │   │   ├── CompanyHiringFlow
│   │   │   ├── CompanyRolePipeline
│   │   │   └── CompanyCandidateReview
│   │   ├── CandidatePage (/candidate)
│   │   │   ├── CandidateAuth
│   │   │   ├── CandidateExperience
│   │   │   ├── CandidateApply
│   │   │   └── SkillPassport
│   │   ├── InterviewPage (/candidate/interview)
│   │   │   └── ProtocallApp
│   │   │       ├── InterviewSetup
│   │   │       ├── InterviewSession (WebRTC + Gemini)
│   │   │       └── AnalysisReport (ElevenLabs TTS)
│   │   └── PassportPage (/passport/:id)
│   │
│   └── Auth0Provider
│       └── Auth0 Hooks (useAuth)
│
├── API Integration
│   └── Axios Client (JWT Interceptor)
│
└── 3D/Animation Layer
    ├── Three.js (Landing Page)
    ├── Framer Motion (Route Transitions)
    ├── GSAP (Advanced Animations)
    └── Lenis (Smooth Scroll)
```

### Backend Component Architecture

```
FastAPI Application
├── Main Application (main.py)
│   ├── CORS Configuration
│   ├── Lifespan Manager (DB init, Zynd init)
│   ├── Exception Handlers
│   └── Routers
│
├── Routers
│   ├── auth.py (Authentication)
│   ├── candidate.py (Candidate management)
│   ├── company.py (Company management)
│   ├── job.py (Job CRUD)
│   ├── application.py (Application processing)
│   ├── pipeline.py (Pipeline execution)
│   ├── passport.py (Skill passport)
│   ├── agent.py (Agent orchestration)
│   └── health.py (Health checks)
│
├── Services
│   ├── PipelineService (High-level pipeline)
│   └── PipelineOrchestrator (10-stage execution)
│
├── Agent Communication
│   ├── AgentClient (HTTP calls)
│   └── ZyndOrchestrator (Zynd discovery)
│
└── Data Access
    ├── SQLAlchemy Models
    ├── Pydantic Schemas
    └── Async Database Session
```

### Agent Architecture

```
Agent Service (Independent Microservice)
├── FastAPI Instance (Unique port per agent)
│   ├── Health Endpoint (/health)
│   ├── Webhook Endpoint (/webhook/sync)
│   └── Capabilities Metadata
│
├── Agent Logic
│   ├── Input Validation
│   ├── External API Calls (GitHub, LeetCode, etc.)
│   ├── AI Processing (Gemini/Ollama)
│   └── Output Generation
│
└── Error Handling
    ├── Timeout Management
    ├── Retry Logic
    └── Logging
```

---

## Data Flow Architecture

### Candidate Application Flow

```
1. CANDIDATE REGISTRATION
   Candidate → Auth0 → Backend (sync)
   Backend → Database (create candidate record)
   Result: Candidate profile created

2. JOB APPLICATION
   Candidate → Frontend → Backend (/api/applications)
   Backend → Database (create application)
   Backend → PipelineService (trigger pipeline)
   Result: Application submitted, pipeline started

3. PIPELINE EXECUTION (10 Stages)
   PipelineOrchestrator → AgentClient → Each Agent (sequential)
   └── Stage 1: ATS Agent → Resume verification
   └── Stage 2: GitHub Agent → Code analysis
   └── Stage 3: LeetCode Agent → Algorithm verification
   └── Stage 4: Codeforces Agent → Competitive coding
   └── Stage 5: LinkedIn Agent → Professional history
   └── Stage 6: Skill Agent → Skill extraction
   └── Stage 7: Test Agent → Practical test
   └── Stage 8: Bias Agent → Fairness audit
   └── Stage 9: Matching Agent → Score calculation
   └── Stage 10: Passport Agent → Credential generation

   Each stage: Backend → Agent → Response → Database (agent_runs)
   Result: Pipeline complete, credential generated

4. CREDENTIAL RETRIEVAL
   Candidate → Frontend → Backend (/api/passport/:id)
   Backend → Database (retrieve credential)
   Result: Skill passport with cryptographic signature
```

### Company Workflow

```
1. COMPANY REGISTRATION
   Company → Auth0 → Backend (sync)
   Backend → Database (create company record)
   Result: Company profile created

2. JOB POSTING
   Company → Frontend → Backend (/api/jobs)
   Backend → Bias Agent (analyze for bias)
   Backend → Database (create job with fairness score)
   Result: Job posted with bias audit results

3. CANDIDATE REVIEW
   Company → Frontend → Backend (/api/company/review-queue)
   Backend → Database (fetch flagged candidates)
   Company → Frontend → Backend (/api/company/review)
   Backend → Database (update review status)
   Result: Human review completed

4. CANDIDATE SELECTION
   Company → Frontend → Backend (/api/applications/:id/status)
   Backend → Database (update status to "selected")
   Result: Candidate selected, offer sent
```

---

## Security Architecture

### Authentication & Authorization

```
+------------------------+     +------------------------+
|    Auth0              |     |    Backend            |
|    (Identity Provider)|     |    (JWT Validation)   |
+------------------------+     +------------------------+
         |                            |
         v                            v
    User Login                  Validate Token
         |                            |
         v                            v
   OAuth2/OIDC               Extract Claims
         |                            |
         v                            v
   Get Token                  Check Permissions
         |                            |
         v                            v
Return Token              Authorize Request
```

### Security Measures

| Layer | Security Measure |
|-------|-----------------|
| Transport | TLS/SSL encryption |
| API | JWT token validation |
| CORS | Allowed origins configuration |
| Data | Encrypted database fields |
| Audit | Agent run logging |
| Rate Limiting | Per-endpoint limits |

---

## Deployment Architecture

### Development Environment

```
┌─────────────────────────────────────────────────────────────┐
│                     DEVELOPMENT                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Frontend   │  │   Backend    │  │   Database   │       │
│  │   Vite       │  │   FastAPI    │  │  PostgreSQL  │       │
│  │   :5173      │  │   :8010      │  │   :5432      │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐      │
│  │            9 Agent Services                       │      │
│  │  :8001 :8002 :8003 :8004 :8005 :8006 :8007 :8008 :8011 │
│  └──────────────────────────────────────────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Production Environment (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│                      PRODUCTION                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │   CDN        │  │   Load       │                         │
│  │   (Static)   │◄─│   Balancer   │                         │
│  └──────────────┘  └──────┬───────┘                         │
│                           │                                  │
│                    ┌──────▼───────┐                         │
│                    │   Backend    │                         │
│                    │   (Scaling)  │                         │
│                    └──────┬───────┘                         │
│                           │                                  │
│              ┌────────────┼────────────┐                    │
│              ▼            ▼            ▼                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Agent 1    │  │   Agent 2    │  │   Agent N    │      │
│  │   (Docker)   │  │   (Docker)   │  │   (Docker)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │   PostgreSQL │  │   External   │                         │
│  │   (RDS)      │  │   Services   │                         │
│  └──────────────┘  └──────────────┘                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend Technologies

| Category | Technology | Version |
|----------|-----------|---------|
| Framework | React | 18.3.1 |
| Build Tool | Vite | 6.0.3 |
| Routing | React Router | 7.13.0 |
| Styling | Tailwind CSS | 3.4.17 |
| Animations | Framer Motion | 12.29.0 |
| Animations | GSAP | 3.12.5 |
| 3D | Three.js | 0.170.0 |
| Scroll | Lenis | 1.1.18 |
| Auth | Auth0 | 2.15.0 |
| AI | Google Generative AI | 0.24.1 |
| Charts | Recharts | 3.7.0 |
| HTTP | Axios | 1.13.3 |

### Backend Technologies

| Category | Technology | Version |
|----------|-----------|---------|
| Framework | FastAPI | 0.109+ |
| ORM | SQLAlchemy | 2.0+ |
| Database | PostgreSQL | 14+ |
| Driver | asyncpg | 0.29+ |
| Validation | Pydantic | 2.5+ |
| Server | Uvicorn | 0.27+ |
| Agent SDK | Zynd | 0.1.0 |

### External Services

| Service | Purpose |
|---------|---------|
| Google Gemini 2.0 | LLM for analysis |
| ElevenLabs | Text-to-Speech |
| Ollama | Local LLM |
| Auth0 | Authentication |

---

## Related Documentation

- [README.md](README.md) - Project overview and quick start
- [backend/README.md](backend/README.md) - Backend documentation
- [fair-hiring-frontend/README.md](fair-hiring-frontend/README.md) - Frontend documentation
- [agents_services/README.md](agents_services/README.md) - Agent services documentation
- [zynd_integration/README.md](zynd_integration/README.md) - Zynd SDK documentation