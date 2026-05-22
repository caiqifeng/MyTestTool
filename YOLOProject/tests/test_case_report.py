import json

from yolo_game_verify.cases.models import CaseVerificationReport
from yolo_game_verify.cases.reporting import write_case_report
from yolo_game_verify.models import AssertionResult


def test_write_case_report(tmp_path):
    report = CaseVerificationReport(
        case_id="case_reward",
        case_name="Reward verification",
        project="pc_mmorpg",
        environment="blackbox",
        result=AssertionResult.PASS,
        reason="reward_popup appeared in 2 frames",
        steps=[],
    )
    out = tmp_path / "case_report.json"

    write_case_report(report, out)

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["case_id"] == "case_reward"
    assert payload["result"] == "pass"
