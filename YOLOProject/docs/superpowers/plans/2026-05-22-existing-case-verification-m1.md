# Existing Case Verification M1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Attach YOLO26/OCR/template functional assertions to existing structured case execution outputs and generate platform-compatible verification reports.

**Architecture:** Build an integration layer on top of the M0 package. It loads a generic structured case JSON, loads frame evidence for each step, evaluates configured assertions per step, and writes an enriched JSON report that can be imported by the current automation platform later.

**Tech Stack:** Python 3.11+, pytest, pydantic, typer, existing `yolo_game_verify` models/assertions/reporting modules.

---

## Scope

This plan implements M1 only:

- Generic structured case input model.
- Assertion configuration attached to case steps.
- Step evidence loading from frame directories.
- Case-level verification runner.
- Enriched report model with step-level functional evidence.
- CLI command to evaluate one existing structured case offline.

It does not implement:

- Real existing platform API integration.
- Real device scheduling.
- Case generation.
- Behavior-tree execution.
- Continuous learning.

## Assumed Structured Case Format

M1 defines a neutral import format that can later be adapted to the real platform:

```json
{
  "case_id": "case_daily_task_001",
  "case_name": "Daily task reward verification",
  "project": "pc_mmorpg",
  "environment": "blackbox",
  "steps": [
    {
      "step_id": "step_001",
      "name": "complete daily task",
      "node_name": "CompleteDailyTask",
      "frame_dir": "frames/step_001",
      "assertions": [
        {
          "assertion_id": "reward_popup_visible",
          "required_label": "reward_popup",
          "min_confidence": 0.5,
          "min_frames": 2
        }
      ]
    }
  ]
}
```

## File Structure

- `src/yolo_game_verify/cases/models.py`: structured case, step, and report models.
- `src/yolo_game_verify/cases/loader.py`: load structured case JSON.
- `src/yolo_game_verify/cases/evidence.py`: load per-step evidence frames from directories.
- `src/yolo_game_verify/cases/runner.py`: evaluate assertions for all case steps.
- `src/yolo_game_verify/cli.py`: add `evaluate-case` command.
- `examples/cases/daily_task_case.json`: example structured case.
- `tests/test_case_models.py`: case model tests.
- `tests/test_case_loader.py`: loader tests.
- `tests/test_case_evidence.py`: frame loading tests.
- `tests/test_case_runner.py`: case runner tests.
- `tests/test_cli_evaluate_case.py`: CLI smoke test.

## Task 1: Structured Case Models

**Files:**
- Create: `src/yolo_game_verify/cases/models.py`
- Create: `src/yolo_game_verify/cases/__init__.py`
- Test: `tests/test_case_models.py`

- [ ] **Step 1: Write failing model tests**

```python
# tests/test_case_models.py
from yolo_game_verify.cases.models import StructuredCase, StructuredStep, StepVerificationResult
from yolo_game_verify.models import AssertionResult, TemporalAssertion


def test_structured_case_contains_steps_and_assertions():
    case = StructuredCase(
        case_id="case_daily_task_001",
        case_name="Daily task reward verification",
        project="pc_mmorpg",
        environment="blackbox",
        steps=[
            StructuredStep(
                step_id="step_001",
                name="complete daily task",
                node_name="CompleteDailyTask",
                frame_dir="frames/step_001",
                assertions=[
                    TemporalAssertion(
                        assertion_id="reward_popup_visible",
                        required_label="reward_popup",
                        min_frames=2,
                    )
                ],
            )
        ],
    )

    assert case.steps[0].assertions[0].required_label == "reward_popup"


def test_step_verification_result_serializes_result_state():
    result = StepVerificationResult(
        step_id="step_001",
        result=AssertionResult.UNKNOWN,
        reason="reward_popup appeared in 1 frame; required 2",
        assertion_results=[],
    )

    assert result.model_dump()["result"] == "unknown"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_case_models.py -q`

Expected: FAIL with missing `yolo_game_verify.cases`.

- [ ] **Step 3: Implement case models**

