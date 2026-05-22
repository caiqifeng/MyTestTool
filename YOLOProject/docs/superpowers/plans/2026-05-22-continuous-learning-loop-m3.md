# Continuous Learning Loop M3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Summarize execution traces and feed reviewed learning signals back into node capability confidence and case suggestions.

**Architecture:** Add a deterministic `learning` package that reads M1 case verification reports and M2 capability libraries. It aggregates pass/fail/unknown outcomes, identifies weak assertions and missing node coverage, updates confidence metadata, and writes a learning summary JSON for human review.

**Tech Stack:** Python 3.11+, pytest, pydantic, typer, existing `yolo_game_verify` case, generation, and model modules.

---

## Scope

M3 implements:

- Execution trace input model for case verification report JSON files.
- Failure and unknown pattern summaries.
- Assertion confidence and node confidence calculations.
- Missing coverage discovery for nodes without supported assertions.
- Suggested case and assertion improvement records.
- CLI command to summarize learning from a report directory.

M3 does not implement:

- Online learning or model retraining.
- Automatic promotion of generated cases.
- Direct scheduling platform integration.
- Dynamic execution.

## File Structure

- `src/yolo_game_verify/learning/models.py`: learning summary models.
- `src/yolo_game_verify/learning/loader.py`: load case verification reports from a directory.
- `src/yolo_game_verify/learning/analyzer.py`: summarize outcomes and update capability confidence.
- `src/yolo_game_verify/learning/reporting.py`: write learning summary JSON.
- `src/yolo_game_verify/learning/__init__.py`: package exports.
- `src/yolo_game_verify/cli.py`: add `summarize-learning` command.
- `examples/learning/case_reward_fail.json`: sample report.
- `tests/test_learning_models.py`
- `tests/test_learning_loader.py`
- `tests/test_learning_analyzer.py`
- `tests/test_learning_report.py`
- `tests/test_cli_summarize_learning.py`

## Tasks

### Task 1: Learning Models

- [ ] Write failing model tests.
- [ ] Run `pytest tests/test_learning_models.py -q` and confirm missing package failure.
- [ ] Implement learning pydantic models.
- [ ] Export package models.
- [ ] Run `pytest tests/test_learning_models.py -q`.
- [ ] Commit with `feat: add learning summary models`.

### Task 2: Report Loader

- [ ] Write failing directory loader tests.
- [ ] Run `pytest tests/test_learning_loader.py -q` and confirm missing loader failure.
- [ ] Implement `load_case_reports`.
- [ ] Run `pytest tests/test_learning_loader.py -q`.
- [ ] Commit with `feat: load learning trace reports`.

### Task 3: Learning Analyzer

- [ ] Write failing analyzer tests for failure summaries, confidence, and coverage gaps.
- [ ] Run `pytest tests/test_learning_analyzer.py -q` and confirm missing analyzer failure.
- [ ] Implement `summarize_learning`.
- [ ] Run `pytest tests/test_learning_analyzer.py -q`.
- [ ] Commit with `feat: summarize execution learning signals`.

### Task 4: Learning Report Writer

- [ ] Write failing writer test.
- [ ] Run `pytest tests/test_learning_report.py -q` and confirm missing writer failure.
- [ ] Implement `write_learning_summary`.
- [ ] Run `pytest tests/test_learning_report.py -q`.
- [ ] Commit with `feat: write learning summary reports`.

### Task 5: CLI Summarize Learning

- [ ] Write failing CLI smoke test.
- [ ] Run `pytest tests/test_cli_summarize_learning.py -q` and confirm missing command failure.
- [ ] Add `summarize-learning` command.
- [ ] Run `pytest tests/test_cli_summarize_learning.py -q`.
- [ ] Run full `pytest`.
- [ ] Commit with `feat: add learning summary cli`.

### Task 6: Examples and Documentation

- [ ] Add example learning report JSON.
- [ ] Update README with learning command.
- [ ] Run full `pytest`.
- [ ] Commit with `docs: add continuous learning example`.

## Self-Review Checklist

- Learning records distinguish observed reports from inferred suggestions.
- Unknown results are not counted as pass.
- Missing assertion coverage is surfaced for human review.
- Capability confidence remains reviewable metadata, not automatic promotion.
- M3 does not replace scheduling or model training.
