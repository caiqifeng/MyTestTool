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
  --out reports\reward_popup.json
```

The report result is one of:

- `pass`: required evidence appeared in enough frames.
- `fail`: required evidence did not appear.
- `unknown`: evidence appeared but was not stable enough.

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
