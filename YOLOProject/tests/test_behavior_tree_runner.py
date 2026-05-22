from yolo_game_verify.behavior.runner import run_behavior_tree
from yolo_game_verify.models import AssertionResult


def test_sequence_passes_when_all_children_pass():
    tree = {
        "type": "sequence",
        "children": [
            {"type": "condition", "name": "main_ui_visible"},
            {"type": "action", "node_name": "ClaimReward"},
        ],
    }

    result = run_behavior_tree(
        tree,
        condition_handlers={"main_ui_visible": lambda: AssertionResult.PASS},
        action_handlers={"ClaimReward": lambda: AssertionResult.PASS},
    )

    assert result.result == AssertionResult.PASS
    assert [event.node_type for event in result.events] == ["condition", "action", "sequence"]


def test_selector_passes_when_second_child_passes():
    tree = {
        "type": "selector",
        "children": [
            {"type": "action", "node_name": "PrimaryNode"},
            {"type": "action", "node_name": "FallbackNode"},
        ],
    }

    result = run_behavior_tree(
        tree,
        condition_handlers={},
        action_handlers={
            "PrimaryNode": lambda: AssertionResult.FAIL,
            "FallbackNode": lambda: AssertionResult.PASS,
        },
    )

    assert result.result == AssertionResult.PASS
