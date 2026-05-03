"""US2: list CLI 통합 테스트 (T022)."""
import pytest
from typer.testing import CliRunner

from cli.main import app

runner = CliRunner()


@pytest.fixture
def populated_db(tmp_db_path):
    """시드 데이터가 있는 임시 DB."""
    runner.invoke(app, ["add", "첫 번째", "--priority", "high"])
    runner.invoke(app, ["add", "두 번째", "--priority", "low"])
    runner.invoke(app, ["add", "세 번째", "--priority", "high"])
    runner.invoke(app, ["done", "3"])
    return tmp_db_path


def test_list_빈_목록_메시지(tmp_db_path):
    """항목이 없으면 안내 메시지를 출력한다."""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "없습니다" in result.output


def test_list_전체_목록_출력(populated_db):
    """전체 목록을 출력한다."""
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "첫 번째" in result.output
    assert "두 번째" in result.output
    assert "세 번째" in result.output


def test_list_filter_pending(populated_db):
    """--filter pending으로 미완료 항목만 출력한다."""
    result = runner.invoke(app, ["list", "--filter", "pending"])
    assert result.exit_code == 0
    assert "pending" in result.output


def test_list_filter_done(populated_db):
    """--filter done으로 완료 항목만 출력한다."""
    result = runner.invoke(app, ["list", "--filter", "done"])
    assert result.exit_code == 0
    assert "done" in result.output


def test_list_priority_high(populated_db):
    """--priority high로 high 우선순위 항목만 출력한다."""
    result = runner.invoke(app, ["list", "--priority", "high"])
    assert result.exit_code == 0
    assert "high" in result.output


def test_list_조합_필터(populated_db):
    """--filter와 --priority를 동시에 사용할 수 있다."""
    result = runner.invoke(app, ["list", "--filter", "pending", "--priority", "high"])
    assert result.exit_code == 0


def test_list_잘못된_filter_오류(tmp_db_path):
    """유효하지 않은 --filter 값은 exit code 2를 반환한다."""
    result = runner.invoke(app, ["list", "--filter", "bad"])
    assert result.exit_code == 2


# US2: 태그로 목록 필터링 (T025)
@pytest.fixture
def tagged_db(tmp_db_path):
    """태그가 있는 시드 데이터."""
    runner.invoke(app, ["add", "업무1", "--tag", "work"])
    runner.invoke(app, ["add", "업무2", "--tag", "work", "--tag", "urgent"])
    runner.invoke(app, ["add", "개인작업", "--tag", "personal"])
    return tmp_db_path


def test_list_tag_work_AC1(tagged_db):
    """AC1: --tag work로 'work' 태그를 가진 항목만 출력한다."""
    result = runner.invoke(app, ["list", "--tag", "work"])
    assert result.exit_code == 0
    assert "업무1" in result.output
    assert "업무2" in result.output
    assert "개인작업" not in result.output


def test_list_tag_personal_AC2(tagged_db):
    """AC2: --tag personal로 'personal' 태그를 가진 항목만 출력한다."""
    result = runner.invoke(app, ["list", "--tag", "personal"])
    assert result.exit_code == 0
    assert "개인작업" in result.output
    assert "업무1" not in result.output


def test_list_tag_없는_태그_AC3(tagged_db):
    """AC3: 존재하지 않는 태그로 필터하면 '없습니다' 메시지를 출력한다."""
    result = runner.invoke(app, ["list", "--tag", "notfound"])
    assert result.exit_code == 0
    assert "없습니다" in result.output


def test_list_tag_filter_조합_AC4(tagged_db):
    """AC4: --tag와 --filter를 함께 사용할 수 있다."""
    result = runner.invoke(app, ["list", "--tag", "work", "--filter", "pending"])
    assert result.exit_code == 0
    # work 태그를 가진 pending 항목들이 출력


def test_list_tag_priority_조합_AC5(tagged_db):
    """AC5: --tag와 --priority를 함께 사용할 수 있다."""
    result = runner.invoke(app, ["list", "--tag", "work", "--priority", "high"])
    assert result.exit_code == 0
    # work 태그를 가진 high 우선순위 항목들이 출력
