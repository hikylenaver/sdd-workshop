"""CLI 출력 포맷 함수 모음."""
from todo_lib.models import Todo


def fmt_todo_row(todo: Todo) -> str:
    """단일 Todo를 한 줄 문자열로 포맷한다."""
    due = todo.due_date or "-"
    priority = todo.priority or "-"
    tags_str = f"[{', '.join(todo.tags)}]" if todo.tags else "[]"
    return f"[{todo.id}] {todo.title}  due={due}  priority={priority}  status={todo.status}  tags={tags_str}"


def fmt_add_success(todo: Todo) -> str:
    """추가 성공 메시지."""
    tags_str = f" tags=[{', '.join(todo.tags)}]" if todo.tags else " tags=[]"
    return f"추가됨 (ID: {todo.id}): {todo.title}{tags_str}"


def fmt_add_error(message: str) -> str:
    """추가 실패 메시지."""
    return f"오류: {message}"


def fmt_list_empty() -> str:
    """목록이 비어 있을 때 메시지."""
    return "저장된 항목이 없습니다."


def fmt_list_todos(todos: list[Todo]) -> str:
    """Todo 목록을 여러 줄 문자열로 포맷한다."""
    header = f"{'ID':<5} {'제목':<30} {'마감일':<12} {'우선순위':<10} {'상태'}"
    separator = "-" * 72
    rows = [f"{t.id:<5} {t.title:<30} {t.due_date or '-':<12} {t.priority or '-':<10} {t.status}" for t in todos]
    return "\n".join([header, separator] + rows)


def fmt_done_success(todo: Todo) -> str:
    """완료 처리 성공 메시지."""
    return f"완료 처리됨 (ID: {todo.id}): {todo.title}"


def fmt_done_already(todo: Todo) -> str:
    """이미 완료된 항목 안내 메시지."""
    return f"이미 완료된 항목입니다 (ID: {todo.id}): {todo.title}"


def fmt_done_error(message: str) -> str:
    """완료 처리 실패 메시지."""
    return f"오류: {message}"


def fmt_delete_success(todo: Todo) -> str:
    """삭제 성공 메시지."""
    return f"삭제됨 (ID: {todo.id}): {todo.title}"


def fmt_delete_error(message: str) -> str:
    """삭제 실패 메시지."""
    return f"오류: {message}"
