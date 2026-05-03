"""SQLAlchemy 기반 TodoRepository 구현."""
from sqlalchemy.orm import Session

from todo_lib.models import STATUS_DONE, Todo


class TodoRepository:
    """Todo 항목의 영속성 관리 클래스."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, todo: Todo) -> Todo:
        """새 Todo를 저장하고 자동 증가 ID가 부여된 인스턴스를 반환한다."""
        self._session.add(todo)
        self._session.commit()
        self._session.refresh(todo)
        return todo

    def get_by_id(self, todo_id: int) -> Todo | None:
        """ID로 단건 조회한다. 없으면 None을 반환한다."""
        return self._session.get(Todo, todo_id)

    def list_all(
        self,
        status: str | None = None,
        priority: str | None = None,
    ) -> list[Todo]:
        """조건에 맞는 Todo 목록을 ID 오름차순으로 반환한다."""
        query = self._session.query(Todo)
        if status is not None:
            query = query.filter(Todo.status == status)
        if priority is not None:
            query = query.filter(Todo.priority == priority)
        return query.order_by(Todo.id).all()

    def mark_done(self, todo: Todo) -> Todo:
        """Todo를 완료 상태로 변경한다. 이미 완료 상태이면 그대로 반환한다."""
        todo.status = STATUS_DONE
        self._session.commit()
        self._session.refresh(todo)
        return todo

    def delete(self, todo: Todo) -> None:
        """Todo를 영구 삭제한다."""
        self._session.delete(todo)
        self._session.commit()