```python
# src/yolo_game_verify/cases/models.py
from pydantic import BaseModel, Field

from yolo_game_verify.models import AssertionResult, EvidenceFrame, TemporalAssertion


class StructuredStep(BaseModel):
    step_id: str
    name: str
    node_name: str
    frame_dir: str
    assertions: list[TemporalAssertion] = Field(default_factory=list)


class StructuredCase(BaseModel):
    case_id: str
    case_name: str
    project: str
    environment: str
    steps: list[StructuredStep]


class AssertionEvaluation(BaseModel):
    assertion_id: str
    result: AssertionResult
    reason: str


class StepVerificationResult(BaseModel):
    step_id: str
    result: AssertionResult
    reason: str
    assertion_results: list[AssertionEvaluation]
    frames: list[EvidenceFrame] = Field(default_factory=list)


class CaseVerificationReport(BaseModel):
    case_id: str
    case_name: str
    project: str
    environment: str
    result: AssertionResult
    reason: str
    steps: list[StepVerificationResult]
```

- [ ] **Step 4: Create package init**

```python
# src/yolo_game_verify/cases/__init__.py
from yolo_game_verify.cases.models import (
    AssertionEvaluation,
    CaseVerificationReport,
    StepVerificationResult,
    StructuredCase,
    StructuredStep,
)

__all__ = [
    "AssertionEvaluation",
    "CaseVerificationReport",
    "StepVerificationResult",
    "StructuredCase",
    "StructuredStep",
]
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_case_models.py -q`

Expected: `2 passed`

- [ ] **Step 6: Commit**

```powershell
git add YOLOProject/src/yolo_game_verify/cases YOLOProject/tests/test_case_models.py
git commit -m "feat: add structured case models"
```

## Task 2: Structured Case Loader

**Files:**
- Create: `src/yolo_game_verify/cases/loader.py`
- Test: `tests/test_case_loader.py`

- [ ] **Step 1: Write failing loader test**

```python
# tests/test_case_loader.py
import json

from yolo_game_verify.cases.loader import load_structured_case


def test_load_structured_case_from_json(tmp_path):
    case_path = tmp_path / "case.json"
    case_path.write_text(
        json.dumps(
            {
                "case_id": "case_daily_task_001",
                "case_name": "Daily task reward verification",
                "project": "pc_mmorpg",
                "environment": "blackbox",
                "steps": [
                    {
                        "step_id": "step_001",
                        "name": "complete daily task",
                        "node_name": "CompleteDailyTask",
                        "frame_dir": "frames/step_001",
                        "assertions": [
                            {
                                "assertion_id": "reward_popup_visible",
                                "required_label": "reward_popup",
                                "min_confidence": 0.5,
                                "min_frames": 2,
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    case = load_structured_case(case_path)

    assert case.case_id == "case_daily_task_001"
    assert case.steps[0].assertions[0].required_label == "reward_popup"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_case_loader.py -q`

Expected: FAIL with missing loader.

- [ ] **Step 3: Implement loader**

```python
# src/yolo_game_verify/cases/loader.py
import json
from pathlib import Path

from yolo_game_verify.cases.models import StructuredCase


def load_structured_case(case_path: Path) -> StructuredCase:
    payload = json.loads(case_path.read_text(encoding="utf-8"))
    return StructuredCase.model_validate(payload)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_case_loader.py -q`

Expected: `1 passed`

- [ ] **Step 5: Commit**

```powershell
git add YOLOProject/src/yolo_game_verify/cases/loader.py YOLOProject/tests/test_case_loader.py
git commit -m "feat: load structured case json"
```

## Task 3: Step Evidence Loader

**Files:**
- Create: `src/yolo_game_verify/cases/evidence.py`
- Test: `tests/test_case_evidence.py`

- [ ] **Step 1: Write failing evidence loader test**

```python
# tests/test_case_evidence.py
from yolo_game_verify.cases.evidence import load_step_frames


def test_load_step_frames_orders_image_files(synthetic_frame_dir):
    frames = load_step_frames(synthetic_frame_dir)

    assert [frame.frame_index for frame in frames] == [0, 1, 2]
    assert frames[0].image_path.endswith("frame_000.png")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_case_evidence.py -q`

Expected: FAIL with missing evidence loader.

- [ ] **Step 3: Implement evidence loader**

```python
# src/yolo_game_verify/cases/evidence.py
from pathlib import Path

from yolo_game_verify.models import EvidenceFrame


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp"}


def load_step_frames(frame_dir: Path) -> list[EvidenceFrame]:
    image_paths = sorted(path for path in frame_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)
    return [EvidenceFrame.from_path(index, path) for index, path in enumerate(image_paths)]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_case_evidence.py -q`

Expected: `1 passed`

- [ ] **Step 5: Commit**

```powershell
git add YOLOProject/src/yolo_game_verify/cases/evidence.py YOLOProject/tests/test_case_evidence.py
git commit -m "feat: load case step evidence frames"
```

## Task 4: Case Verification Runner

