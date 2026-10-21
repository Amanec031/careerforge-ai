from app import models  # noqa: F401
from app.db import Base

EXPECTED = {
    "users", "master_resume_versions", "job_sources", "job_postings", "tailored_resumes",
    "match_analyses", "saved_jobs", "applications", "notification_preferences",
    "notification_deliveries", "job_runs", "ai_usage",
}


def test_all_tables_registered():
    assert EXPECTED <= set(Base.metadata.tables)


def test_job_dedup_constraints_exist():
    t = Base.metadata.tables["job_postings"]
    names = {c.name for c in t.constraints}
    assert "uq_job_source_external" in names
    assert t.c.fingerprint.unique


def test_notification_sent_once_index_is_unique_and_partial():
    t = Base.metadata.tables["notification_deliveries"]
    idx = next(i for i in t.indexes if i.name == "uq_delivery_sent_once")
    assert idx.unique
    assert "sent" in str(idx.dialect_options["postgresql"]["where"])
