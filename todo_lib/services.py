"""TodoService: 유스케이스 및 공통 검증 함수."""
from __future__ import annotations

import re
from datetime import datetime

from todo_lib.models import ALLOWED_PRIORITIES, ALLOWED_STATUSES, STATUS_DONE, Todo
from todo_lib.repository import TodoRepository

# 날짜 형식 정규식
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------------------------------------------------------------------------
# 검증 함수
# ---------------------------------------------------------------------------

def validate_title(title: str) -> str:
    """제목을 검증하고 정규화된 문자열을 반환한다. 유효하지 않으면 ValueError를 발생시킨다."""
    stripped = title.strip()
    if not stripped:
        raise ValueError("제목은 빈 값일 수 없습니다.")
    if len(stripped) > 200:
        raise ValueError(f"제목은 200자 이하여야 합니다. (현재 {len(stripped)}자)")
    return stripped


def validate_due_date(due_date: str | None) -> str | None:
    """마감일 형식을 검증한다. None이면 None을 반환한다. 유효하지 않으면 ValueError를 발생시킨다."""
    if due_date is None:
        return None
    if not _DATE_RE.match(due_date):
        raise ValueError(f"날짜 형식이 올바르지 않습니다: '{due_date}'. YYYY-MM-DD 형식을 사용하세요.")
    try:
        datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"유효하지 않은 날짜입니다: '{due_date}'.")
    return due_date


def validate_priority(priority: str | None) -> str | None:
    """우선순위 값을 검증한다. None이면 None을 반환한다. 유효하지 않으면 ValueError를 발생시킨다."""
    if priority is None:
        return None
    if priority not in ALLOWED_PRIORITIES:
        allowed = ", ".join(sorted(ALLOWED_PRIORITIES))
        raise ValueError(f"우선순위는 {allowed} 중 하나여야 합니다: '{priority}'")
    return priority


def validate_status_filter(status: str | None) -> str | None:
    """상태 필터 값을 검증한다."""
    if status is None:
        return None
    if status not in ALLOWED_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_STATUSES))
        raise ValueError(f"상태 필터는 {allowed} 중 하나여야 합니다: '{status}'")
    return status


# ---------------------------------------------------------------------------
# 유스케이스
# ---------------------------------------------------------------------------

class TodoService:
    """Todo 비즈니스 로직 유스케이스 모음."""

    def __init__(self, repository: TodoRepository) -> None:
        self._repo = repository

    def add_todo(
        self,
        title: str,
        due_date: str | None = None,
        priority: str | None = None,
    ) -> Todo:
        """새 Todo를 생성하고 저장한다."""
        clean_title = validate_title(title)
        clean_due = validate_due_date(due_date)
        clean_priority = validate_priority(priority)

        now = datetime.utcnow()
        todo = Todo(
            title=clean_title,
            due_date=clean_due,
            priority=clean_priority,
            created_at=now,
            updated_at=now,
        )
        return self._repo.add(todo)

    def list_todos(
        self,
        status: str | None = None,
        priority: str | None = None,
    ) -> list[Todo]:
        """조건에 맞는 Todo 목록을 반환한다."""
        clean_status = validate_status_filter(status)
        clean_priority = validate_priority(priority)
        return self._repo.list_all(status=clean_status, priority=clean_priority)

    def mark_done(self, todo_id: int) -> tuple[Todo, bool]:
        """Todo를 완료 처리한다. (todo, already_done) 튜플을 반환한다."""
        todo = self._repo.get_by_id(todo_id)
        if todo is None:
            raise LookupError(f"ID {todo_id}에 해당하는 항목을 찾을 수 없습니다.")
        already_done = todo.status == STATUS_DONE
        if not already_done:
            self._repo.mark_done(todo)
        return todo, already_done

    def delete_todo(self, todo_id: int) -> Todo:
        """Todo를 영구 삭제하고 삭제된 항목을 반환한다."""
        todo = self._repo.get_by_id(todo_id)
        if todo is None:
            raise LookupError(f"ID {todo_id}에 해당하는 항목을 찾을 수 없습니다.")
        self._repo.delete(todo)
        return todo
