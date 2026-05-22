from collections.abc import Callable
from pathlib import Path

from yolo_game_verify.assertions.temporal import evaluate_temporal_assertion
from yolo_game_verify.cases.evidence import load_step_frames
from yolo_game_verify.cases.models import (
    AssertionEvaluation,
    CaseVerificationReport,
    StepVerificationResult,
    StructuredCase,
)
from yolo_game_verify.models import AssertionResult, EvidenceFrame

FrameEnricher = Callable[[EvidenceFrame], EvidenceFrame]


def _combine_results(results: list[AssertionResult]) -> AssertionResult:
    if any(result == AssertionResult.FAIL for result in results):
        return AssertionResult.FAIL
    if any(result == AssertionResult.UNKNOWN for result in results):
        return AssertionResult.UNKNOWN
    return AssertionResult.PASS


def evaluate_structured_case(
    case: StructuredCase,
    frame_enricher: FrameEnricher | None = None,
) -> CaseVerificationReport:
    step_results: list[StepVerificationResult] = []
    for step in case.steps:
        frames = load_step_frames(Path(step.frame_dir))
        if frame_enricher is not None:
            frames = [frame_enricher(frame) for frame in frames]

        assertion_results: list[AssertionEvaluation] = []
        for assertion in step.assertions:
            result, reason = evaluate_temporal_assertion(assertion, frames)
            assertion_results.append(
                AssertionEvaluation(
                    assertion_id=assertion.assertion_id,
                    result=result,
                    reason=reason,
                )
            )

        step_result = _combine_results([item.result for item in assertion_results])
        reason = "; ".join(item.reason for item in assertion_results) if assertion_results else "no assertions configured"
        step_results.append(
            StepVerificationResult(
                step_id=step.step_id,
                result=step_result,
                reason=reason,
                assertion_results=assertion_results,
                frames=frames,
            )
        )

    case_result = _combine_results([step.result for step in step_results])
    case_reason = "; ".join(step.reason for step in step_results)
    return CaseVerificationReport(
        case_id=case.case_id,
        case_name=case.case_name,
        project=case.project,
        environment=case.environment,
        result=case_result,
        reason=case_reason,
        steps=step_results,
    )
