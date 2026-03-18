# Fair Hiring Network - Use Cases

## Table of Contents

1. [Overview](#overview)
2. [Candidate Use Cases](#candidate-use-cases)
3. [Company Use Cases](#company-use-cases)
4. [System Use Cases](#system-use-cases)
5. [Agent-Specific Use Cases](#agent-specific-use-cases)

---

## Overview

The Fair Hiring Network supports multiple user roles with distinct workflows:

| Role | Primary Goals |
|------|---------------|
| **Candidate** | Apply to jobs, get verified, receive offers |
| **Company** | Post jobs, review candidates, make hires |
| **Reviewer** | Review flagged cases, ensure fairness |
| **System** | Orchestrate agents, generate credentials |

---

## Candidate Use Cases

### UC-001: Candidate Registration

**Actor**: Job seeker
**Goal**: Create an account on the platform

**Preconditions**: None

**Flow**:
1. Candidate visits the platform
2. Clicks "Sign Up" as Candidate
3. Chooses Auth0 authentication (Google, GitHub, email)
4. Auth0 returns OAuth token
5. Frontend syncs token with backend
6. Backend creates candidate record
7. Candidate redirected to dashboard

**Postconditions**: Candidate account created with unique `anon_id`

---

### UC-002: Apply to Job

**Actor**: Candidate
**Goal**: Submit application for a job

**Preconditions**:
- Candidate is authenticated
- At least one job is published

**Flow**:
1. Candidate browses available jobs
2. Clicks on a job to view details
3. Clicks "Apply Now"
4. Uploads resume (PDF)
5. Fills application form
6. Submits application
7. Backend receives application
8. Backend triggers pipeline
9. Candidate sees "Under Review" status

**Postconditions**: Application created, pipeline initiated

---

### UC-003: Complete Skill Assessment

**Actor**: Candidate
**Goal**: Demonstrate practical skills

**Preconditions**:
- Application submitted
- Skill test scheduled

**Flow**:
1. Candidate receives skill test notification
2. Opens skill test from dashboard
3. Anti-cheat system initializes (browser monitoring)
4. Candidate completes coding challenges
5. Test results submitted to backend
6. Backend updates application with test scores

**Postconditions**: Test results stored, pipeline continues

---

### UC-004: Complete AI Interview

**Actor**: Candidate
**Goal**: Complete AI-powered video interview

**Preconditions**:
- Skill test completed
- Interview scheduled

**Flow**:
1. Candidate receives interview notification
2. Opens interview setup
3. Configures camera/microphone
4. Starts interview session
5. AI (Gemini) asks questions in real-time
6. Candidate responds via video
7. System records and analyzes responses
8. Interview ends, analysis generated
9. Audio summary generated via ElevenLabs

**Postconditions**: Interview completed, analysis stored

---

### UC-005: View Skill Passport

**Actor**: Candidate
**Goal**: View verified credentials

**Preconditions**: Pipeline completed, credential generated

**Flow**:
1. Candidate navigates to passport page
2. Enters candidate ID or selects from profile
3. Backend retrieves credential
4. Frontend displays skill graph
5. Shows cryptographic signature verification

**Postconditions**: Passport displayed with verification status

---

### UC-006: Track Application Status

**Actor**: Candidate
**Goal**: Monitor application progress

**Preconditions**: At least one application submitted

**Flow**:
1. Candidate opens dashboard
2. Views application list
3. Each application shows status:
   - Applied (submitted)
   - Under Review (pipeline running)
   - Shortlisted (passed initial screening)
   - Interview Scheduled
   - Offer Received
   - Rejected (with feedback)

**Postconditions**: Application status visible

---

## Company Use Cases

### UC-101: Company Registration

**Actor**: Employer
**Goal**: Create company account

**Preconditions**: None

**Flow**:
1. Company representative visits platform
2. Clicks "Sign Up" as Company
3. Enters company email and password (or Auth0)
4. Backend creates company record
5. Company redirected to dashboard

**Postconditions**: Company account created

---

### UC-102: Post New Job

**Actor**: Company HR/Recruiter
**Goal**: Create a new job posting

**Preconditions**: Company account exists

**Flow**:
1. Company navigates to "Post Job"
2. Enters job details (title, description, requirements)
3. Adds required skills
4. Sets seniority level
5. Submits job posting
6. Backend sends to Bias Agent for analysis
7. Bias Agent returns fairness score
8. Job created with fairness score visible

**Postconditions**: Job posted, bias analysis complete

---

### UC-103: Review Candidates

**Actor**: Company HR/Recruiter
**Goal**: Evaluate candidates who applied

**Preconditions**: At least one application exists

**Flow**:
1. Company opens dashboard
2. Views list of jobs
3. Selects a job to see applicants
4. Kanban view shows candidates by stage
5. Clicks on candidate card
6. Views:
   - Resume
   - Skill passport (verified credentials)
   - Agent analysis results
   - Match score breakdown
7. Can advance, reject, or flag for review

**Postconditions**: Candidate status updated

---

### UC-104: Review Flagged Candidates

**Actor**: Company HR/Recruiter
**Goal**: Handle candidates flagged by AI

**Preconditions**: At least one candidate flagged

**Flow**:
1. Company views flagged queue
2. Reads flagged reason (from bias agent or ATS)
3. Reviews candidate details
4. Makes decision:
   - Override flag (proceed with hiring)
   - Confirm flag (reject application)
5. Decision recorded in database

**Postconditions**: Flag resolved, candidate status updated

---

### UC-105: Make Job Offer

**Actor**: Company HR/Recruiter
**Goal**: Extend offer to selected candidate

**Preconditions**: Candidate passed all stages

**Flow**:
1. Company selects candidate from pipeline
2. Clicks "Make Offer"
3. Confirms offer details
4. Candidate status changes to "Offer Sent"
5. Candidate receives notification

**Postconditions**: Offer recorded, candidate notified

---

### UC-106: Analyze Job Fairness

**Actor**: Company HR/Recruiter
**Goal**: Check job posting for bias

**Preconditions**: Job exists

**Flow**:
1. Company opens job details
2. Views "Fairness Score" section
3. Sees breakdown:
   - Gender bias indicators
   - College bias indicators
   - Demographic terms flagged
4. Gets recommendations for improvement

**Postconditions**: Fairness analysis visible

---

## System Use Cases

### UC-201: Execute Pipeline

**Actor**: System (Backend)
**Goal**: Run all verification agents for an application

**Preconditions**: Application submitted

**Flow**:
1. Application created
2. PipelineService triggered
3. PipelineOrchestrator runs 10 stages sequentially:
   - Stage 1: ATS Agent (fraud check)
   - Stage 2: GitHub Agent (code analysis)
   - Stage 3: LeetCode Agent (algorithms)
   - Stage 4: Codeforces Agent (competitive)
   - Stage 5: LinkedIn Agent (professional history)
   - Stage 6: Skill Agent (skill extraction)
   - Stage 7: Test Agent (practical test)
   - Stage 8: Bias Agent (fairness audit)
   - Stage 9: Matching Agent (score calculation)
   - Stage 10: Passport Agent (credential generation)
4. Each stage logs to agent_runs table
5. Final credential stored in credentials table

**Postconditions**: Pipeline complete, credential generated

---

### UC-202: Discover Agents (Zynd Mode)

**Actor**: System (Zynd Orchestrator)
**Goal**: Find agents by capability

**Preconditions**: USE_ZYND=1

**Flow**:
1. Backend needs agent for capability
2. ZyndOrchestrator receives request
3. Searches registry for matching capability
4. Returns agent endpoint
5. Backend calls agent via webhook

**Postconditions**: Agent discovered and called

---

### UC-203: Verify Credential

**Actor**: System or User
**Goal**: Validate cryptographic passport

**Preconditions**: Credential exists

**Flow**:
1. User requests passport verification
2. Backend retrieves credential
3. Extracts hash and signature
4. Verifies signature with public key
5. Returns verification result (valid/invalid)

**Postconditions**: Verification result returned

---

## Agent-Specific Use Cases

### ATS Agent: UC-301

**Goal**: Detect resume fraud
**Flow**:
1. Receive candidate resume and data
2. Check against known fraud patterns
3. Query blacklist database
4. Verify policy compliance
5. Return fraud score and flags

**Output**: `{fraud_score, blacklist_match, policy_gating}`

---

### Bias Agent: UC-302

**Goal**: Detect bias in job descriptions
**Flow**:
1. Receive job description text
2. Analyze for gender-biased terms
3. Analyze for college-biased terms
4. Check for demographic indicators
5. Calculate overall fairness score

**Output**: `{bias_score, flagged_terms, fairness_eligibility}`

---

### Skill Agent: UC-303

**Goal**: Extract skills from multiple sources
**Flow**:
1. Receive resume text
2. Receive profile URLs (GitHub, LinkedIn)
3. Parse and extract skills
4. Build evidence graph
5. Calculate confidence scores

**Output**: `{skills: [], confidence_scores: {}, evidence_sources: []}`

---

### Matching Agent: UC-304

**Goal**: Calculate evidence-based match score
**Flow**:
1. Receive candidate profile and evidence
2. Receive job requirements
3. Weight evidence by relevance
4. Calculate match score
5. Generate recommendations

**Output**: `{match_score, evidence_weights, recommendations}`

---

### Passport Agent: UC-305

**Goal**: Generate cryptographic credential
**Flow**:
1. Receive all agent outputs
2. Aggregate into skill graph
3. Calculate SHA256 hash
4. Generate cryptographic signature
5. Store in database

**Output**: `{credential_id, skill_graph, hash_sha256, signature_b64}`

---

### GitHub Agent: UC-306

**Goal**: Analyze code repositories
**Flow**:
1. Receive GitHub username
2. Fetch profile and repository data
3. Analyze code quality metrics
4. Calculate contribution score
5. Return analysis results

**Output**: `{repo_count, stars, forks, languages, contribution_score}`

---

### LeetCode Agent: UC-307

**Goal**: Verify algorithmic skills
**Flow**:
1. Receive LeetCode username
2. Fetch profile and activity
3. Calculate problems solved by difficulty
4. Get current rating and percentile
5. Return verification results

**Output**: `{problems_solved, rating, easy/medium/hard, percentile}`

---

### Codeforces Agent: UC-308

**Goal**: Verify competitive programming
**Flow**:
1. Receive Codeforces username
2. Fetch profile and contest history
3. Get current and max rating
4. Calculate contest participation
5. Return verification results

**Output**: `{rating, max_rating, contests, problems_solved}`

---

### LinkedIn Agent: UC-309

**Goal**: Verify professional history
**Flow**:
1. Receive LinkedIn profile URL
2. Fetch profile data
3. Verify job history
4. Check education credentials
5. Validate skills and endorsements

**Output**: `{verified, job_history, education, skills}`

---

## Related Documentation

- [README.md](README.md) - Project overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [API_SPEC.md](API_SPEC.md) - API specification
- [backend/README.md](backend/README.md) - Backend documentation
- [agents_services/README.md](agents_services/README.md) - Agent services