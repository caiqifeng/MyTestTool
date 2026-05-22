import json

from yolo_game_verify.models import AssertionResult, VerificationReport
from yolo_game_verify.reporting.json_report import write_json_report


def test_write_json_report(tmp_path):
    report = VerificationReport(
        case_id="case_reward",
        result=AssertionResult.PASS,
        reason="reward_popup appeared in 2 frames",
        frames=[],
    )
    out = tmp_path / "report.json"

    write_json_report(report, out)

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["case_id"] == "case_reward"
    assert payload["result"] == "pass"
    assert payload["reason"] == "reward_popup appeared in 2 frames"
