from yolo_game_verify.cases.models import (
    AssertionEvaluation,
    CaseVerificationReport,
    StepVerificationResult,
)
from yolo_game_verify.generation.models import NodeCapability
from yolo_game_verify.learning.analyzer import summarize_learning
from yolo_game_verify.models import AssertionResult, TemporalAssertion


def make_report(
    case_id: str,
    result: AssertionResult,
    reason: str,
    assertion_result: AssertionResult,
) -> CaseVerificationReport:
    return CaseVerificationReport(
        case_id=case_id,
        case_name=case_id,
        project="pc_mmorpg",
        environment="blackbox",
        result=result,
        reason=reason,
        steps=[
            StepVerificationResult(
                step_id="step_001",
                result=assertion_result,
                reason=reason,
                assertion_results=[
                    AssertionEvaluation(
                        assertion_id="reward_popup_visible",
                        result=assertion_result,
                        reason=reason,
                    )
                ],
                frames=[],
            )
        ],
    )


def test_summarize_learning_counts_failures_unknowns_and_confidence():
    reports = [
        make_report("case_pass", AssertionResult.PASS, "reward_popup appeared in 2 frames", AssertionResult.PASS),
        make_report("case_fail", AssertionResult.FAIL, "reward_popup did not appear", AssertionResult.FAIL),
        make_report(
            "case_unknown",
            AssertionResult.UNKNOWN,
            "reward_popup appeared in 1 frame; required 2",
            AssertionResult.UNKNOWN,
        ),
    ]
    capabilities = [
        NodeCapability(
            node_name="ClaimReward",
            module="daily_task",
            execution_action="claim reward",
            success_state="reward_popup",
            failure_state="error_popup",
            supported_assertions=[
                TemporalAssertion(
                    assertion_id="reward_popup_visible",
                    required_label="reward_popup",
                    min_frames=2,
                )
            ],
        ),
        NodeCapability(
            node_name="CompleteDailyTask",
            module="daily_task",
            execution_action="complete task",
            success_state="quest_complete_hint",
            failure_state="blocked_flow_hint",
            supported_assertions=[],
        ),
    ]

    summary = summarize_learning(reports, capabilities)

    assert summary.total_reports == 3
    assert summary.result_counts == {"pass": 1, "fail": 1, "unknown": 1}
    assert summary.failure_patterns[0].key == "reward_popup did not appear"
    assert summary.unknown_patterns[0].key == "reward_popup appeared in 1 frame; required 2"
    assert summary.assertion_confidence[0].assertion_id == "reward_popup_visible"
    assert summary.assertion_confidence[0].pass_rate == 1 / 3
    assert "CompleteDailyTask has no supported assertions" in summary.coverage_gaps
    assert "Review failure pattern: reward_popup did not appear" in summary.suggested_cases
