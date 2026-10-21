import redis
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_session

router = APIRouter(tags=["health"])


@router.get("/health")
def liveness() -> dict[str, str]:
    """Process is up. Does not touch dependencies."""
    return {"status": "ok"}


def check_redis() -> None:
    redis.Redis.from_url(get_settings().redis_url, socket_connect_timeout=2).ping()


@router.get("/health/ready")
def readiness(session: Session = Depends(get_session)) -> dict[str, str]:
    """Database and Redis are reachable."""
    try:
        session.execute(text("SELECT 1"))
        check_redis()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail=f"not ready: {type(exc).__name__}") from exc
    return {"status": "ready"}
