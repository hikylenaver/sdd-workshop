"""US3: done CLI 통합 테스트 (T029)."""
import pytest
from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_done_성공_메시지(tmp_db_path):
    """완료 처리 성공 시 메시지를 출력한다."""
    runner.invoke(app, ["add", "할 일"])
    result = runner.invoke(app, ["done", "1"])
    assert result.exit_code == 0
    assert "완료" in result.output


def test_done_이미_완료된_항목_안내(tmp_db_path):
    """이미 완료된 항목은 안내 메시지를 출력하고 exit code 0을 반환한다."""
    runner.invoke(app, ["add", "할 일"])
    runner.invoke(app, ["done", "1"])
    result = runner.invoke(app, ["done", "1"])
    assert result.exit_code == 0
    assert "이미" in result.output


def test_done_미존재_id_오류(tmp_db_path):
    """존재하지 않는 ID는 exit code 1을 반환한다."""
    result = runner.invoke(app, ["done", "9999"])
    assert result.exit_code == 1


def test_done_완료_후_목록_변경(tmp_db_path):
    """완료 처리 후 목록 재조회 시 상태가 변경된다."""
    runner.invoke(app, ["add", "상태 변경 테스트"])
    runner.invoke(app, ["done", "1"])
    result = runner.invoke(app, ["list", "--filter", "done"])
    assert result.exit_code == 0
    assert "done" in result.output
