from yolo_game_verify.generation.models import BehaviorTreeDraft, GeneratedCaseDraft
from yolo_game_verify.review.flow import record_human_review, record_trial_run, promote_to_official
from yolo_game_verify.review.models import ReviewDecision, TrialRunResult
from yolo_game_verify.models import AssertionResult


def make_draft(risk_level: str = "low") -> GeneratedCaseDraft:
    return GeneratedCaseDraft(
        draft_id="draft_case_reward",
        source_case_id="case_reward",
        structured_case={
            "case_id": "draft_case_reward",
            "case_name": "Generated reward verification",
            "project": "pc_mmorpg",
            "environment": "blackbox",
            "steps": [],
        },
        behavior_tree=BehaviorTreeDraft(intent="verify reward", root={"type": "sequence", "children": []}),
        assertion_config=[],
        generation_evidence=[],
        risk_level=risk_level,
    )


def test_review_flow_promotes_after_approval_and_passing_trial():
    reviewed = record_human_review(
        make_draft(),
        ReviewDecision(reviewer="qa_lead", approved=True, notes="ok"),
    )
    trialed = record_trial_run(
        reviewed,
        TrialRunResult(run_id="trial_001", result=AssertionResult.PASS, report_path="reports/trial.json"),
    )

    promoted = promote_to_official(trialed)

    assert promoted.review_state == "official"
    assert promoted.review_metadata["reviewer"] == "qa_lead"
    assert promoted.review_metadata["trial_runs"][0]["run_id"] == "trial_001"


def test_high_risk_draft_requires_rejection_or_manual_downgrade():
    reviewed = record_human_review(
        make_draft(risk_level="high"),
        ReviewDecision(reviewer="qa_lead", approved=True, notes="too risky"),
    )

    assert reviewed.review_state == "risk_blocked"
    assert reviewed.review_metadata["approved"] is False
