from yolo_game_verify.cases.models import StructuredCase
from yolo_game_verify.generation.models import BehaviorTreeDraft, GeneratedCaseDraft, NodeCapability
from yolo_game_verify.models import TemporalAssertion

RISK_ORDER = {"low": 0, "medium": 1, "high": 2}


def _highest_risk(risk_levels: list[str]) -> str:
    if not risk_levels:
        return "medium"
    return max(risk_levels, key=lambda value: RISK_ORDER[value])


def generate_case_draft(
    historical_case: StructuredCase,
    capabilities: list[NodeCapability],
) -> GeneratedCaseDraft:
    capabilities_by_node = {capability.node_name: capability for capability in capabilities}
    structured_payload = historical_case.model_dump()
    structured_payload["case_id"] = f"draft_{historical_case.case_id}"
    structured_payload["case_name"] = f"Generated {historical_case.case_name}"

    assertion_config: list[TemporalAssertion] = []
    generation_evidence: list[str] = []
    behavior_children: list[dict[str, object]] = []
    risk_levels: list[str] = []

    for step_payload, step in zip(structured_payload["steps"], historical_case.steps, strict=True):
        capability = capabilities_by_node.get(step.node_name)
        assertions = step.assertions
        if capability is None:
            generation_evidence.append(f"no capability match for {step.node_name}")
            risk_levels.append("medium")
        else:
            assertions = capability.supported_assertions or step.assertions
            generation_evidence.append(f"matched node {step.node_name} from historical case")
            risk_levels.append(capability.risk_level)

        step_payload["assertions"] = [assertion.model_dump() for assertion in assertions]
        assertion_config.extend(assertions)
        behavior_children.append(
            {
                "type": "action",
                "step_id": step.step_id,
                "node_name": step.node_name,
                "preconditions": capability.preconditions if capability is not None else [],
                "success_state": capability.success_state if capability is not None else None,
                "failure_recovery": capability.failure_state if capability is not None else "manual_review",
                "assertions": [assertion.assertion_id for assertion in assertions],
            }
        )

    behavior_tree = BehaviorTreeDraft(
        intent=f"Generate reviewed draft from {historical_case.case_name}",
        root={"type": "sequence", "children": behavior_children},
    )

    return GeneratedCaseDraft(
        draft_id=f"draft_{historical_case.case_id}",
        source_case_id=historical_case.case_id,
        review_state="draft",
        structured_case=structured_payload,
        behavior_tree=behavior_tree,
        assertion_config=assertion_config,
        generation_evidence=generation_evidence,
        risk_level=_highest_risk(risk_levels),
    )
