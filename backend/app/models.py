"""Database models. Deduplication is enforced with DB-level unique constraints."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def _now() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    display_name: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = _now()


class MasterResumeVersion(Base):
    __tablename__ = "master_resume_versions"
    __table_args__ = (UniqueConstraint("user_id", "version"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(200), default="")
    latex_source: Mapped[str] = mapped_column(Text)
    source_sha256: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = _now()


class JobSource(Base):
    __tablename__ = "job_sources"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(50), unique=True)  # e.g. adzuna, remotive
    name: Mapped[str] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)  # no secrets here
    created_at: Mapped[datetime] = _now()


class JobPosting(Base):
    __tablename__ = "job_postings"
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_job_source_external"),
        Index("ix_job_salary_status", "salary_status"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("job_sources.id"), index=True)
    external_id: Mapped[str | None] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(Text)
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True)  # stable hash fallback
    company: Mapped[str] = mapped_column(String(300))
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default="")
    location: Mapped[str] = mapped_column(String(300), default="")
    is_remote: Mapped[bool | None] = mapped_column(Boolean)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    experience_min_years: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    experience_max_years: Mapped[Decimal | None] = mapped_column(Numeric(4, 1))
    salary_min: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    salary_max: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    salary_currency: Mapped[str | None] = mapped_column(String(3))
    salary_period: Mapped[str | None] = mapped_column(String(10))  # year|month|hour
    salary_annual_inr_min: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    salary_annual_inr_max: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    # qualified | uncertain | below | unknown  (see strict rule in README)
    salary_status: Mapped[str] = mapped_column(String(12), default="unknown")


class TailoredResume(Base):
    __tablename__ = "tailored_resumes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    master_version_id: Mapped[int] = mapped_column(ForeignKey("master_resume_versions.id"))
    job_posting_id: Mapped[int | None] = mapped_column(ForeignKey("job_postings.id"))
    company: Mapped[str] = mapped_column(String(300))
    job_title: Mapped[str] = mapped_column(String(300))
    job_description: Mapped[str] = mapped_column(Text)
    job_url: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(300))
    salary_text: Mapped[str | None] = mapped_column(String(200))
    latex_source: Mapped[str] = mapped_column(Text)
    change_summary: Mapped[list] = mapped_column(JSON, default=list)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(12), default="draft")  # draft|approved
    pdf_path: Mapped[str | None] = mapped_column(Text)
    compile_status: Mapped[str] = mapped_column(String(12), default="none")
    compile_log: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = _now()
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class MatchAnalysis(Base):
    __tablename__ = "match_analyses"
    __table_args__ = (UniqueConstraint("job_posting_id", "master_version_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    job_posting_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id", ondelete="CASCADE"))
    master_version_id: Mapped[int] = mapped_column(ForeignKey("master_resume_versions.id"))
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    matched_skills: Mapped[list] = mapped_column(JSON, default=list)
    missing_skills: Mapped[list] = mapped_column(JSON, default=list)
    explanation: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = _now()


class SavedJob(Base):
    __tablename__ = "saved_jobs"
    __table_args__ = (UniqueConstraint("user_id", "job_posting_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    job_posting_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = _now()


class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    job_posting_id: Mapped[int | None] = mapped_column(ForeignKey("job_postings.id"))
    tailored_resume_id: Mapped[int | None] = mapped_column(ForeignKey("tailored_resumes.id"))
    company: Mapped[str] = mapped_column(String(300))
    title: Mapped[str] = mapped_column(String(300))
    # interested|resume_ready|applied|interview|rejected|offer
    status: Mapped[str] = mapped_column(String(20), default="interested")
    notes: Mapped[str] = mapped_column(Text, default="")
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = _now()
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    recipient_email: Mapped[str] = mapped_column(String(320), default="")
    send_hour_local: Mapped[int] = mapped_column(Integer, default=9)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Kolkata")
    min_match_score: Mapped[int] = mapped_column(Integer, default=50)
    salary_threshold_inr: Mapped[int] = mapped_column(Integer, default=1_500_000)
    role_keywords: Mapped[list] = mapped_column(JSON, default=list)
    location_keywords: Mapped[list] = mapped_column(JSON, default=list)
    show_uncertain_in_dashboard: Mapped[bool] = mapped_column(Boolean, default=True)


class NotificationDelivery(Base):
    __tablename__ = "notification_deliveries"
    __table_args__ = (
        # A job can be successfully emailed to a user only once, even on reruns.
        Index("uq_delivery_sent_once", "user_id", "job_posting_id", unique=True,
              postgresql_where=text("status = 'sent'")),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    job_posting_id: Mapped[int] = mapped_column(ForeignKey("job_postings.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(10))  # sent|failed
    provider_message_id: Mapped[str | None] = mapped_column(String(200))
    error: Mapped[str | None] = mapped_column(Text)  # sanitized, never credentials
    created_at: Mapped[datetime] = _now()


class JobRun(Base):
    __tablename__ = "job_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    trigger: Mapped[str] = mapped_column(String(12))  # schedule|manual
    started_at: Mapped[datetime] = _now()
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(12), default="running")
    sources_checked: Mapped[list] = mapped_column(JSON, default=list)
    new_jobs: Mapped[int] = mapped_column(Integer, default=0)
    qualified_matches: Mapped[int] = mapped_column(Integer, default=0)
    email_status: Mapped[str] = mapped_column(String(12), default="none")
    error_message: Mapped[str | None] = mapped_column(Text)


class AiUsage(Base):
    __tablename__ = "ai_usage"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    provider: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(100))
    purpose: Mapped[str] = mapped_column(String(50))
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = _now()
