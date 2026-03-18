# Fair Hiring Network - API Specification

## Table of Contents

1. [Overview](#overview)
2. [Base Configuration](#base-configuration)
3. [Authentication](#authentication)
4. [Candidates](#candidates)
5. [Companies](#companies)
6. [Jobs](#jobs)
7. [Applications](#applications)
8. [Pipeline](#pipeline)
9. [Passport](#passport)
10. [Health](#health)

---

## Overview

The FHN Backend provides a RESTful API for the Fair Hiring Network platform. All endpoints are prefixed with `/api` unless otherwise noted.

### API Base URL

```
Development: http://localhost:8010
Production:  https://api.fairhiring.network (example)
```

### Documentation

- Swagger UI: `/docs`
- ReDoc: `/redoc`

---

## Base Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `8010` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql+asyncpg://user:pass@localhost:5432/fhn` |
| `USE_ZYND` | Enable Zynd orchestration | `0` |

---

## Authentication

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/candidate/signup` | Register new candidate |
| POST | `/api/auth/candidate/login` | Login candidate |
| POST | `/api/auth/company/signup` | Register new company |
| POST | `/api/auth/company/login` | Login company |
| POST | `/api/auth/sync` | Sync Auth0 user to backend |

### Request/Response

**POST /api/auth/candidate/signup**

Request:
```json
{
  "email": "candidate@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "gender": "prefer_not_to_say",
  "college": "MIT",
  "engineer_level": "senior"
}
```

Response:
```json
{
  "success": true,
  "candidate": {
    "id": "uuid",
    "anon_id": "ANON-ABC123",
    "email": "candidate@example.com"
  },
  "token": "jwt_token_here"
}
```

---

## Candidates

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/candidate/profile` | Get candidate profile |
| PUT | `/api/candidate/profile` | Update candidate profile |
| GET | `/api/candidate/stats` | Get candidate statistics |
| GET | `/api/candidate/applications` | List candidate's applications |
| GET | `/api/candidate/passport` | Get skill passport |

### GET /api/candidate/profile

Response:
```json
{
  "id": "uuid",
  "anon_id": "ANON-ABC123",
  "email": "candidate@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "gender": "prefer_not_to_say",
  "college": "MIT",
  "engineer_level": "senior",
  "github_username": "johndoe",
  "leetcode_username": "johndoe",
  "codeforces_username": "johndoe",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "created_at": "YYYY-MM-DDTHH:MM:SSZ"
}
```

### GET /api/candidate/stats

Response:
```json
{
  "total_applications": 5,
  "pending": 2,
  "interview": 1,
  "rejected": 1,
  "offer": 1,
  "average_match_score": 85.5
}
```

### GET /api/candidate/applications

Response:
```json
{
  "applications": [
    {
      "id": "uuid",
      "job_id": "uuid",
      "job_title": "Senior Software Engineer",
      "company_name": "Tech Corp",
      "status": "interview",
      "match_score": 92.5,
      "applied_at": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ]
}
```

---

## Companies

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/company/profile` | Get company profile |
| PUT | `/api/company/profile` | Update company profile |
| GET | `/api/company/stats` | Get company statistics |
| GET | `/api/company/jobs` | List company jobs |
| GET | `/api/company/review-queue` | Get flagged applications |
| POST | `/api/company/review` | Submit review decision |

### GET /api/company/profile

Response:
```json
{
  "id": "uuid",
  "email": "hr@techcorp.com",
  "company_name": "Tech Corp",
  "industry": "Technology",
  "size": "100-500",
  "created_at": "YYYY-MM-DDTHH:MM:SSZ"
}
```

### GET /api/company/stats

Response:
```json
{
  "total_jobs": 10,
  "total_applications": 50,
  "active_jobs": 5,
  "average_fairness_score": 95.2,
  "candidates_in_pipeline": 25
}
```

### GET /api/company/review-queue

Response:
```json
{
  "flagged_cases": [
    {
      "application_id": "uuid",
      "candidate_anon_id": "ANON-ABC123",
      "job_title": "Software Engineer",
      "flag_reason": "Potential bias detected",
      "severity": "medium",
      "flagged_by": "bias_agent"
    }
  ]
}
```

---

## Jobs

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs` | List published jobs |
| GET | `/api/jobs/{id}` | Get job details |
| POST | `/api/jobs` | Create new job |
| PUT | `/api/jobs/{id}` | Update job |
| DELETE | `/api/jobs/{id}` | Delete job |
| POST | `/api/jobs/analyze` | Analyze job for bias |

### GET /api/jobs

Query Parameters:
- `page` (int): Page number
- `limit` (int): Items per page
- `search` (str): Search by title
- `seniority` (str): Filter by level
- `min_fairness` (float): Minimum fairness score

Response:
```json
{
  "jobs": [
    {
      "id": "uuid",
      "title": "Senior Software Engineer",
      "company_name": "Tech Corp",
      "description": "We are looking for...",
      "required_skills": ["Python", "React", "AWS"],
      "seniority": "senior",
      "fairness_score": 95.5,
      "created_at": "YYYY-MM-DDTHH:MM:SSZ"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

### POST /api/jobs/analyze

Request:
```json
{
  "title": "Senior Software Engineer",
  "description": "We are looking for a rockstar developer from top-tier colleges..."
}
```

Response:
```json
{
  "fairness_score": 72.5,
  "flagged_issues": [
    {
      "type": "college_bias",
      "term": "top-tier colleges",
      "severity": "high",
      "recommendation": "Remove specific college references"
    },
    {
      "type": "gender_bias",
      "term": "rockstar",
      "severity": "medium",
      "recommendation": "Use gender-neutral terms like 'professional'"
    }
  ]
}
```

---

## Applications

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/applications` | Submit application |
| GET | `/api/applications/{id}` | Get application details |
| GET | `/api/applications/job/{job_id}` | List job applications |
| PUT | `/api/applications/{id}/status` | Update application status |
| GET | `/api/applications/{id}/results` | Get agent results |

### POST /api/applications

Request (multipart/form-data):
```
resume: file (PDF)
job_id: uuid
candidate_id: uuid
```

Response:
```json
{
  "success": true,
  "application": {
    "id": "uuid",
    "job_id": "uuid",
    "candidate_id": "uuid",
    "status": "applied",
    "pipeline_status": "pending",
    "created_at": "YYYY-MM-DDTHH:MM:SSZ"
  }
}
```

### GET /api/applications/{id}

Response:
```json
{
  "id": "uuid",
  "job_id": "uuid",
  "job_title": "Senior Software Engineer",
  "candidate_anon_id": "ANON-ABC123",
  "status": "interview",
  "pipeline_status": "completed",
  "match_score": 92.5,
  "resume_url": "https://...",
  "agent_results": {
    "ats": { "fraud_score": 0.05 },
    "github": { "contribution_score": 85 },
    "leetcode": { "rating": 1800 },
    "bias": { "score": 95 },
    "match": { "score": 92.5 }
  },
  "created_at": "YYYY-MM-DDTHH:MM:SSZ"
}
```

---

## Pipeline

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/pipeline/run` | Run pipeline for application |
| GET | `/api/pipeline/status/{application_id}` | Get pipeline status |
| GET | `/api/pipeline/credential/{application_id}` | Get generated credential |
| GET | `/api/pipeline/history/{application_id}` | Get pipeline execution history |

### POST /api/pipeline/run

Request:
```json
{
  "application_id": "uuid"
}
```

Response:
```json
{
  "success": true,
  "pipeline_id": "uuid",
  "status": "running",
  "current_stage": 3,
  "total_stages": 10
}
```

### GET /api/pipeline/status/{application_id}

Response:
```json
{
  "application_id": "uuid",
  "status": "completed",
  "stages": [
    { "name": "ats", "status": "completed", "duration_ms": 450 },
    { "name": "github", "status": "completed", "duration_ms": 1200 },
    { "name": "leetcode", "status": "completed", "duration_ms": 800 },
    { "name": "codeforces", "status": "completed", "duration_ms": 750 },
    { "name": "linkedin", "status": "completed", "duration_ms": 600 },
    { "name": "skill", "status": "completed", "duration_ms": 900 },
    { "name": "test", "status": "completed", "duration_ms": 3000 },
    { "name": "bias", "status": "completed", "duration_ms": 500 },
    { "name": "matching", "status": "completed", "duration_ms": 400 },
    { "name": "passport", "status": "completed", "duration_ms": 200 }
  ],
  "total_duration_ms": 8800
}
```

---

## Passport

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/passport/{candidate_id}` | Get skill passport |
| POST | `/api/passport/verify` | Verify passport signature |

### GET /api/passport/{candidate_id}

Response:
```json
{
  "credential_id": "uuid",
  "candidate_anon_id": "ANON-ABC123",
  "generated_at": "YYYY-MM-DDTHH:MM:SSZ",
  "skill_graph": {
    "skills": [
      {
        "name": "Python",
        "confidence": 95,
        "evidence_sources": ["github", "leetcode", "test"]
      },
      {
        "name": "React",
        "confidence": 88,
        "evidence_sources": ["github", "test"]
      }
    ]
  },
  "verification": {
    "hash_sha256": "abc123...",
    "signature_b64": "xyz789...",
    "is_valid": true
  }
}
```

### POST /api/passport/verify

Request:
```json
{
  "credential_id": "uuid"
}
```

Response:
```json
{
  "is_valid": true,
  "hash_match": true,
  "signature_valid": true,
  "verified_at": "YYYY-MM-DDTHH:MM:SSZ"
}
```

---

## Health

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

### GET /health

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "agents": "9/9 available"
}
```

---

## Error Responses

All endpoints may return standard HTTP error codes:

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid/missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error |

Error Response Format:
```json
{
  "detail": "Error message here"
}
```

---

## Related Documentation

- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [USE_CASES.md](USE_CASES.md) - Use case documentation
- [backend/README.md](backend/README.md) - Backend documentation