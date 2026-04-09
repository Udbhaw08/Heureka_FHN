# Test Agent (Conditional Test Service)

**FastAPI service for generating and evaluating skill-based tests**

---

## Overview

The **Test Agent** (also known as Conditional Test Service) generates and evaluates practical skill tests for candidates. It creates customized tests based on the candidate's verified skill set and evaluates their answers to provide a practical skills score.

**Port**: 8009

**Agent DID**: `did:zynd:0xTEST`

---

## Purpose

The Test Agent serves as **Stage 7** in the 10-stage pipeline:

1. Evaluates candidates on their verified skills
2. Generates skill-appropriate questions
3. Provides practical skill verification beyond profile data
4. Includes anti-cheat measures for test integrity

---

## Features

### Test Generation
- **Skill-based questions**: Generates questions based on candidate's verified skills
- **Difficulty levels**: Easy, Medium, Hard
- **Customizable**: Configurable number of questions
- **LLM Integration**: Ready for Claude/GPT question generation

### Test Evaluation
- **Automatic grading**: Scores submitted answers
- **Pass/Fail determination**: Based on passing threshold (default 70%)
- **Detailed feedback**: Provides score and improvement suggestions
- **Audit trail**: Stores test results for review

### Job Skill Extraction
- **Extracts skills** from job descriptions
- **Categorizes** technical skills and experience level
- **Integrates** with Job Extraction Agent

---

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "conditional_test",
  "tests_in_memory": 5
}
```

### Generate Test

```
POST /generate
```

Request:
```json
{
  "skills": ["Python", "React", "AWS"],
  "difficulty": "medium",
  "num_questions": 10
}
```

Response:
```json
{
  "test_id": "a1b2c3d4e5f6",
  "questions": [
    {
      "id": "q1",
      "text": "Which of the following best describes Python?",
      "options": [
        "Option A about Python",
        "Option B about Python",
        "Option C about Python",
        "Option D about Python"
      ]
    }
  ],
  "time_limit": 30,
  "passing_score": 70
}
```

### Evaluate Test

```
POST /evaluate
```

Request:
```json
{
  "test_id": "a1b2c3d4e5f6",
  "answers": {
    "q1": "A",
    "q2": "B",
    "q3": "A"
  }
}
```

Response:
```json
{
  "score": 75,
  "passed": true,
  "total_questions": 10,
  "correct_answers": 8,
  "feedback": "Great job! You scored 75% and passed the test."
}
```

### Get Test

```
GET /test/{test_id}
```

Retrieves test questions (without correct answers) for review/resume.

### Extract Job Skills

```
POST /extract
```

Request:
```json
{
  "job_title": "Senior Software Engineer",
  "job_description": "We need a Python developer with React and AWS experience..."
}
```

Response:
```json
{
  "skills": ["Python", "React", "AWS"],
  "experience_level": "senior",
  "categories": {
    "programming_languages": ["Python"],
    "frameworks": ["React"],
    "cloud_services": ["AWS"]
  }
}
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Service port | `8009` |

### Dependencies

```
fastapi
pydantic
uvicorn
```

---

## Integration

### With Backend Pipeline

The Test Agent is called during **Stage 7** of the pipeline:

```
PipelineService → Test Agent (Port 8009)
                  ↓
            /generate (create test)
                  ↓
            Store test in memory
                  ↓
            Return test to candidate
                  ↓
            /evaluate (after submission)
                  ↓
            Store results in agent_runs
```

### Test Flow

```
1. Skill Agent verifies skills
2. Backend calls Test Agent (/generate)
3. Candidate receives test questions
4. Candidate submits answers
5. Backend calls Test Agent (/evaluate)
6. Test Agent returns score and results
7. Results stored in database
```

---

## Anti-Cheat Features

- **Time limits**: 30-minute window for completion
- **Unique test IDs**: Each test has unique identifier
- **No answer leakage**: Correct answers not sent to frontend
- **Audit logging**: All submissions logged for review

---

## Running the Test Agent

```bash
cd agents_services
python conditional_test_service.py
```

Or with custom port:
```bash
PORT=8009 python conditional_test_service.py
```

---

## Related Documentation

- [Main README](../../README.md) - Project overview
- [Backend README](../../backend/README.md) - Pipeline integration
- [agents_services README](./README.md) - All agent services
- [skill_verification_agent README](../../agents_files/Clean_Hiring_System/skill_verification_agent/README.md) - Skill verification

---

*This agent generates practical skill tests for candidate verification.*