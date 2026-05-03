"""고정 DB 경로 및 세션 재실행 영속성 테스트 (T012)."""
import os

from todo_lib.db import create_db_engine, get_db_path, get_session_factory
from todo_lib.models import Todo
from todo_lib.repository import TodoRepository


def test_환경변수로_DB_경로_지정(tmp_path, monkeypatch):
    """TODO_DB_PATH 환경변수가 설정되면 해당 경로를 사용한다."""
    db_file = tmp_path / "test.db"
    monkeypatch.setenv("TODO_DB_PATH", str(db_file))
    assert get_db_path() == str(db_file)


def test_환경변수_없으면_홈_디렉터리_사용(monkeypatch):
    """TODO_DB_PATH가 없으면 ~/.todo/todo.db를 사용한다."""
    monkeypatch.delenv("TODO_DB_PATH", raising=False)
    path = get_db_path()
    assert path.endswith("todo.db")
    assert ".todo" in path


def test_세션_재실행_후_데이터_영속(tmp_db_path):
    """엔진을 재생성해도 이전에 저장된 데이터가 유지된다."""
    # 첫 번째 세션: 데이터 저장
    engine1 = create_db_engine(tmp_db_path)
    session1 = get_session_factory(engine1)()
    repo1 = TodoRepository(session1)
    from datetime import datetime
    todo = Todo(title="영속성 테스트", created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    saved = repo1.add(todo)
    saved_id = saved.id
    session1.close()

    # 두 번째 세션: 데이터 조회
    engine2 = create_db_engine(tmp_db_path)
    session2 = get_session_factory(engine2)()
    repo2 = TodoRepository(session2)
    found = repo2.get_by_id(saved_id)
    assert found is not None
    assert found.title == "영속성 테스트"
    session2.close()
