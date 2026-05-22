from collections import Counter, defaultdict

from yolo_game_verify.cases.models import CaseVerificationReport
from yolo_game_verify.generation.models import NodeCapability
from yolo_game_verify.learning.models import (
    AssertionConfidence,
    LearningSummary,
    NodeConfidence,
    PatternSummary,
)
from yolo_game_verify.models import AssertionResult


def _pattern_summaries(patterns: dict[str, list[str]]) -> list[PatternSummary]:
    return [
        PatternSummary(key=key, count=len(case_ids), case_ids=case_ids)
        for key, case_ids in sorted(patterns.items(), key=lambda item: (-len(item[1]), item[0]))
    ]


def summarize_learning(
    reports: list[CaseVerificationReport],
    capabilities: list[NodeCapability],
) -> LearningSummary:
    result_counts = Counter(report.result.value for report in reports)
    for result in AssertionResult:
        result_counts.setdefault(result.value, 0)

    failure_patterns: dict[str, list[str]] = defaultdict(list)
    unknown_patterns: dict[str, list[str]] = defaultdict(list)
    assertion_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for report in reports:
        if report.result == AssertionResult.FAIL:
            failure_patterns[report.reason].append(report.case_id)
        elif report.result == AssertionResult.UNKNOWN:
            unknown_patterns[report.reason].append(report.case_id)

        for step in report.steps:
            for assertion in step.assertion_results:
                assertion_counts[assertion.assertion_id][assertion.result.value] += 1

    assertion_confidence = []
    for assertion_id, counts in sorted(assertion_counts.items()):
        observed_runs = sum(counts.values())
        pass_rate = counts[AssertionResult.PASS.value] / observed_runs if observed_runs else 0.0
        assertion_confidence.append(
            AssertionConfidence(
                assertion_id=assertion_id,
                pass_rate=pass_rate,
                observed_runs=observed_runs,
            )
        )

    node_confidence = [
        NodeConfidence(
            node_name=capability.node_name,
            pass_rate=next(
                (
                    confidence.pass_rate
                    for confidence in assertion_confidence
                    if any(assertion.assertion_id == confidence.assertion_id for assertion in capability.supported_assertions)
                ),
                0.0,
            ),
            observed_runs=next(
                (
                    confidence.observed_runs
                    for confidence in assertion_confidence
                    if any(assertion.assertion_id == confidence.assertion_id for assertion in capability.supported_assertions)
                ),
                0,
            ),
        )
        for capability in capabilities
    ]

    coverage_gaps = [
        f"{capability.node_name} has no supported assertions"
        for capability in capabilities
        if not capability.supported_assertions
    ]
    suggested_cases = [f"Review failure pattern: {pattern}" for pattern in sorted(failure_patterns)]
    suggested_cases.extend(f"Investigate unstable evidence: {pattern}" for pattern in sorted(unknown_patterns))

    return LearningSummary(
        total_reports=len(reports),
        result_counts=dict(sorted(result_counts.items())),
        failure_patterns=_pattern_summaries(failure_patterns),
        unknown_patterns=_pattern_summaries(unknown_patterns),
        node_confidence=node_confidence,
        assertion_confidence=assertion_confidence,
        coverage_gaps=coverage_gaps,
        suggested_cases=suggested_cases,
    )
