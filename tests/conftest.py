"""공통 테스트 fixture."""
import os
import tempfile
import pytest
from typer.testing import CliRunner


@pytest.fixture
def tmp_db_path(tmp_path, monkeypatch):
    """테스트용 임시 SQLite DB 경로를 반환하고 환경변수로 주입한다."""
    db_file = tmp_path / "todo.db"
    monkeypatch.setenv("TODO_DB_PATH", str(db_file))
    return str(db_file)


@pytest.fixture
def cli_runner():
    """Typer CLI 테스트 러너를 반환한다."""
    return CliRunner()
