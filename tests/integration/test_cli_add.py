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


# US1: 태그 포함 추가 (T017)
def test_add_단일_태그_AC1(tmp_db_path):
    """AC1: --tag work 옵션으로 단일 태그를 지정할 수 있다."""
    result = runner.invoke(app, ["add", "작업", "--tag", "work"])
    assert result.exit_code == 0
    assert "tags=[work]" in result.output


def test_add_다중_태그_AC2(tmp_db_path):
    """AC2: --tag를 여러 번 사용하여 다중 태그를 지정할 수 있다."""
    result = runner.invoke(
        app, ["add", "긴급 작업", "--tag", "work", "--tag", "urgent"]
    )
    assert result.exit_code == 0
    assert "tags=[work, urgent]" in result.output or "tags=[urgent, work]" in result.output


def test_add_최대_5개_태그_AC3(tmp_db_path):
    """AC3: --tag 5개까지 모두 지정할 수 있다."""
    result = runner.invoke(
        app,
        [
            "add",
            "많은 태그",
            "--tag", "tag1",
            "--tag", "tag2",
            "--tag", "tag3",
            "--tag", "tag4",
            "--tag", "tag5",
        ],
    )
    assert result.exit_code == 0
    assert "tags=[" in result.output


def test_add_6개_태그_오류_AC4(tmp_db_path):
    """AC4: --tag 6개 이상은 exit code 2와 오류 메시지를 반환한다."""
    result = runner.invoke(
        app,
        [
            "add",
            "너무 많은 태그",
            "--tag", "tag1",
            "--tag", "tag2",
            "--tag", "tag3",
            "--tag", "tag4",
            "--tag", "tag5",
            "--tag", "tag6",
        ],
    )
    assert result.exit_code == 2
    assert "태그는 최대" in result.output


def test_add_21자_태그_오류_AC5(tmp_db_path):
    """AC5: 21자 이상 태그는 exit code 2와 오류 메시지를 반환한다."""
    result = runner.invoke(app, ["add", "작업", "--tag", "a" * 21])
    assert result.exit_code == 2
    assert "허용되지 않는 문자" in result.output


def test_add_빈_태그_오류_AC6(tmp_db_path):
    """AC6: 빈 태그는 exit code 2와 오류 메시지를 반환한다."""
    result = runner.invoke(app, ["add", "작업", "--tag", ""])
    assert result.exit_code == 2
    assert "빈 값" in result.output or "허용되지 않는" in result.output
