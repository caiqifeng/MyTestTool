# YOLO Game Verify

Black-box functional verification prototype for game automation.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Run Tests

```powershell
pytest
```

## Evaluate Frame Directory

```powershell
yolo-game-verify evaluate-frames `
  --frames path\to\frames `
  --required-label reward_popup `
  --min-frames 2 `
  --out reports\reward_popup.json `
  --context examples\context\pc_mmorpg_blackbox.json
```

Template matching can be used for deterministic local smoke runs:

```powershell
yolo-game-verify evaluate-frames `
  --frames path\to\frames `
  --required-label reward_popup `
  --min-frames 1 `
  --template path\to\reward_template.png `
  --template-label reward_popup `
  --out reports\reward_popup.json
```

The report result is one of:

- `pass`: required evidence appeared in enough frames.
- `fail`: required evidence did not appear.
- `unknown`: evidence appeared but was not stable enough.

Assertions default to `"expected": "present"`. Use `"expected": "absent"` for exception UI checks such as `error_popup` or `network_error`.

## First MVP Labels

- `quest_tracker`
- `quest_complete_hint`
- `reward_popup`
- `claim_reward_button`
- `reward_text_area`
- `error_popup`
- `network_error`
- `blocked_flow_hint`

## Evaluate Structured Case

```powershell
yolo-game-verify evaluate-case `
  --case examples\cases\daily_task_case.json `
  --out reports\daily_task_case_report.json
```

The structured case format lets the existing platform attach functional assertions to fixed execution steps without replacing scheduling.

## Generate Case Draft

```powershell
yolo-game-verify generate-case-draft `
  --case examples\cases\daily_task_case.json `
  --capabilities examples\capabilities\daily_task_nodes.json `
  --out reports\daily_task_draft.json
```

Generated drafts include compatible structured steps, a behavior-tree draft, assertion configuration, generation evidence, risk level, and a `draft` review state.

## Review Generated Draft

```powershell
yolo-game-verify review-draft --draft reports\daily_task_draft.json --reviewer qa_lead --approved --out reports\daily_task_reviewed.json
yolo-game-verify trial-draft --draft reports\daily_task_reviewed.json --run-id trial_001 --result pass --report-path reports\trial.json --out reports\daily_task_trialed.json
yolo-game-verify promote-draft --draft reports\daily_task_trialed.json --out reports\daily_task_official.json
```

Generated cases only become `official` after human approval and at least one passing trial run. High-risk drafts are blocked for manual review.

## Dry-Run Behavior Tree Draft

```powershell
yolo-game-verify run-behavior-draft `
  --draft reports\daily_task_draft.json `
  --out reports\behavior_dry_run.json
```

The dry-run runner validates behavior-tree structure with injected handlers. It does not execute game actions or replace the platform scheduler.

## Summarize Learning Signals

```powershell
yolo-game-verify summarize-learning `
  --reports examples\learning `
  --capabilities examples\capabilities\daily_task_nodes.json `
  --out reports\learning_summary.json `
  --context examples\context\pc_mmorpg_blackbox.json
```

Learning summaries aggregate observed verification reports into failure patterns, unknown evidence patterns, assertion confidence, node confidence, coverage gaps, and suggested review actions.

The optional context file binds outputs to project, game version, model version, dataset version, environment, and execution id.

## Prepare Dataset Manifest

```powershell
yolo-game-verify prepare-dataset `
  --frames path\to\historical\frames `
  --project pc_mmorpg `
  --game-version 1.2.3 `
  --environment blackbox `
  --out reports\dataset_manifest.json
```

Dataset manifests record image dimensions, SHA-256 hashes, duplicate relationships, and project/version/environment tags for labeling and replay evaluation.
