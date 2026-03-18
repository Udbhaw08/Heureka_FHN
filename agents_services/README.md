# Agent Services – Fair Hiring Platform

Independent microservices for candidate verification and bias detection.

---

## Overview

The Agent Services provide a distributed network of 9 specialized AI agents that verify candidate skills, detect bias, and generate cryptographic credentials. Each agent runs as an independent microservice on its own port, communicating with the backend via REST API.

---

## Architecture

### Agent Network (ASCII)

```
+-------------------------------------------------------------------------------+
|                          AGENT SERVICES NETWORK                              |
+-------------------------------------------------------------------------------+

    +------------------+        +------------------+        +------------------+
    |                  |        |                  |        |                  |
    |    BACKEND       |        |   ZYND           |        |   EXTERNAL       |
    |    (Port 8010)   |        |   ORCHESTRATOR   |        |   SERVICES       |
    |                  |        |   (Port 5100)    |        |                  |
    +--------+---------+        +--------+---------+        +--------+---------+
             │                          │                          │
             │   HTTP/Webhook          │   Discovery              │
             ▼                          ▼                          ▼
+-------------------------------------------------------------------------------+
|                              AGENT CONSTELLATION                              |
+-------------------------------------------------------------------------------+

+--------+   +--------+   +--------+   +--------+   +--------+   +--------+
| MATCH  |   | BIAS   |   | SKILL  |   |  ATS   |   | PASSPORT|  |LINKEDIN|
| Agent  |   | Agent  |   | Agent  |   | Agent  |   | Agent  |   | Agent  |
|  8001  |   |  8002  |   |  8003  |   |  8004  |   |  8008  |   |  8007  |
+---+----+   +---+----+   +---+----+   +---+----+   +---+----+   +---+----+
    |          |          |          |          |          |
    |          |          |          |          |          |
+--------+   +--------+   +--------+   +--------+   +--------+
|GITHUB  |   |LEETCODE|   |CODEFORCES|
| Agent  |   | Agent  |   | Agent   |
|  8005  |   |  8006  |   |  8011   |
+--------+   +--------+   +--------+

+-------------------------------------------------------------------------------+
|                              EXTERNAL DATA SOURCES                           |
+-------------------------------------------------------------------------------+

  +------------+  +------------+  +------------+  +------------+  +------------+
  |  GitHub    |  | LeetCode   |  | Codeforces |  |  LinkedIn  |  | Resume DB  |
  |  API       |  |    API     |  |    API     |  |    API     |  |   (ATS)    |
  +------------+  +------------+  +------------+  +------------+  +------------+
```

---

## The 9 Agents

### 1. Matching Agent (Port 8001)

**Purpose**: Evidence-based candidate-job matching

**Capabilities**:
- Score candidates against job requirements
- Weight evidence from all verification sources
- Generate match recommendations

**Input**: Candidate profile, job requirements, evidence graph
**Output**: Match score, evidence weights, recommendations

**API**:
```
GET /health
POST /webhook/sync
```

---

### 2. Bias Agent (Port 8002)

**Purpose**: Gender & college bias detection in job descriptions

**Capabilities**:
- Analyze job descriptions for biased language
- Check for socio-economic indicators
- Calculate fairness score

**Input**: Job description text
**Output**: Bias score, flagged terms, fairness eligibility

**API**:
```
GET /health
POST /webhook/sync
```

---

### 3. Skill Agent (Port 8003)

**Purpose**: Skill extraction and verification

**Capabilities**:
- Extract skills from resume text
- Build evidence graph from multiple sources
- Calculate confidence scores

**Input**: Resume text, profile URLs
**Output**: Skills taxonomy, confidence scores, evidence sources

**API**:
```
GET /health
POST /webhook/sync
```

---

### 4. ATS Agent (Port 8004)

**Purpose**: Resume fraud detection and blacklist checking

**Capabilities**:
- Verify resume authenticity
- Check against blacklist database
- Policy compliance verification

**Input**: Resume URL, candidate data
**Output**: Fraud score, blacklist match, policy gating

**API**:
```
GET /health
POST /webhook/sync
```

---

### 5. GitHub Agent (Port 8005)

**Purpose**: Code repository analysis and verification

**Capabilities**:
- Analyze GitHub profile and repositories
- Calculate code quality metrics
- Verify contribution history

**Input**: GitHub username
**Output**: Repo count, stars, forks, language skills, contribution score

**API**:
```
GET /health
POST /webhook/sync
```

---

