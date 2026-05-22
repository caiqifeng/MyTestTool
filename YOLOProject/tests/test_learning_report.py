import json

from yolo_game_verify.learning.models import LearningSummary
from yolo_game_verify.learning.reporting import write_learning_summary


def test_write_learning_summary(tmp_path):
    summary = LearningSummary(
        total_reports=1,
        result_counts={"pass": 1, "fail": 0, "unknown": 0},
        failure_patterns=[],
        unknown_patterns=[],
        node_confidence=[],
        assertion_confidence=[],
        coverage_gaps=[],
        suggested_cases=[],
    )
    out = tmp_path / "learning.json"

    write_learning_summary(summary, out)

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["total_reports"] == 1
    assert payload["result_counts"]["pass"] == 1