**Files:**
- Create: `src/yolo_game_verify/cases/runner.py`
- Test: `tests/test_case_runner.py`

- [ ] **Step 1: Write failing runner tests**

```python
# tests/test_case_runner.py
from yolo_game_verify.cases.models import StructuredCase, StructuredStep
from yolo_game_verify.cases.runner import evaluate_structured_case
from yolo_game_verify.models import AssertionResult, BoundingBox, Detection, TemporalAssertion


def test_evaluate_structured_case_passes_when_step_assertion_passes(synthetic_frame_dir):
    case = StructuredCase(
        case_id="case_reward",
        case_name="Reward verification",
        project="pc_mmorpg",
        environment="blackbox",
        steps=[
            StructuredStep(
                step_id="step_001",
                name="claim reward",
                node_name="ClaimReward",
                frame_dir=str(synthetic_frame_dir),
                assertions=[
                    TemporalAssertion(
                        assertion_id="reward_popup_visible",
                        required_label="reward_popup",
                        min_frames=2,
                    )
                ],
            )
        ],
    )

    def detector(frame):
        frame.detections.append(
            Detection(
                label="reward_popup",
                bbox=BoundingBox(x1=1, y1=1, x2=20, y2=20),
                confidence=0.9,
                source="fake",
                frame_index=frame.frame_index,
            )
        )
        return frame

    report = evaluate_structured_case(case, frame_enricher=detector)

    assert report.result == AssertionResult.PASS
    assert report.steps[0].assertion_results[0].result == AssertionResult.PASS


def test_evaluate_structured_case_unknown_when_evidence_is_partial(synthetic_frame_dir):
    case = StructuredCase(
        case_id="case_reward",
        case_name="Reward verification",
        project="pc_mmorpg",
        environment="blackbox",
        steps=[
            StructuredStep(
                step_id="step_001",
                name="claim reward",
                node_name="ClaimReward",
                frame_dir=str(synthetic_frame_dir),
                assertions=[
                    TemporalAssertion(
                        assertion_id="reward_popup_visible",
                        required_label="reward_popup",
                        min_frames=2,
                    )
                ],
            )
        ],
    )

    def detector(frame):
        if frame.frame_index == 0:
            frame.detections.append(
                Detection(
                    label="reward_popup",
                    bbox=BoundingBox(x1=1, y1=1, x2=20, y2=20),
                    confidence=0.9,
                    source="fake",
                    frame_index=frame.frame_index,
                )
            )
        return frame

    report = evaluate_structured_case(case, frame_enricher=detector)

    assert report.result == AssertionResult.UNKNOWN
    assert "required 2" in report.reason
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_case_runner.py -q`

Expected: FAIL with missing runner.

- [ ] **Step 3: Implement case runner**

```python
# src/yolo_game_verify/cases/runner.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_case_runner.py -q`

Expected: `2 passed`

- [ ] **Step 5: Commit**

```powershell
git add YOLOProject/src/yolo_game_verify/cases/runner.py YOLOProject/tests/test_case_runner.py
git commit -m "feat: evaluate structured case assertions"
```

## Task 5: Case Report Writer

**Files:**
- Create: `src/yolo_game_verify/cases/reporting.py`
- Test: `tests/test_case_report.py`

- [ ] **Step 1: Write failing report writer test**

```python
# tests/test_case_report.py
import json

from yolo_game_verify.cases.models import CaseVerificationReport
from yolo_game_verify.cases.reporting import write_case_report
from yolo_game_verify.models import AssertionResult


def test_write_case_report(tmp_path):
    report = CaseVerificationReport(
        case_id="case_reward",
        case_name="Reward verification",
        project="pc_mmorpg",
        environment="blackbox",
        result=AssertionResult.PASS,
        reason="reward_popup appeared in 2 frames",
        steps=[],
    )
    out = tmp_path / "case_report.json"

    write_case_report(report, out)

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["case_id"] == "case_reward"
    assert payload["result"] == "pass"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_case_report.py -q`

Expected: FAIL with missing report writer.

- [ ] **Step 3: Implement case report writer**

```python
# src/yolo_game_verify/cases/reporting.py
from pathlib import Path

from yolo_game_verify.cases.models import CaseVerificationReport


def write_case_report(report: CaseVerificationReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_case_report.py -q`

Expected: `1 passed`

- [ ] **Step 5: Commit**

```powershell
git add YOLOProject/src/yolo_game_verify/cases/reporting.py YOLOProject/tests/test_case_report.py
git commit -m "feat: write structured case verification reports"
```