### 6. LeetCode Agent (Port 8006)

**Purpose**: Algorithm problem-solving verification

**Capabilities**:
- Verify LeetCode profile
- Calculate problem-solving metrics
- Track difficulty distribution

**Input**: LeetCode username
**Output**: Problems solved, rating, difficulty breakdown, percentile

**API**:
```
GET /health
POST /webhook/sync
```

---

### 7. LinkedIn Agent (Port 8007)

**Purpose**: Professional history verification

**Capabilities**:
- Verify LinkedIn profile authenticity
- Validate work history
- Check skills and endorsements

**Input**: LinkedIn profile URL
**Output**: Verified status, job history, education, skills

**API**:
```
GET /health
POST /webhook/sync
```

---

### 8. Passport Agent (Port 8008)

**Purpose**: Cryptographic credential generation

**Capabilities**:
- Aggregate all verification results
- Generate skill passport
- Create cryptographic signature

**Input**: All agent outputs, candidate profile
**Output**: Credential ID, skill graph, SHA256 hash, signature (Base64)

**API**:
```
GET /health
POST /webhook/sync
```

---

### 9. Codeforces Agent (Port 8011)

**Purpose**: Competitive programming verification

**Capabilities**:
- Verify Codeforces profile
- Track contest participation
- Calculate rating history

**Input**: Codeforces username
**Output**: Rating, max rating, contests, problems solved

**API**:
```
GET /health
POST /webhook/sync
```

---

## Running All Agents

### Start All Agents

```bash
cd agents_services
python start_all.py
```

This launches all 9 agent services on their designated ports with visible logs.

### Individual Agent Startup

```bash
# Matching Agent
python matching_agent_service.py

# Bias Agent
python bias_agent_service.py

# Skill Agent
python skill_agent_service.py

# ATS Agent
python ats_service.py

# GitHub Agent
python github_service.py

# LinkedIn Agent
python linkedin_service.py

# LeetCode Agent
python leetcode_service.py

# Codeforces Agent
python codeforce_service.py

# Passport Agent
python passport_service.py
```

---

## Health Checks

Each agent provides a health check endpoint:

```bash
curl http://localhost:8001/health  # Matching
curl http://localhost:8002/health  # Bias
curl http://localhost:8003/health  # Skill
curl http://localhost:8004/health  # ATS
curl http://localhost:8005/health  # GitHub
curl http://localhost:8006/health  # LeetCode
curl http://localhost:8007/health  # LinkedIn
curl http://localhost:8008/health  # Passport
curl http://localhost:8011/health  # Codeforces
```

Response:
```json
{
  "status": "healthy",
  "agent": "matching_agent",
  "version": "1.0.0",
  "capabilities": ["fair_hiring", "matching"]
}
```

---

## Configuration

### Environment Variables

Each agent can be configured via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Agent port | Per agent (see above) |
| `GEMINI_API_KEY` | Google Gemini key | From .env |
| `OLLAMA_BASE_URL` | Ollama URL | http://localhost:11434 |
| `LOG_LEVEL` | Logging level | INFO |

### Agent Communication

Agents communicate with the backend via:
- **Direct HTTP**: REST calls to agent endpoints
- **Zynd Mode**: Via Zynd orchestrator for capability-based discovery

---

## Troubleshooting

### Agent Not Responding

1. Check if port is in use:
   ```bash
   netstat -an | grep 8001
   ```

2. Verify agent is running:
   ```bash
   curl http://localhost:8001/health
   ```

3. Check agent logs for errors

### Connection Timeout

1. Increase timeout in backend config
2. Check network connectivity
3. Verify firewall rules

### Zynd Discovery Failed

1. Check Zynd API key in .env
2. Verify Zynd registry is accessible
3. Review capability mapping

---

## Development

### Adding New Agent

1. Create new service file in `agents_services/`
2. Implement `/health` and `/webhook/sync` endpoints
3. Add to `start_all.py`
4. Update port configuration

### Testing Individual Agent

```bash
curl -X POST http://localhost:8001/webhook/sync \
  -H "Content-Type: application/json" \
  -d '{"job_id": "123", "candidate_id": "456"}'
```

---

## Related Documentation

- [Main README](../README.md) - Project overview
- [Backend README](../backend/README.md) - FastAPI backend
- [Zynd Integration README](../zynd_integration/README.md) - Zynd SDK setup
- [Clean Hiring System](../agents_files/Clean_Hiring_System/) - Core implementations

---

*Each agent is stateless and results are persisted by the backend.*