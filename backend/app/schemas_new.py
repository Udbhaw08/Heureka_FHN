"""
⚠️ DEPRECATED FILE — NOT USED BY ANY MODULE
This file is NOT imported anywhere in the codebase. All active code uses schemas.py.
This file exists as a reference for a future schema migration.
Do NOT use these schemas — they are not validated against any endpoint.
To use a schema from this file, copy its definition into schemas.py first.

Pydantic Schemas for Fair Hiring System
Request and response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


# Enums
class ApplicationStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    matched = "matched"
    rejected = "rejected"
    needs_review = "needs_review"


class PipelineStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class FairnessStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class ReviewSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class ReviewCaseStatus(str, Enum):
    pending = "pending"
    in_review = "in_review"
    resolved = "resolved"
    dismissed = "dismissed"


# Standard Response Wrapper
class StandardResponse(BaseModel):
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


# Company Schemas
class CompanyRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)


class CompanyLogin(BaseModel):
    email: EmailStr
    password: str


class CompanyResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Candidate Schemas
class CandidateRegister(BaseModel):
    anon_id: str = Field(..., min_length=10, max_length=50)
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8)
    gender: Optional[str] = None
    college: Optional[str] = None
    engineer_level: Optional[str] = None


class CandidateLogin(BaseModel):
    email: EmailStr
    password: str


class CandidateResponse(BaseModel):
    id: int
    anon_id: str
    email: str
    name: str
    gender: Optional[str]
    college: Optional[str]
    engineer_level: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CandidateStats(BaseModel):
    total_applications: int
    matched_applications: int
    pending_applications: int
    rejected_applications: int
    average_match_score: Optional[float]


# Job Schemas
class JobCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=10)
    required_skills: List[str] = Field(default_factory=list)
    max_participants: Optional[int] = None
    application_deadline: Optional[datetime] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    fairness_score: Optional[int] = None
    fairness_status: Optional[FairnessStatus] = None
    fairness_findings: Optional[Dict[str, Any]] = None
    published: Optional[bool] = None
    max_participants: Optional[int] = None
    application_deadline: Optional[datetime] = None


class JobResponse(BaseModel):
    id: int
    company_id: int
    title: str
    description: str
    required_skills: List[str]
    fairness_score: Optional[int]
    fairness_status: Optional[str]
    fairness_findings: Optional[Dict[str, Any]]
    published: bool
    max_participants: Optional[int]
    application_deadline: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Application Schemas
class ApplicationCreate(BaseModel):
    job_id: int
    resume_text: Optional[str] = None
    github_url: Optional[str] = None
    leetcode_url: Optional[str] = None
    codeforces_url: Optional[str] = None
    linkedin_text: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    match_score: Optional[float] = None
    feedback_json: Optional[Dict[str, Any]] = None
    test_required: Optional[bool] = None
    test_score: Optional[int] = None
    pipeline_status: Optional[PipelineStatus] = None
    pipeline_error: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    resume_text: Optional[str]
    resume_path: Optional[str]
    github_url: Optional[str]
    leetcode_url: Optional[str]
    codeforces_url: Optional[str]
    linkedin_pdf_path: Optional[str]
    linkedin_text: Optional[str]
    status: str
    match_score: Optional[float]
    feedback_json: Optional[Dict[str, Any]]
    test_required: bool
    test_score: Optional[int]
    pipeline_status: str
    pipeline_error: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Credential Schemas
class CredentialResponse(BaseModel):
    id: int
    candidate_id: int
    application_id: int
    credential_json: Dict[str, Any]
    hash_sha256: str
    signature_b64: str
    issued_at: datetime
    expires_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Agent Run Schemas
class AgentRunResponse(BaseModel):
    id: int
    application_id: int
    agent_name: str
    input_payload: Optional[Dict[str, Any]]
    output_payload: Optional[Dict[str, Any]]
    status: str
    error_message: Optional[str]
    execution_time_ms: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Review Case Schemas
class ReviewCaseCreate(BaseModel):
    application_id: int
    triggered_by: str
    severity: ReviewSeverity
    reason: str
    evidence: Optional[Dict[str, Any]] = None


class ReviewCaseUpdate(BaseModel):
    status: Optional[ReviewCaseStatus] = None
    review_notes: Optional[str] = None


class ReviewCaseResponse(BaseModel):
    id: int
    application_id: int
    job_id: int
    candidate_id: int
    triggered_by: str
    severity: str
    reason: str
    evidence: Optional[Dict[str, Any]]
    status: str
    reviewed_by: Optional[int]
    review_notes: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Blacklist Schemas
class BlacklistCreate(BaseModel):
    candidate_id: int
    reason: str


class BlacklistResponse(BaseModel):
    id: int
    candidate_id: int
    reason: str
    blacklisted_by: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Pipeline Schemas
class PipelineRunRequest(BaseModel):
    application_id: int


class PipelineStatusResponse(BaseModel):
    application_id: int
    pipeline_status: str
    current_step: Optional[str]
    total_steps: int
    completed_steps: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class PipelineRunResponse(BaseModel):
    success: bool
    application_id: int
    credential: Optional[Dict[str, Any]]
    match_score: Optional[float]
    pipeline_results: Optional[Dict[str, Any]]


class PipelineLogResponse(BaseModel):
    application_id: int
    logs: List[AgentRunResponse]


# Evidence Schemas (for credential_json validation)
class EvidenceSchema(BaseModel):
    ats: Optional[Dict[str, Any]] = None
    github: Optional[Dict[str, Any]] = None
    leetcode: Optional[Dict[str, Any]] = None
    codeforces: Optional[Dict[str, Any]] = None
    linkedin: Optional[Dict[str, Any]] = None
    skills: Optional[Dict[str, Any]] = None
    bias: Optional[Dict[str, Any]] = None
    matching: Optional[Dict[str, Any]] = None


class VerifiedSkillsSchema(BaseModel):
    core: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    infrastructure: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)


class CredentialJsonSchema(BaseModel):
    credential_id: str
    verification_url: Optional[str] = None
    status: str = Field(default="ISSUED")
    evidence: EvidenceSchema
    verified_skills: VerifiedSkillsSchema
    skill_confidence: float = Field(..., ge=0, le=100)
    match_score: Optional[float] = Field(None, ge=0, le=100)
    hash: Optional[str] = None
    signature: Optional[str] = None
    issued_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    @validator('skill_confidence')
    def validate_confidence(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('skill_confidence must be between 0 and 100')
        return v


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    anon_id: Optional[str] = None
    company_id: Optional[int] = None


# Aliases for backward compatibility with routers
CandidateRegisterRequest = CandidateRegister
CandidateLoginRequest = CandidateLogin
CandidateStatsResponse = BaseModel  # Will need to create this properly
ApplicationListResponse = BaseModel  # Will need to create this properly
ApplicationDetailResponse = BaseModel  # Will need to create this properly
JobCreateRequest = JobCreate
JobListResponse = BaseModel  # Will need to create this properly
ApplicationCreateRequest = ApplicationCreate