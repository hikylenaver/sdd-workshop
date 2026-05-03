"""CLI 진입점: Typer 앱 및 명령 등록."""
import sys
from typing import Optional

import typer

from cli import formatters
from todo_lib.db import create_db_engine, get_session_factory
from todo_lib.repository import TodoRepository
from todo_lib.services import TodoService

app = typer.Typer(help="로컬 CLI ToDo 관리 도구")


def _get_service() -> TodoService:
    """서비스 인스턴스를 생성한다."""
    engine = create_db_engine()
    session_factory = get_session_factory(engine)
    session = session_factory()
    repo = TodoRepository(session)
    return TodoService(repo)


@app.command()
def add(
    title: str = typer.Argument(..., help="추가할 할 일 제목"),
    due: Optional[str] = typer.Option(None, "--due", help="마감일 (YYYY-MM-DD)"),
    priority: Optional[str] = typer.Option(None, "--priority", help="우선순위 (high/medium/low)"),
) -> None:
    """새 ToDo 항목을 추가한다."""
    service = _get_service()
    try:
        todo = service.add_todo(title=title, due_date=due, priority=priority)
        typer.echo(formatters.fmt_add_success(todo))
    except ValueError as e:
        typer.echo(formatters.fmt_add_error(str(e)), err=True)
        raise typer.Exit(code=2)


@app.command(name="list")
def list_todos(
    filter_: Optional[str] = typer.Option(None, "--filter", help="상태 필터 (done/pending)"),
    priority: Optional[str] = typer.Option(None, "--priority", help="우선순위 필터 (high/medium/low)"),
) -> None:
    """ToDo 목록을 조회한다."""
    service = _get_service()
    try:
        todos = service.list_todos(status=filter_, priority=priority)
    except ValueError as e:
        typer.echo(formatters.fmt_add_error(str(e)), err=True)
        raise typer.Exit(code=2)

    if not todos:
        typer.echo(formatters.fmt_list_empty())
    else:
        typer.echo(formatters.fmt_list_todos(todos))


@app.command()
def done(
    todo_id: int = typer.Argument(..., help="완료 처리할 항목 ID"),
) -> None:
    """ToDo 항목을 완료 처리한다."""
    service = _get_service()
    try:
        todo, already_done = service.mark_done(todo_id)
        if already_done:
            typer.echo(formatters.fmt_done_already(todo))
        else:
            typer.echo(formatters.fmt_done_success(todo))
    except LookupError as e:
        typer.echo(formatters.fmt_done_error(str(e)), err=True)
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(formatters.fmt_done_error(str(e)), err=True)
        raise typer.Exit(code=2)


@app.command()
def delete(
    todo_id: int = typer.Argument(..., help="삭제할 항목 ID"),
) -> None:
    """ToDo 항목을 영구 삭제한다."""
    service = _get_service()
    try:
        todo = service.delete_todo(todo_id)
        typer.echo(formatters.fmt_delete_success(todo))
    except LookupError as e:
        typer.echo(formatters.fmt_delete_error(str(e)), err=True)
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(formatters.fmt_delete_error(str(e)), err=True)
        raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
