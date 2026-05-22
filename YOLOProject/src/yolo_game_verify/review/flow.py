from yolo_game_verify.generation.models import GeneratedCaseDraft
from yolo_game_verify.models import AssertionResult
from yolo_game_verify.review.models import ReviewDecision, TrialRunResult


def record_human_review(draft: GeneratedCaseDraft, decision: ReviewDecision) -> GeneratedCaseDraft:
    approved = decision.approved and draft.risk_level != "high"
    metadata = draft.review_metadata | {
        "reviewer": decision.reviewer,
        "approved": approved,
        "notes": decision.notes,
    }
    state = "reviewed" if approved else "risk_blocked"
    if not decision.approved:
        state = "rejected"
    return draft.model_copy(update={"review_state": state, "review_metadata": metadata})


def record_trial_run(draft: GeneratedCaseDraft, trial: TrialRunResult) -> GeneratedCaseDraft:
    trial_runs = list(draft.review_metadata.get("trial_runs", []))
    trial_runs.append(trial.model_dump())
    metadata = draft.review_metadata | {"trial_runs": trial_runs}
    state = "trial_passed" if trial.result == AssertionResult.PASS else draft.review_state
    return draft.model_copy(update={"review_state": state, "review_metadata": metadata})


def promote_to_official(draft: GeneratedCaseDraft) -> GeneratedCaseDraft:
    approved = draft.review_metadata.get("approved") is True
    has_passing_trial = any(
        trial.get("result") == AssertionResult.PASS for trial in draft.review_metadata.get("trial_runs", [])
    )
    if not approved or not has_passing_trial:
        return draft
    return draft.model_copy(update={"review_state": "official"})
