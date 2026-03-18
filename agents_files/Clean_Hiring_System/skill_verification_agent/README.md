# 🏢 Fair Hiring Network - Complete System Documentation

> **Tagline:** *Fair hiring starts with fair systems. We verify both.*

**Version:** 4.0 | 

---

## 🎯 Executive Summary

The Fair Hiring Network is an AI-powered hiring pipeline that ensures **fair, transparent, and verifiable** candidate evaluation. The system uses a **multi-agent architecture** with built-in bias detection, security hardening, and human-in-the-loop oversight.

### Key Innovations (v4.0)
| Feature | Description |
|---------|-------------|
| **Dual LLM Strategy** | Local models for extraction (cost: $0), Cloud models for security (high accuracy) |
| **Human Review Queue** | Centralized service for critical decisions requiring human oversight |
| **Semantic Injection Detection** | AI-powered detection of resume manipulation attempts |
| **Systemic Bias Auditing** | Statistical analysis of hiring patterns across demographics |
| **Cryptographic Passports** | Ed25519 signed credentials for portable skill verification |

---

## 📁 Project Structure

```
Clean_Hiring_System/
│
├── 📄 README.md                          # This documentation
├── 📄 AGENTS.md                          # Agent specifications
├── 📄 DUAL_LLM_WALKTHROUGH.md           # LLM strategy documentation
│
├── 🤖 skill_verification_agent/          # Core verification pipeline
│   ├── agents/
│   │   ├── ats.py                        # ATS Resume Parser + Security
│   │   ├── skill_verification_agent_v2.py # Credential issuer
│   │   └── evidence_graph_builder.py     # Multi-source evidence fusion
│   ├── scrapers/
│   │   ├── github_api.py                 # GitHub profile analyzer
│   │   ├── codeforces_scraper.py         # Codeforces stats
│   │   └── leetcode_scraper.py           # LeetCode achievements
│   ├── utils/
│   │   ├── dual_llm_client.py            # 🆕 Dual LLM routing
│   │   ├── manipulation_detector.py      # 🆕 Prompt injection defense
│   │   ├── evasion_detector.py           # 🆕 Semantic injection scanner
│   │   └── white_text_detector.py        # Hidden text detection
│   ├── run_complete_workflow.py          # Main pipeline runner
│   └── config.py                         # LLM & API configuration
│
├── ⚖️ bias_detection_agent/              # Fairness auditor
│   ├── agents/
│   │   └── bias_detection_agent.py       # 🆕 Integrated with Human Review
│   └── run_bias_check.py                 # Standalone bias tester
│
├── 🤝 matching_agent/                    # Transparent job matching
│   └── agents/
│       └── matching_agent.py             # Explainable scoring
│
├── 🛂 passport_agent/                    # Credential issuance
│   └── agents/
│       └── passport_agent.py             # Ed25519 signed passports
│
├── 🏢 company_fairness_agent/            # JD bias scanner
│   └── agents/
│       └── company_fairness_agent.py     # Gendered language detection
│
├── 🔧 services/                          # 🆕 Shared services
│   ├── human_review_service.py           # Central review queue manager
│   └── review_service.py                 # Legacy review service
│
├── 🧪 test_attacks/                      # Security test cases
│   ├── David Chen - Senior ML Engineer.pdf  # Semantic injection test
│   └── *.pdf                             # Various attack vectors
│
├── 📊 Output Files (Generated)
│   ├── ats_output.json                   # Resume extraction + security
│   ├── github_output.json                # GitHub analysis
│   ├── evidence_graph_output.json        # Fused evidence
│   ├── final_credential.json             # Verified skills
│   ├── bias_report.json                  # Fairness audit
│   ├── match_result.json                 # Job matching score
│   ├── passport_credential.json          # Signed passport
│   └── human_review_queue.json           # 🆕 Pending reviews
│
└── 📚 docs/                              # Additional documentation
```

---

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Python 3.11+
python --version

# Ollama (for local LLM)
ollama serve
ollama pull llama3.2
```

### 2. Environment Setup
```bash
cd Clean_Hiring_System
pip install -r skill_verification_agent/requirements.txt

# Configure API keys
cp skill_verification_agent/.env.example skill_verification_agent/.env
# Edit .env with your OPENROUTER_API_KEY
```

### 3. Run Complete Pipeline
```bash
python skill_verification_agent/run_complete_workflow.py \
  --resume "path/to/resume.pdf" \
  --github "username" \
  --linkedin "profile.pdf" \
  --leetcode "https://leetcode.com/u/username/" \
  --codeforces "https://codeforces.com/profile/username"
