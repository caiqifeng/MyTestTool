# Case Generation Drafts M2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate reviewed test case drafts from historical structured cases and a game node capability library.

**Architecture:** Add a deterministic `generation` package on top of M1 case models. It loads node capabilities, enriches a historical structured case with supported assertions, produces a behavior-tree draft, and writes a JSON draft report for human review and trial execution.

**Tech Stack:** Python 3.11+, pytest, pydantic, typer, existing `yolo_game_verify` models and case modules.

---

## Scope

M2 implements:

- Node capability library model and JSON loader.
- Generated case draft model.
- Deterministic draft generator from one historical structured case.
- Behavior-tree draft output with intent, state checks, node actions, assertions, and recovery.
- Assertion configuration output derived from node capabilities.
- CLI command to generate one draft offline.

M2 does not implement:

- LLM-based generation.
- Human review UI.
- Trial execution promotion workflow.
- Continuous learning.
- Dynamic behavior-tree execution.

## File Structure

- `src/yolo_game_verify/generation/models.py`: node capability, behavior tree, and generated draft models.
- `src/yolo_game_verify/generation/loader.py`: load node capabilities from JSON.
- `src/yolo_game_verify/generation/generator.py`: create generated case drafts.
- `src/yolo_game_verify/generation/reporting.py`: write draft JSON.
- `src/yolo_game_verify/generation/__init__.py`: package exports.
- `src/yolo_game_verify/cli.py`: add `generate-case-draft` command.
- `examples/capabilities/daily_task_nodes.json`: example node capability library.
- `tests/test_generation_models.py`: model tests.
- `tests/test_generation_loader.py`: loader tests.
- `tests/test_case_generator.py`: generator tests.
- `tests/test_generation_report.py`: writer tests.
- `tests/test_cli_generate_case_draft.py`: CLI smoke test.

## Tasks

### Task 1: Generation Models

- [ ] Write failing tests for node capability and draft serialization in `tests/test_generation_models.py`.
- [ ] Run `pytest tests/test_generation_models.py -q` and confirm missing package failure.
- [ ] Implement pydantic models in `src/yolo_game_verify/generation/models.py`.
- [ ] Export models in `src/yolo_game_verify/generation/__init__.py`.
- [ ] Run `pytest tests/test_generation_models.py -q`.
- [ ] Commit with `feat: add case generation draft models`.

### Task 2: Capability Loader

- [ ] Write failing loader test in `tests/test_generation_loader.py`.
- [ ] Run `pytest tests/test_generation_loader.py -q` and confirm missing loader failure.
- [ ] Implement `load_node_capabilities`.
- [ ] Run `pytest tests/test_generation_loader.py -q`.
- [ ] Commit with `feat: load node capability library`.

### Task 3: Draft Generator

- [ ] Write failing generator tests in `tests/test_case_generator.py`.
- [ ] Run `pytest tests/test_case_generator.py -q` and confirm missing generator failure.
- [ ] Implement `generate_case_draft`.
- [ ] Run `pytest tests/test_case_generator.py -q`.
- [ ] Commit with `feat: generate structured case drafts`.

### Task 4: Draft Report Writer

- [ ] Write failing JSON writer test in `tests/test_generation_report.py`.
- [ ] Run `pytest tests/test_generation_report.py -q` and confirm missing writer failure.
- [ ] Implement `write_generated_case_draft`.
- [ ] Run `pytest tests/test_generation_report.py -q`.
- [ ] Commit with `feat: write generated case draft reports`.

### Task 5: CLI Generate Draft

- [ ] Write failing CLI smoke test in `tests/test_cli_generate_case_draft.py`.
- [ ] Run `pytest tests/test_cli_generate_case_draft.py -q` and confirm command failure.
- [ ] Add `generate-case-draft` command to `src/yolo_game_verify/cli.py`.
- [ ] Run `pytest tests/test_cli_generate_case_draft.py -q`.
- [ ] Run full `pytest`.
- [ ] Commit with `feat: add case draft generation cli`.

### Task 6: Examples and Documentation

- [ ] Add `examples/capabilities/daily_task_nodes.json`.
- [ ] Update `README.md` with draft generation usage.
- [ ] Run full `pytest`.
- [ ] Commit with `docs: add case generation draft example`.

## Self-Review Checklist

- Generated draft includes existing platform structured steps.
- Generated draft includes behavior-tree draft.
- Generated draft includes assertion configuration.
- Draft stays in review state and is not promoted automatically.
- Capability evidence records source historical case and matched nodes.
- M2 does not replace scheduling, device management, or M1 verification.
