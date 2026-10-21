"""initial schema

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

TS = sa.DateTime(timezone=True)
NOW = sa.text("now()")


def _id():
    return sa.Column("id", sa.Integer(), primary_key=True)


def _created():
    return sa.Column("created_at", TS, server_default=NOW, nullable=False)


def upgrade() -> None:
    op.create_table(
        "users", _id(),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("display_name", sa.String(200), nullable=False), _created())

    op.create_table(
        "master_resume_versions", _id(),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("latex_source", sa.Text(), nullable=False),
        sa.Column("source_sha256", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False), _created(),
        sa.UniqueConstraint("user_id", "version"))
    op.create_index("ix_master_resume_versions_user_id", "master_resume_versions", ["user_id"])

    op.create_table(
        "job_sources", _id(),
        sa.Column("key", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False), _created())

    op.create_table(
        "job_postings", _id(),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("job_sources.id"), nullable=False),
        sa.Column("external_id", sa.String(200)),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("fingerprint", sa.String(64), nullable=False, unique=True),
        sa.Column("company", sa.String(300), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(300), nullable=False),
        sa.Column("is_remote", sa.Boolean()),
        sa.Column("posted_at", TS),
        sa.Column("first_seen_at", TS, server_default=NOW, nullable=False),
        sa.Column("experience_min_years", sa.Numeric(4, 1)),
        sa.Column("experience_max_years", sa.Numeric(4, 1)),
        sa.Column("salary_min", sa.Numeric(14, 2)),
        sa.Column("salary_max", sa.Numeric(14, 2)),
        sa.Column("salary_currency", sa.String(3)),
        sa.Column("salary_period", sa.String(10)),
        sa.Column("salary_annual_inr_min", sa.Numeric(14, 2)),
        sa.Column("salary_annual_inr_max", sa.Numeric(14, 2)),
        sa.Column("salary_status", sa.String(12), nullable=False),
        sa.UniqueConstraint("source_id", "external_id", name="uq_job_source_external"))
    op.create_index("ix_job_postings_source_id", "job_postings", ["source_id"])
    op.create_index("ix_job_salary_status", "job_postings", ["salary_status"])

    op.create_table(
        "tailored_resumes", _id(),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("master_version_id", sa.Integer(), sa.ForeignKey("master_resume_versions.id"), nullable=False),
        sa.Column("job_posting_id", sa.Integer(), sa.ForeignKey("job_postings.id")),
        sa.Column("company", sa.String(300), nullable=False),
        sa.Column("job_title", sa.String(300), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("job_url", sa.Text()),
        sa.Column("location", sa.String(300)),
        sa.Column("salary_text", sa.String(200)),
        sa.Column("latex_source", sa.Text(), nullable=False),
        sa.Column("change_summary", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column("pdf_path", sa.Text()),
        sa.Column("compile_status", sa.String(12), nullable=False),
        sa.Column("compile_log", sa.Text()), _created(),
        sa.Column("approved_at", TS))
    op.create_index("ix_tailored_resumes_user_id", "tailored_resumes", ["user_id"])

    op.create_table(
        "match_analyses", _id(),
        sa.Column("job_posting_id", sa.Integer(), sa.ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("master_version_id", sa.Integer(), sa.ForeignKey("master_resume_versions.id"), nullable=False),
        sa.Column("score", sa.Numeric(5, 2), nullable=False),
        sa.Column("breakdown", sa.JSON(), nullable=False),
        sa.Column("matched_skills", sa.JSON(), nullable=False),
        sa.Column("missing_skills", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False), _created(),
        sa.UniqueConstraint("job_posting_id", "master_version_id"))

    op.create_table(
        "saved_jobs", _id(),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_posting_id", sa.Integer(), sa.ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False),
        _created(), sa.UniqueConstraint("user_id", "job_posting_id"))

    op.create_table(
        "applications", _id(),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_posting_id", sa.Integer(), sa.ForeignKey("job_postings.id")),
        sa.Column("tailored_resume_id", sa.Integer(), sa.ForeignKey("tailored_resumes.id")),
        sa.Column("company", sa.String(300), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("applied_at", TS), _created(),
        sa.Column("updated_at", TS, server_default=NOW, nullable=False))
    op.create_index("ix_applications_user_id", "applications", ["user_id"])

    op.create_table(
        "notification_preferences", _id(),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("recipient_email", sa.String(320), nullable=False),
        sa.Column("send_hour_local", sa.Integer(), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False),
        sa.Column("min_match_score", sa.Integer(), nullable=False),
        sa.Column("salary_threshold_inr", sa.Integer(), nullable=False),
        sa.Column("role_keywords", sa.JSON(), nullable=False),
        sa.Column("location_keywords", sa.JSON(), nullable=False),
        sa.Column("show_uncertain_in_dashboard", sa.Boolean(), nullable=False))

    op.create_table(
        "notification_deliveries", _id(),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_posting_id", sa.Integer(), sa.ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(10), nullable=False),
        sa.Column("provider_message_id", sa.String(200)),
        sa.Column("error", sa.Text()), _created())
    op.create_index("uq_delivery_sent_once", "notification_deliveries",
                    ["user_id", "job_posting_id"], unique=True,
                    postgresql_where=sa.text("status = 'sent'"))

    op.create_table(
        "job_runs", _id(),
        sa.Column("trigger", sa.String(12), nullable=False),
        sa.Column("started_at", TS, server_default=NOW, nullable=False),
        sa.Column("finished_at", TS),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column("sources_checked", sa.JSON(), nullable=False),
        sa.Column("new_jobs", sa.Integer(), nullable=False),
        sa.Column("qualified_matches", sa.Integer(), nullable=False),
        sa.Column("email_status", sa.String(12), nullable=False),
        sa.Column("error_message", sa.Text()))

    op.create_table(
        "ai_usage", _id(),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("provider", sa.String(30), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("purpose", sa.String(50), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False), _created())


def downgrade() -> None:
    for t in ["ai_usage", "job_runs", "notification_deliveries", "notification_preferences",
              "applications", "saved_jobs", "match_analyses", "tailored_resumes",
              "job_postings", "job_sources", "master_resume_versions", "users"]:
        op.drop_table(t)
