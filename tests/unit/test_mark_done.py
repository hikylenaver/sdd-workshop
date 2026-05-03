"""US3: mark_done 유스케이스 단위 테스트 (T028)."""
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


class TestMarkDone:
    def test_pending_항목_완료_처리(self, service):
        service.add_todo("완료 테스트")
        todo, already_done = service.mark_done(1)
        assert todo.status == "done"
        assert already_done is False

    def test_이미_완료된_항목_idempotent(self, service):
        service.add_todo("완료 테스트")
        service.mark_done(1)
        todo, already_done = service.mark_done(1)
        assert todo.status == "done"
        assert already_done is True

    def test_미존재_id_오류(self, service):
        with pytest.raises(LookupError):
            service.mark_done(9999)

    def test_완료_후_상태_변경_확인(self, service):
        service.add_todo("상태 확인")
        service.mark_done(1)
        todos = service.list_todos(status="done")
        assert len(todos) == 1
        assert todos[0].id == 1

    def test_완료_후_pending_목록에서_제외(self, service):
        service.add_todo("항목 A")
        service.add_todo("항목 B")
        service.mark_done(1)
        pending = service.list_todos(status="pending")
        assert all(t.id != 1 for t in pending)
