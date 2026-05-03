"""SQLite 엔진/세션 팩토리 및 기본 DB 경로 초기화."""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from todo_lib.models import Base


def get_db_path() -> str:
    """DB 파일 경로를 반환한다. 환경변수 TODO_DB_PATH가 있으면 우선 사용한다."""
    env_path = os.environ.get("TODO_DB_PATH")
    if env_path:
        return env_path
    # 기본 경로: ~/.todo/todo.db
    todo_dir = Path.home() / ".todo"
    todo_dir.mkdir(parents=True, exist_ok=True)
    return str(todo_dir / "todo.db")


def create_db_engine(db_path: str | None = None) -> Engine:
    """SQLite 엔진을 생성하고 테이블을 초기화한다."""
    path = db_path or get_db_path()
    engine = create_engine(f"sqlite:///{path}", echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    """세션 팩토리를 반환한다."""
    return sessionmaker(bind=engine, expire_on_commit=False)
