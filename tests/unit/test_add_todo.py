"""US1: add 유스케이스 단위 테스트 (T014)."""
import pytest

from todo_lib.db import create_db_engine, get_session_factory
from todo_lib.repository import TodoRepository
from todo_lib.services import TodoService


@pytest.fixture
def service(tmp_db_path):
    """테스트용 서비스 인스턴스를 반환한다."""
    engine = create_db_engine(tmp_db_path)
    session = get_session_factory(engine)()
    repo = TodoRepository(session)
    return TodoService(repo)


class TestAddTodo:
    def test_유효한_제목으로_추가_성공(self, service):
        todo = service.add_todo("보고서 작성")
        assert todo.id is not None
        assert todo.title == "보고서 작성"
        assert todo.status == "pending"

    def test_마감일_포함_추가(self, service):
        todo = service.add_todo("마감일 작업", due_date="2026-12-31")
        assert todo.due_date == "2026-12-31"

    def test_우선순위_포함_추가(self, service):
        todo = service.add_todo("우선 작업", priority="high")
        assert todo.priority == "high"

    def test_빈_제목_저장_거부(self, service):
        with pytest.raises(ValueError):
            service.add_todo("")

    def test_201자_제목_저장_거부(self, service):
        with pytest.raises(ValueError):
            service.add_todo("a" * 201)

    def test_잘못된_날짜_형식_거부(self, service):
        with pytest.raises(ValueError):
            service.add_todo("작업", due_date="31-12-2026")

    def test_잘못된_우선순위_거부(self, service):
        with pytest.raises(ValueError):
            service.add_todo("작업", priority="critical")

    def test_자동_증가_ID(self, service):
        todo1 = service.add_todo("첫 번째")
        todo2 = service.add_todo("두 번째")
        assert todo2.id == todo1.id + 1

    def test_삭제_후_ID_재사용_안함(self, service):
        todo1 = service.add_todo("삭제될 항목")
        first_id = todo1.id
        service.delete_todo(first_id)
        todo2 = service.add_todo("새 항목")
        assert todo2.id > first_id
