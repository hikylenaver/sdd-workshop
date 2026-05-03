"""US4: delete 유스케이스 단위 테스트 (T035)."""
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


class TestDeleteTodo:
    def test_pending_항목_삭제(self, service):
        service.add_todo("삭제 대상")
        deleted = service.delete_todo(1)
        assert deleted.title == "삭제 대상"

    def test_done_항목도_삭제_가능(self, service):
        service.add_todo("완료 후 삭제")
        service.mark_done(1)
        deleted = service.delete_todo(1)
        assert deleted.id == 1

    def test_삭제_후_목록에서_사라짐(self, service):
        service.add_todo("A")
        service.add_todo("B")
        service.delete_todo(1)
        todos = service.list_todos()
        assert all(t.id != 1 for t in todos)
        assert len(todos) == 1

    def test_미존재_id_오류(self, service):
        with pytest.raises(LookupError):
            service.delete_todo(9999)

    def test_삭제_후_조회_시_None(self, service):
        service.add_todo("조회 테스트")
        service.delete_todo(1)
        from todo_lib.db import create_db_engine, get_session_factory
        from todo_lib.repository import TodoRepository
        repo = TodoRepository(get_session_factory(create_db_engine(service._repo._session.bind.url.database))())
        assert repo.get_by_id(1) is None
