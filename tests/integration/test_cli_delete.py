"""US4: delete CLI 통합 테스트 (T036)."""
import pytest
from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


def test_delete_성공_메시지(tmp_db_path):
    """삭제 성공 시 메시지를 출력한다."""
    runner.invoke(app, ["add", "삭제 대상"])
    result = runner.invoke(app, ["delete", "1"])
    assert result.exit_code == 0
    assert "삭제됨" in result.output


def test_delete_미존재_id_오류(tmp_db_path):
    """존재하지 않는 ID는 exit code 1을 반환한다."""
    result = runner.invoke(app, ["delete", "9999"])
    assert result.exit_code == 1


def test_delete_완료된_항목_삭제(tmp_db_path):
    """완료된 항목도 삭제할 수 있다."""
    runner.invoke(app, ["add", "완료 후 삭제"])
    runner.invoke(app, ["done", "1"])
    result = runner.invoke(app, ["delete", "1"])
    assert result.exit_code == 0


def test_delete_후_목록에서_사라짐(tmp_db_path):
    """삭제 후 목록 조회 시 항목이 사라진다."""
    runner.invoke(app, ["add", "A"])
    runner.invoke(app, ["add", "B"])
    runner.invoke(app, ["delete", "1"])
    result = runner.invoke(app, ["list"])
    assert "A" not in result.output
    assert "B" in result.output


def test_delete_pending_done_구분_없이_삭제(tmp_db_path):
    """pending/done 상태에 무관하게 삭제된다."""
    runner.invoke(app, ["add", "pending 항목"])
    runner.invoke(app, ["add", "done 항목"])
    runner.invoke(app, ["done", "2"])
    result1 = runner.invoke(app, ["delete", "1"])
    result2 = runner.invoke(app, ["delete", "2"])
    assert result1.exit_code == 0
    assert result2.exit_code == 0
