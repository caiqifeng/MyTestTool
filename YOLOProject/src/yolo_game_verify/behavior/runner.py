from collections.abc import Callable
from typing import Any

from yolo_game_verify.behavior.models import BehaviorEvent, BehaviorRunResult
from yolo_game_verify.models import AssertionResult

Handler = Callable[[], AssertionResult]


def run_behavior_tree(
    tree: dict[str, Any],
    condition_handlers: dict[str, Handler],
    action_handlers: dict[str, Handler],
) -> BehaviorRunResult:
    events: list[BehaviorEvent] = []

    def run_node(node: dict[str, Any]) -> AssertionResult:
        node_type = node["type"]
        if node_type == "sequence":
            for child in node.get("children", []):
                child_result = run_node(child)
                if child_result != AssertionResult.PASS:
                    events.append(BehaviorEvent(node_type=node_type, name="sequence", result=child_result))
                    return child_result
            events.append(BehaviorEvent(node_type=node_type, name="sequence", result=AssertionResult.PASS))
            return AssertionResult.PASS

        if node_type == "selector":
            last_result = AssertionResult.FAIL
            for child in node.get("children", []):
                last_result = run_node(child)
                if last_result == AssertionResult.PASS:
                    events.append(BehaviorEvent(node_type=node_type, name="selector", result=AssertionResult.PASS))
                    return AssertionResult.PASS
            events.append(BehaviorEvent(node_type=node_type, name="selector", result=last_result))
            return last_result

        if node_type == "condition":
            name = node["name"]
            result = condition_handlers.get(name, lambda: AssertionResult.UNKNOWN)()
            events.append(BehaviorEvent(node_type=node_type, name=name, result=result))
            return result

        if node_type == "action":
            name = node["node_name"]
            result = action_handlers.get(name, lambda: AssertionResult.UNKNOWN)()
            events.append(BehaviorEvent(node_type=node_type, name=name, result=result))
            return result

        events.append(BehaviorEvent(node_type=node_type, name="unsupported", result=AssertionResult.UNKNOWN))
        return AssertionResult.UNKNOWN

    return BehaviorRunResult(result=run_node(tree), events=events)
