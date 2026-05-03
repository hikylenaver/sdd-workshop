"""도메인 모델 및 상수 정의."""
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# 상태 상수
STATUS_PENDING = "pending"
STATUS_DONE = "done"
ALLOWED_STATUSES = {STATUS_PENDING, STATUS_DONE}

# 우선순위 상수
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"
ALLOWED_PRIORITIES = {PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW}


class Base(DeclarativeBase):
    pass


class Todo(Base):
    """ToDo 항목 도메인 모델. sqlite_autoincrement=True로 삭제된 ID 재사용을 방지한다."""

    __tablename__ = "todos"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    due_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default=STATUS_PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<Todo id={self.id} title={self.title!r} status={self.status}>"
