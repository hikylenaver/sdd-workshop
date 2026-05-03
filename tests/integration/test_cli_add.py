"""US1: add CLI 통합 테스트 (T015)."""
import pytest
from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_add_성공_메시지_출력(tmp_db_path):
    """add 성공 시 ID가 포함된 메시지를 출력한다."""
    result = runner.invoke(app, ["add", "보고서 작성"])
    assert result.exit_code == 0
    assert "ID: 1" in result.output
    assert "보고서 작성" in result.output


def test_add_마감일_포함(tmp_db_path):
    """--due 옵션으로 마감일을 지정할 수 있다."""
    result = runner.invoke(app, ["add", "마감 작업", "--due", "2026-12-31"])
    assert result.exit_code == 0


def test_add_우선순위_포함(tmp_db_path):
    """--priority 옵션으로 우선순위를 지정할 수 있다."""
    result = runner.invoke(app, ["add", "중요 작업", "--priority", "high"])
    assert result.exit_code == 0


def test_add_빈_제목_오류(tmp_db_path):
    """빈 제목은 exit code 2와 오류 메시지를 반환한다."""
    result = runner.invoke(app, ["add", ""])
    assert result.exit_code == 2


def test_add_잘못된_날짜_오류(tmp_db_path):
    """잘못된 날짜 형식은 exit code 2를 반환한다."""
    result = runner.invoke(app, ["add", "작업", "--due", "bad-date"])
    assert result.exit_code == 2


def test_add_잘못된_우선순위_오류(tmp_db_path):
    """허용되지 않는 우선순위는 exit code 2를 반환한다."""
    result = runner.invoke(app, ["add", "작업", "--priority", "urgent"])
    assert result.exit_code == 2


def test_add_여러_항목_순차_ID(tmp_db_path):
    """여러 항목 추가 시 ID가 순차적으로 증가한다."""
    runner.invoke(app, ["add", "첫 번째"])
    result = runner.invoke(app, ["add", "두 번째"])
    assert "ID: 2" in result.output