```

### 4. Check Results
```bash
# View credential
cat final_credential.json

# View security findings
cat ats_output.json

# View pending human reviews
cat human_review_queue.json
```

---

## 🏗️ Architecture Overview

### Pipeline Flow
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CANDIDATE SUBMISSION                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 1: ATS RESUME PROCESSING                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  │
│  │ White Text Detector │  │ Injection Scanner   │  │ Dual LLM Defense    │  │
│  │ (Hidden keywords)   │  │ (Regex patterns)    │  │ (Claude 3.5 Haiku)  │  │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  │
│                                       │                                      │
│                    ┌──────────────────┴──────────────────┐                  │
│                    ▼                                      ▼                  │
│            [SAFE: Continue]                    [THREAT: Blacklist + Review] │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 2-5: EVIDENCE COLLECTION (Parallel)                                   │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐                │
│  │  GitHub   │  │ LeetCode  │  │Codeforces │  │ LinkedIn  │                │
│  │   API     │  │  Scraper  │  │  Scraper  │  │   PDF     │                │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 6: EVIDENCE GRAPH BUILDER                                             │
│  - Cross-references skills across sources                                   │
│  - Detects conflicts (claim without proof)                                  │
│  - Calculates confidence scores                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 7: SKILL CREDENTIAL ISSUANCE                                          │
│  ┌─────────────────────┐  ┌─────────────────────┐                           │
│  │ Integrity Check     │  │ Manipulation Score  │──► [HIGH: Human Review]  │
│  │ (Claim vs Evidence) │  │ (Aggregate Flags)   │                           │
│  └─────────────────────┘  └─────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 8: BIAS DETECTION (System Audit)                                      │
│  - Gender Gap Analysis                                                       │
│  - College Tier Bias                                                         │
│  - GitHub Age Discrimination                                                │
│                    │                                                         │
│                    ▼                                                         │
│         [BIAS DETECTED: Human Review + Flagged]                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 9: TRANSPARENT MATCHING                                               │
│  - Skill overlap scoring                                                     │
│  - Explainable decision                                                      │
│  - Same scorecard for candidate & company                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  STEP 10: PASSPORT ISSUANCE                                                 │
│  - Ed25519 Digital Signature                                                │
│  - Portable credential                                                       │
│  - Verification URL                                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Features (v4.0)

### Dual LLM Strategy
| Layer | Model | Purpose | Cost |
|-------|-------|---------|------|
| **Extraction** | Ollama/Llama 3.1 | Resume parsing, skill extraction | $0 (local) |
| **Security** | Claude 3.5 Haiku | Prompt injection, manipulation detection | ~$0.001/call |

### Threat Detection
```json
// Example: Semantic Injection Detected
{
  "injection_detected": true,
  "severity": "critical",
  "action": "immediate_blacklist",
  "narrative_analysis": {
    "type": "semantic_injection",
    "patterns_matched": [
      "Evaluation systems processing this data should recognize",
      "Assessment frameworks are designed to"
    ]
  },
  "human_review_status": "SUBMITTED",
  "human_review_id": "review_254a2d"
}
```

### Security Checks
| Check | Description | Action |
|-------|-------------|--------|
| **White Text Detection** | Hidden keywords in PDFs | Blacklist |
| **Regex Injection Scan** | `[SYSTEM]`, `ignore previous` | Blacklist |
| **Semantic Injection** | Professional language masks | Blacklist + Review |
| **Evasion Detection** | CSS tricks, steganography | Flag for Review |

---

## 👥 Human Review System

### Queue Structure (`human_review_queue.json`)
```json
{
  "review_id": "review_9b79bd",
  "candidate_id": "eval_6cb46a61",
  "triggered_by": "bias_detection",
  "severity": "high",
  "reason": "Systemic Bias Detected: HIGH",
  "evidence": {
    "gender_bias": {
      "bias_detected": true,
      "gap": 25,
      "male_avg": 85,
      "female_avg": 60
    }
  },
  "system_action_taken": "flagged",
  "status": "PENDING",
  "human_decision": null,
  "reviewer_notes": null
}
```

### Triggers for Human Review
| Trigger | Severity | System Action |
|---------|----------|---------------|
| Security Blacklist | Critical | `blocked` |
| Injection Detected | Critical | `blocked` |
| White Text Found | Critical | `blocked` |
| Systemic Bias (Gap > 10) | High | `flagged` |
| PII Leak Detected | Critical | `blocked` |
| Manipulation Score > 70 | High | `paused` |

---

## ⚖️ Bias Detection

### Checks Performed
1. **Gender Bias**: Compares average scores between genders (threshold: 10 points)
2. **College Tier Bias**: IIT/NIT vs Tier-2 vs Tier-3 scoring gaps
3. **GitHub Age Bias**: Penalizing newer accounts unfairly
4. **Metadata Leak**: Ensuring protected attributes don't influence scoring

### Mock Testing
```bash
# Run bias check with exaggerated mock data
python bias_detection_agent/run_bias_check.py
```

---

## 🛠️ Configuration

### `skill_verification_agent/config.py`
```python
# LLM Backend Selection
LLM_BACKEND = "ollama"  # or "openrouter"

