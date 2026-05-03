"""CLI 명령 시그니처/옵션 계약 테스트 (T013, T020, T027, T034, T041)."""
import pytest
from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


class TestAddContract:
    """todo add 명령 시그니처 계약."""

    def test_add_title_인자_필수(self):
        """제목 없이 호출하면 exit code 2를 반환한다."""
        result = runner.invoke(app, ["add"])
        assert result.exit_code == 2

    def test_add_due_옵션_존재(self, tmp_db_path):
        """--due 옵션이 존재한다."""
        result = runner.invoke(app, ["add", "테스트", "--due", "2026-12-31"])
        assert result.exit_code == 0

    def test_add_priority_옵션_존재(self, tmp_db_path):
        """--priority 옵션이 존재한다."""
        result = runner.invoke(app, ["add", "테스트", "--priority", "high"])
        assert result.exit_code == 0

    def test_add_성공_exit_code_0(self, tmp_db_path):
        """성공 시 exit code 0을 반환한다."""
        result = runner.invoke(app, ["add", "할 일 항목"])
        assert result.exit_code == 0

    def test_add_검증_실패_exit_code_2(self, tmp_db_path):
        """검증 실패 시 exit code 2를 반환한다."""
        result = runner.invoke(app, ["add", ""])
        assert result.exit_code == 2


class TestListContract:
    """todo list 명령 옵션 계약."""

    def test_list_filter_옵션_존재(self, tmp_db_path):
        """--filter 옵션이 존재한다."""
        result = runner.invoke(app, ["list", "--filter", "pending"])
        assert result.exit_code == 0

    def test_list_priority_옵션_존재(self, tmp_db_path):
        """--priority 옵션이 존재한다."""
        result = runner.invoke(app, ["list", "--priority", "high"])
        assert result.exit_code == 0

    def test_list_옵션_없이_호출_가능(self, tmp_db_path):
        """옵션 없이 호출해도 exit code 0을 반환한다."""
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0

    def test_list_잘못된_filter_exit_code_2(self, tmp_db_path):
        """유효하지 않은 --filter 값은 exit code 2를 반환한다."""
        result = runner.invoke(app, ["list", "--filter", "invalid"])
        assert result.exit_code == 2


class TestDoneContract:
    """todo done <id> 계약."""

    def test_done_id_인자_필수(self):
        """ID 없이 호출하면 exit code 2를 반환한다."""
        result = runner.invoke(app, ["done"])
        assert result.exit_code == 2

    def test_done_미존재_id_exit_code_1(self, tmp_db_path):
        """존재하지 않는 ID는 exit code 1을 반환한다."""
        result = runner.invoke(app, ["done", "9999"])
        assert result.exit_code == 1

    def test_done_성공_exit_code_0(self, tmp_db_path):
        """성공 시 exit code 0을 반환한다."""
        runner.invoke(app, ["add", "완료 테스트"])
        result = runner.invoke(app, ["done", "1"])
        assert result.exit_code == 0


class TestDeleteContract:
    """todo delete <id> 계약."""

    def test_delete_id_인자_필수(self):
        """ID 없이 호출하면 exit code 2를 반환한다."""
        result = runner.invoke(app, ["delete"])
        assert result.exit_code == 2

    def test_delete_미존재_id_exit_code_1(self, tmp_db_path):
        """존재하지 않는 ID는 exit code 1을 반환한다."""
        result = runner.invoke(app, ["delete", "9999"])
        assert result.exit_code == 1

    def test_delete_성공_exit_code_0(self, tmp_db_path):
        """성공 시 exit code 0을 반환한다."""
        runner.invoke(app, ["add", "삭제 테스트"])
        result = runner.invoke(app, ["delete", "1"])
        assert result.exit_code == 0


class TestExitCodeCommon:
    """Exit Code 공통 검증 (T041)."""

    def test_알_수_없는_명령_exit_code_2(self):
        result = runner.invoke(app, ["unknown-command"])
        assert result.exit_code == 2
