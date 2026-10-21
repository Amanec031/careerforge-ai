from app.config import Settings


def test_cors_parsing():
    s = Settings(cors_origins="http://a.com, http://b.com ,")
    assert s.cors_origin_list == ["http://a.com", "http://b.com"]


def test_default_threshold_is_15_lpa():
    assert Settings().salary_threshold_inr == 1_500_000


def test_secrets_not_in_repr():
    s = Settings(anthropic_api_key="sk-secret")
    assert "sk-secret" not in repr(s)
