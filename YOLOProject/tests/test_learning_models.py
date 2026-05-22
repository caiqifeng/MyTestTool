from yolo_game_verify.learning.models import (
    AssertionConfidence,
    LearningSummary,
    NodeConfidence,
    PatternSummary,
)


def test_learning_summary_serializes_patterns_and_confidence():
    summary = LearningSummary(
        total_reports=3,
        result_counts={"pass": 1, "fail": 1, "unknown": 1},
        failure_patterns=[
            PatternSummary(
                key="reward_popup did not appear",
                count=1,
                case_ids=["case_reward"],
            )
        ],
        unknown_patterns=[
            PatternSummary(
                key="reward evidence was unstable",
                count=1,
                case_ids=["case_reward_partial"],
            )
        ],
        node_confidence=[
            NodeConfidence(node_name="ClaimReward", pass_rate=0.5, observed_runs=2),
        ],
        assertion_confidence=[
            AssertionConfidence(assertion_id="reward_popup_visible", pass_rate=0.5, observed_runs=2),
        ],
        coverage_gaps=["CompleteDailyTask has no supported assertions"],
        suggested_cases=["Add review for ClaimReward failure pattern"],
    )

    payload = summary.model_dump()

    assert payload["total_reports"] == 3
    assert payload["failure_patterns"][0]["case_ids"] == ["case_reward"]
    assert payload["node_confidence"][0]["node_name"] == "ClaimReward"