## Task 6: CLI Evaluate Case Command

**Files:**
- Modify: `src/yolo_game_verify/cli.py`
- Test: `tests/test_cli_evaluate_case.py`

- [ ] **Step 1: Write failing CLI test**

```python
# tests/test_cli_evaluate_case.py
import json

from typer.testing import CliRunner

from yolo_game_verify.cli import app


def test_cli_evaluate_case_writes_report(synthetic_frame_dir, tmp_path):
    case_path = tmp_path / "case.json"
    out = tmp_path / "case_report.json"
    case_path.write_text(
        json.dumps(
            {
                "case_id": "case_reward",
                "case_name": "Reward verification",
                "project": "pc_mmorpg",
                "environment": "blackbox",
                "steps": [
                    {
                        "step_id": "step_001",
                        "name": "claim reward",
                        "node_name": "ClaimReward",
                        "frame_dir": str(synthetic_frame_dir),
                        "assertions": [
                            {
                                "assertion_id": "reward_popup_visible",
                                "required_label": "reward_popup",
                                "min_confidence": 0.5,
                                "min_frames": 2,
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["evaluate-case", "--case", str(case_path), "--out", str(out)])

    assert result.exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["case_id"] == "case_reward"
    assert payload["steps"][0]["step_id"] == "step_001"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli_evaluate_case.py -q`

Expected: FAIL because `evaluate-case` command does not exist.

- [ ] **Step 3: Add CLI command**

Append to `src/yolo_game_verify/cli.py`:

```python
from yolo_game_verify.cases.loader import load_structured_case
from yolo_game_verify.cases.reporting import write_case_report
from yolo_game_verify.cases.runner import evaluate_structured_case
```

Add command:

```python
@app.command("evaluate-case")
def evaluate_case(
    case: Path = typer.Option(..., exists=True, file_okay=True, dir_okay=False),
    out: Path = typer.Option(...),
) -> None:
    structured_case = load_structured_case(case)
    report = evaluate_structured_case(structured_case)
    write_case_report(report, out)
    typer.echo(f"{report.result}: {report.reason}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli_evaluate_case.py -q`

Expected: `1 passed`

- [ ] **Step 5: Run full test suite**

Run: `pytest`

Expected: all tests pass.

- [ ] **Step 6: Commit**

```powershell
git add YOLOProject/src/yolo_game_verify/cli.py YOLOProject/tests/test_cli_evaluate_case.py
git commit -m "feat: add structured case evaluation cli"
```

## Task 7: Examples and README

**Files:**
- Create: `examples/cases/daily_task_case.json`
- Modify: `README.md`

- [ ] **Step 1: Add example structured case**

```json
{
  "case_id": "case_daily_task_001",
  "case_name": "Daily task reward verification",
  "project": "pc_mmorpg",
  "environment": "blackbox",
  "steps": [
    {
      "step_id": "step_001",
      "name": "complete daily task",
      "node_name": "CompleteDailyTask",
      "frame_dir": "examples/frames/daily_task/step_001",
      "assertions": [
        {
          "assertion_id": "reward_popup_visible",
          "required_label": "reward_popup",
          "min_confidence": 0.5,
          "min_frames": 2
        },
        {
          "assertion_id": "error_popup_absent_check",
          "required_label": "error_popup",
          "min_confidence": 0.5,
          "min_frames": 1
        }
      ]
    }
  ]
}
```

- [ ] **Step 2: Update README with case evaluation command**

Append to `README.md`:

```markdown
## Evaluate Structured Case

```powershell
yolo-game-verify evaluate-case `
  --case examples\cases\daily_task_case.json `
  --out reports\daily_task_case_report.json
```

The structured case format lets the existing platform attach functional assertions to fixed execution steps without replacing scheduling.
```

- [ ] **Step 3: Run full test suite**

Run: `pytest`

Expected: all tests pass.

- [ ] **Step 4: Commit**

```powershell
git add YOLOProject/README.md YOLOProject/examples/cases/daily_task_case.json
git commit -m "docs: add structured case evaluation example"
```

## Self-Review Checklist

- M1 attaches assertion configuration to existing structured cases through `StructuredStep.assertions`.
- M1 generates enriched functional evidence through `CaseVerificationReport`.
- M1 does not replace existing scheduling or device execution.
- M1 supports task/reward/exception labels through existing `TemporalAssertion.required_label`.
- Case generation is still excluded and remains M2.
- Dynamic execution is still excluded and remains future work.
