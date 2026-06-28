"""API 依赖。"""
from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# MVP 阶段使用占位认证，后续接入 JWT
def get_current_user_id() -> int:
    return 1


def get_current_active_user_id(user_id: int = Depends(get_current_user_id)) -> int:
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return user_id
