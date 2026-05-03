"""US2: list 유스케이스 단위 테스트 (T021)."""
import pytest

from todo_lib.db import create_db_engine, get_session_factory
from todo_lib.repository import TodoRepository
from todo_lib.services import TodoService


@pytest.fixture
def service(tmp_db_path):
    engine = create_db_engine(tmp_db_path)
    session = get_session_factory(engine)()
    repo = TodoRepository(session)
    return TodoService(repo)


@pytest.fixture
def seeded_service(service):
    """시드 데이터가 있는 서비스 인스턴스."""
    service.add_todo("첫 번째 작업", priority="high")
    service.add_todo("두 번째 작업", priority="low")
    service.add_todo("세 번째 작업", priority="high")
    # 세 번째 항목 완료 처리
    service.mark_done(3)
    return service


class TestListTodos:
    def test_빈_목록_반환(self, service):
        todos = service.list_todos()
        assert todos == []

    def test_전체_목록_ID_오름차순(self, seeded_service):
        todos = seeded_service.list_todos()
        assert len(todos) == 3
        assert todos[0].id < todos[1].id < todos[2].id

    def test_pending_필터(self, seeded_service):
        todos = seeded_service.list_todos(status="pending")
        assert all(t.status == "pending" for t in todos)
        assert len(todos) == 2

    def test_done_필터(self, seeded_service):
        todos = seeded_service.list_todos(status="done")
        assert all(t.status == "done" for t in todos)
        assert len(todos) == 1

    def test_priority_high_필터(self, seeded_service):
        todos = seeded_service.list_todos(priority="high")
        assert all(t.priority == "high" for t in todos)
        assert len(todos) == 2

    def test_status_priority_조합_필터(self, seeded_service):
        todos = seeded_service.list_todos(status="pending", priority="high")
        assert len(todos) == 1
        assert todos[0].status == "pending"
        assert todos[0].priority == "high"

    def test_잘못된_status_오류(self, service):
        with pytest.raises(ValueError):
            service.list_todos(status="invalid")

    def test_잘못된_priority_오류(self, service):
        with pytest.raises(ValueError):
            service.list_todos(priority="urgent")

    def test_필터_결과_누락_없음(self, seeded_service):
        """필터 결과가 전체 합산과 일치한다."""
        all_todos = seeded_service.list_todos()
        pending = seeded_service.list_todos(status="pending")
        done = seeded_service.list_todos(status="done")
        assert len(pending) + len(done) == len(all_todos)
