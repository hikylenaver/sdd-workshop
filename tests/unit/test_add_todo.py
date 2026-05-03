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

    def test_단일_태그_포함_추가(self, service):
        """단일 태그를 포함하여 추가한다."""
        todo = service.add_todo("작업", tags=["work"])
        assert todo.tags == ["work"]

    def test_다중_태그_포함_추가(self, service):
        """여러 태그를 포함하여 추가한다."""
        todo = service.add_todo("긴급 작업", tags=["work", "urgent"])
        assert todo.tags == ["work", "urgent"]

    def test_태그_없이_추가_하위호환(self, service):
        """태그 없이 추가하는 기존 방식도 지원한다."""
        todo = service.add_todo("태그 없는 작업")
        assert todo.tags == []

    def test_빈_태그_목록_명시_추가(self, service):
        """명시적으로 빈 태그 목록을 전달해도 동작한다."""
        todo = service.add_todo("명시적 빈 태그", tags=[])
        assert todo.tags == []

    def test_태그_검증_6개_오류(self, service):
        """6개 이상 태그는 ValueError를 발생시킨다."""
        with pytest.raises(ValueError, match="태그는 최대 5개"):
            service.add_todo("많은 태그", tags=["a", "b", "c", "d", "e", "f"])

    def test_태그_중복_제거(self, service):
        """중복된 태그는 제거된다."""
        todo = service.add_todo("작업", tags=["work", "work", "urgent"])
        assert todo.tags == ["work", "urgent"]

    def test_태그_마감일_우선순위_조합(self, service):
        """태그와 마감일, 우선순위를 함께 추가할 수 있다."""
        todo = service.add_todo(
            "복합 작업",
            due_date="2026-12-31",
            priority="high",
            tags=["work", "urgent"],
        )
        assert todo.title == "복합 작업"
        assert todo.due_date == "2026-12-31"
        assert todo.priority == "high"
        assert todo.tags == ["work", "urgent"]
