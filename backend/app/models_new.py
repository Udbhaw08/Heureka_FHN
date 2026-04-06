"""
⚠️ DEPRECATED FILE — NOT USED BY ANY MODULE
This file is NOT imported anywhere in the codebase. All active code uses models.py.
This file exists as a reference for a future schema migration.
Do NOT use these models — they are not registered with the database.
To use a model from this file, copy its definition into models.py first.

New Database Models for Fair Hiring System
Rebuilt with proper constraints, indexes, and relationships
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, 
    ForeignKey, JSON, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Company(Base):
    """Company table for job postings"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")
    reviewed_cases = relationship("ReviewCase", back_populates="reviewer")
    blacklisted_candidates = relationship("Blacklist", back_populates="blacklisted_by_company")


class Candidate(Base):
    """Candidate table for job applicants"""
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    anon_id = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    gender = Column(String(50))
    college = Column(String(255))
    engineer_level = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    applications = relationship("Application", back_populates="candidate", cascade="all, delete-orphan")
    credentials = relationship("Credential", back_populates="candidate", cascade="all, delete-orphan")
    review_cases = relationship("ReviewCase", back_populates="candidate", cascade="all, delete-orphan")
    blacklist_entries = relationship("Blacklist", back_populates="candidate", cascade="all, delete-orphan")


class Job(Base):
    """Job table for job postings"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)
    fairness_score = Column(Integer, CheckConstraint('fairness_score >= 0 AND fairness_score <= 100'))
    fairness_status = Column(String(50), CheckConstraint("fairness_status IN ('pending', 'approved', 'rejected')"))
    fairness_findings = Column(JSON)
    published = Column(Boolean, default=False, index=True)
    max_participants = Column(Integer)
    application_deadline = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    review_cases = relationship("ReviewCase", back_populates="job", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_jobs_status', 'fairness_status'),
    )


class Application(Base):
    """Application table for job applications"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_text = Column(Text)
    resume_path = Column(String(500))
    github_url = Column(String(500))
    leetcode_url = Column(String(500))
    codeforces_url = Column(String(500))
    linkedin_pdf_path = Column(String(500))
    linkedin_text = Column(Text)
    status = Column(
        String(50), 
        default='pending',
        index=True
    )
    match_score = Column(Float)
    feedback_json = Column(JSON)
    test_required = Column(Boolean, default=False)
    test_score = Column(Integer)
    pipeline_status = Column(
        String(50),
        default='not_started',
        index=True
    )
    pipeline_error = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    credentials = relationship("Credential", back_populates="application", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="application", cascade="all, delete-orphan")
    review_cases = relationship("ReviewCase", back_populates="application", cascade="all, delete-orphan")


class Credential(Base):
    """Credential table for skill passports"""
    __tablename__ = "credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    credential_json = Column(JSON, nullable=False)
    hash_sha256 = Column(String(100), nullable=False, index=True)
    signature_b64 = Column(Text, nullable=False)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="credentials")
    application = relationship("Application", back_populates="credentials")


class AgentRun(Base):
    """Agent run table for audit trail"""
    __tablename__ = "agent_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    input_payload = Column(JSON)
    output_payload = Column(JSON)
    status = Column(
        String(50),
        nullable=False,
        index=True
    )
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    application = relationship("Application", back_populates="agent_runs")


class ReviewCase(Base):
    """Review case table for human review queue"""
    __tablename__ = "review_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    triggered_by = Column(String(100), nullable=False)
    severity = Column(
        String(50),
        index=True
    )
    reason = Column(Text, nullable=False)
    evidence = Column(JSON)
    status = Column(
        String(50),
        default='pending',
        index=True
    )
    reviewed_by = Column(Integer, ForeignKey("companies.id"))
    review_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    application = relationship("Application", back_populates="review_cases")
    job = relationship("Job", back_populates="review_cases")
    candidate = relationship("Candidate", back_populates="review_cases")
    reviewer = relationship("Company", back_populates="reviewed_cases")


class Blacklist(Base):
    """Blacklist table for blacklisted candidates"""
    __tablename__ = "blacklists"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    blacklisted_by = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    candidate = relationship("Candidate", back_populates="blacklist_entries")
    blacklisted_by_company = relationship("Company", back_populates="blacklisted_candidates")