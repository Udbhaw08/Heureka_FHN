# Company Fairness Agent

The **Company Fairness Agent** is a specialized AI agent that analyzes company hiring practices and job postings for potential bias. It goes beyond individual job descriptions to evaluate the overall fairness profile of an employer's hiring approach.

---

## Overview

**Purpose**: Detect and measure bias in company hiring practices and job postings

**Agent DID**: `did:zynd:0xCOMPANYFAIRNESS`

**Primary Use**: Analyze company job postings and hiring patterns for:
- Gender bias indicators
- Age bias indicators
- College/university bias
- Experience inflation patterns
- Overall fairness scoring

---

## Features

### Bias Detection Categories

1. **Gender Bias Detection**
   - Detects masculine-coded language ("rockstar", "ninja", "guru")
   - Identifies aggressive/dominant terminology
   - Flags gendered role assumptions

2. **Age Bias Detection**
   - Identifies age-related keywords ("young", "energetic")
   - Detects experience requirements that exclude older workers
   - Flags "digital native" and similar generational language

3. **College Bias Detection**
   - Identifies tier-based college language ("IIT", "NIT", "Tier-1")
   - Flags specific university preferences
   - Detects Ivy League/oxbridge bias patterns

4. **Experience Inflation Detection**
   - Identifies unrealistic experience requirements
   - Detects patterns like "10+ years for entry role"
   - Flags "must have X years" without context

### Fairness Scoring

| Score Range | Classification | Action |
|-------------|----------------|--------|
| 90-100 | Excellent | No flags, fully inclusive |
| 75-89 | Good | Minor adjustments recommended |
| 60-74 | Fair | Moderate changes needed |
| Below 60 | Poor | Requires revision before posting |

### Penalty System

- **Severe Bias**: -15 points
- **Moderate Bias**: -10 points
- **Minor Bias**: -5 points

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | API key for LLM | Required |
| `REDIS_HOST` | Redis host | localhost |
| `REDIS_PORT` | Redis port | 6379 |

### Fairness Thresholds

Located in `config.py`:

```python
MINIMUM_FAIRNESS_SCORE = 60  # Below this = rejected from pipeline
SEVERE_PENALTY = 15         # Points deducted for severe bias
MODERATE_PENALTY = 10       # Points deducted for moderate bias
MINOR_PENALTY = 5           # Points deducted for minor bias
```

### Bias Keywords

The agent uses comprehensive keyword dictionaries:

```python
GENDERED_KEYWORDS = [
    "rockstar", "ninja", "guru", "wizard", "hacker",
    "aggressive", "dominant", "assertive",
    "young", "energetic", "digital native",
    "chairman", "manpower", "mankind"
]

AGE_BIAS_KEYWORDS = [
    "young team", "fresh graduate", "recent graduate",
    "digital native", "young and dynamic",
    "maximum 5 years experience", "no more than"
]

COLLEGE_BIAS_KEYWORDS = [
    "tier-1 college", "iit", "nit", "bits",
    "top university", "premier institute",
    "ivy league", "oxbridge"
]
```

---

## Usage

### Python API

```python
from agents.company_fairness_agent import CompanyFairnessAgent

# Initialize agent
agent = CompanyFairnessAgent()

# Analyze job description
result = agent.analyze("""
Senior Software Engineer - Rockstar Developer Wanted!

We're looking for a coding ninja to join our young team.
Requirements:
- Must be from a Tier-1 college (IIT preferred)
- 10+ years of experience
""")

print(result)
```

### Output Format

```json
{
  "fairness_score": 45,
  "flagged_issues": [
    {
      "type": "gender_bias",
      "term": "rockstar",
      "severity": "moderate",
      "recommendation": "Use gender-neutral terms like 'professional'"
    },
    {
      "type": "college_bias",
      "term": "Tier-1 college",
      "severity": "severe",
      "recommendation": "Remove specific college requirements"
    },
    {
      "type": "experience_inflation",
      "term": "10+ years",
      "severity": "severe",
      "recommendation": "Adjust experience requirements to be realistic"
    }
  ],
  "overall_recommendation": "Requires significant revision before posting"
}
```

---

## Integration

### With Backend

The Company Fairness Agent is integrated with the backend via:

1. **Direct HTTP** (Default)
   - Runs on designated port
   - Backend calls `/webhook/sync` endpoint

2. **Zynd Mode** (Optional)
   - Registered in Zynd registry
   - Discovered via capability search

### Endpoint

```
GET  /health          - Health check
POST /webhook/sync    - Analyze job for bias
```

---

## Example Analysis

### Biased Input

```
Senior Software Engineer - Rockstar Developer Wanted!

We're looking for a coding ninja to join our young and dynamic team.
You should be a self-starter with aggressive problem-solving skills.

Requirements:
- Must be from a Tier-1 college (IIT/NIT preferred)
- 10+ years of experience in Python
- Recent graduate energy with senior-level skills
- Digital native who lives and breathes code
```

### Output

```json
{
  "fairness_score": 35,
  "flagged_issues": [
    {"type": "gender_bias", "term": "rockstar", "severity": "moderate"},
    {"type": "gender_bias", "term": "ninja", "severity": "moderate"},
    {"type": "gender_bias", "term": "aggressive", "severity": "severe"},
    {"type": "age_bias", "term": "young and dynamic", "severity": "severe"},
    {"type": "age_bias", "term": "digital native", "severity": "moderate"},
    {"type": "age_bias", "term": "recent graduate", "severity": "severe"},
    {"type": "college_bias", "term": "Tier-1 college", "severity": "severe"},
    {"type": "college_bias", "term": "IIT/NIT", "severity": "severe"},
    {"type": "experience_inflation", "term": "10+ years", "severity": "severe"}
  ],
  "overall_recommendation": "Requires significant revision"
}
```

### Fair Input

```
Senior Software Engineer

We're looking for an experienced engineer to join our collaborative team.

Requirements:
- Strong Python programming skills
- 5+ years of software development experience
- Experience with distributed systems
- Excellent problem-solving abilities

We offer:
- Competitive salary based on experience
- Comprehensive health benefits
- Flexible work arrangements
- Professional development budget
```

### Output

```json
{
  "fairness_score": 95,
  "flagged_issues": [],
  "overall_recommendation": "Job posting is inclusive and fair"
}
```

---

## Dependencies

```
anthropic
openrouter
redis
python-dotenv
```

See `requirements.txt` for full list.

---

## Related Documentation

- [Main README](../../../README.md) - Project overview
- [Backend README](../../../backend/README.md) - Backend integration
- [Bias Agent README](../bias_detection_agent/README.md) - Related bias agent
- [agents_services README](../../../agents_services/README.md) - Agent services

---

*This agent uses Claude Sonnet via OpenRouter for nuanced bias detection.*