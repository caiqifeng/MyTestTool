from yolo_game_verify.cases.models import CaseVerificationReport
from yolo_game_verify.learning.loader import load_case_reports
from yolo_game_verify.models import AssertionResult


def test_load_case_reports_orders_json_files(tmp_path):
    first = CaseVerificationReport(
        case_id="case_a",
        case_name="Case A",
        project="pc_mmorpg",
        environment="blackbox",
        result=AssertionResult.PASS,
        reason="ok",
        steps=[],
    )
    second = CaseVerificationReport(
        case_id="case_b",
        case_name="Case B",
        project="pc_mmorpg",
        environment="blackbox",
        result=AssertionResult.FAIL,
        reason="reward_popup did not appear",
        steps=[],
    )
    (tmp_path / "b.json").write_text(second.model_dump_json(), encoding="utf-8")
    (tmp_path / "a.json").write_text(first.model_dump_json(), encoding="utf-8")

    reports = load_case_reports(tmp_path)

    assert [report.case_id for report in reports] == ["case_a", "case_b"]