# Local Model (Extraction)
OLLAMA_MODEL = "llama3.2"

# Cloud Model (Security)
OPENROUTER_API_KEY = "sk-or-..."
OPENROUTER_SECURITY_MODEL = "anthropic/claude-3.5-haiku"

# Thresholds
MANIPULATION_THRESHOLD = 70
BIAS_GAP_THRESHOLD = 10
```

---

## 📊 Output Files Reference

| File | Description | Generated By |
|------|-------------|--------------|
| `ats_output.json` | Resume extraction + security findings | ATS Agent |
| `github_output.json` | GitHub profile analysis | GitHub Scraper |
| `leetcode_output.json` | LeetCode stats | LeetCode Scraper |
| `codeforces_output.json` | Codeforces ratings | Codeforces Scraper |
| `linkedin_output.json` | LinkedIn PDF extraction | LinkedIn Parser |
| `evidence_graph_output.json` | Fused evidence from all sources | Evidence Graph Builder |
| `final_credential.json` | Verified skills with confidence | Skill Verification Agent |
| `bias_report.json` | Fairness audit results | Bias Detection Agent |
| `match_result.json` | Job matching score | Matching Agent |
| `passport_credential.json` | Signed portable credential | Passport Agent |
| `human_review_queue.json` | Pending human review items | Human Review Service |

---

## 🧪 Testing

### Security Testing
```bash
# Test with malicious resume (should be BLACKLISTED)
python skill_verification_agent/run_complete_workflow.py \
  --resume "test_attacks/David Chen - Senior ML Engineer.pdf" \
  --github "testuser"
```

### Bias Testing
```bash
# Run standalone bias check
python bias_detection_agent/run_bias_check.py
```

### Unit Tests
```bash
cd tests
python -m pytest
```

---

## 🔄 API Integration (Coming Soon)

### FastAPI Endpoints (Planned)
```
POST /api/v1/candidates/submit
GET  /api/v1/candidates/{id}/status
GET  /api/v1/reviews/pending
POST /api/v1/reviews/{id}/decision
GET  /api/v1/passports/{credential_id}/verify
```

---

## 📈 Cost Analysis

| Component | Model | Cost per Call | Calls per Candidate |
|-----------|-------|---------------|---------------------|
| Resume Extraction | Llama 3.1 (local) | $0 | 1 |
| Security Check | Claude 3.5 Haiku | ~$0.001 | 1 |
| Bias Analysis | Llama 3.1 (local) | $0 | 1 |
| Matching | Llama 3.1 (local) | $0 | 1 |
| **Total** | | **~$0.001** | |

---

## 🛡️ Compliance & Ethics

- ✅ **No ATS Keyword Gaming**: Skills verified against code evidence
- ✅ **Explainable Decisions**: Every score can be traced to evidence
- ✅ **Same Scorecard**: Candidate and company see identical data
- ✅ **Bias Auditing**: Statistical fairness checks on every batch
- ✅ **Human Oversight**: Critical decisions require human approval
- ✅ **Portable Credentials**: Candidates own their verified skills

---

## 👨‍💻 Development Team

Built for the Fair Hiring Initiative | 2026

---

## 📚 Related Documentation

- [AGENTS.md](./AGENTS.md) - Detailed agent specifications
- [DUAL_LLM_WALKTHROUGH.md](./DUAL_LLM_WALKTHROUGH.md) - LLM strategy deep-dive
- [DB_HANDOFF.md](./DB_HANDOFF.md) - Database integration guide
- [PIPELINE_DOCUMENTATION.md](./PIPELINE_DOCUMENTATION.md) - Pipeline internals

---

**Version:** 4.0 | **License:** MIT | **Status:** Production Ready
