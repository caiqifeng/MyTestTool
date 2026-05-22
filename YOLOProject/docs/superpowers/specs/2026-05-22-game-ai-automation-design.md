# Game AI Automation System Design

## Background

The current automation platform already supports project/environment/case-set selection, execution device selection, task distribution to multiple machines, and long-running stability execution. It can detect whether the game is stuck, crashed, or abnormally exited.

The current gaps are:

- Existing cases are fixed structured step sequences. When nodes, UI, flow, or game states change, cases stop working.
- The system can tell whether the game is alive, but cannot reliably verify whether game functionality is correct.
- Case authoring is labor-heavy. Testers must manually compose game nodes for every case.
- The team wants the system to learn from long-running executions and generate better functional test cases over time.

This design enhances the existing platform rather than rebuilding scheduling.

Engineering repository for future implementation:

- https://github.com/caiqifeng/MyTestTool

## Goals

1. Add black-box functional verification using YOLO26, OCR, screenshots, and temporal visual evidence.
2. Generate test case drafts from historical structured cases and the game node/API capability library.
3. Produce three outputs for generated cases: existing platform structured steps, behavior-tree draft, and assertion configuration.
4. Support long-term learning from large-scale machine execution to improve test coverage and generated cases.
5. Preserve existing scheduling, device distribution, and long-running execution infrastructure.

## Non-Goals

- Rebuilding the current task scheduling platform.
- Replacing the current execution device management system.
- Fully autonomous unreviewed case generation in MVP.
- Full dynamic execution in the first phase.
- Guaranteeing function correctness from a single screenshot.
- Building a full behavior-tree visual editor in MVP.

## Overall Direction

The system should evolve from fixed-step execution to an intent, state, and assertion driven automation layer.

Current case model:

- Step 1, Step 2, Step 3, Step 4 are fixed.
- Execution succeeds only if the expected node sequence still matches the game.

Target model:

- A case has a test intent, such as verify task completion or reward claiming.
- YOLO26/OCR recognizes the current game state.
- Assertions verify whether the functional result happened.
- Historical steps and node metadata are used to generate new case drafts.
- Behavior-tree drafts capture state transitions and recovery logic for future dynamic execution.

## Priority

The enhancement roadmap is:

1. Functional verification.
2. Automatic case generation.
3. Dynamic execution.

Functional verification comes first because generated cases are not useful unless the system can judge whether the function result is correct.

## Existing Platform Integration

The existing platform remains responsible for:

- Project selection.
- Environment selection.
- Case-set selection.
- Execution device selection.
- Task distribution to multiple machines.
- Long-running execution.
- Stability checks, including stuck state, crash, and abnormal exit.

The new system adds:

- Functional verification plugin.
- YOLO26/OCR detector layer.
- Assertion engine.
- Evidence report extensions.
- Node capability library.
- Case generation assistant.
- Behavior-tree draft output.
- Learning pipeline from execution traces.

## Functional Verification

### Verification Mode

MVP defaults to black-box verification because task status and reward arrival APIs/logs are not currently available.

The system must support:

- YOLO26 visual object detection.
- OCR text recognition.
- Screenshot evidence.
- Multi-frame temporal evidence.
- Pass / Fail / Unknown result states.

Unknown is required. If visual evidence is insufficient, the system must not incorrectly mark the case as passed.

### First Detection Scope

First priority labels:

- `quest_tracker`
- `quest_complete_hint`
- `reward_popup`
- `claim_reward_button`
- `reward_text_area`
- `error_popup`
- `network_error`
- `blocked_flow_hint`

These cover the most important gap: whether tasks, rewards, and blocking errors can be detected.

Second priority labels:

- Login/main UI.
- NPC dialog/confirm buttons.
- Combat/settlement state.

### Assertion Model

Assertions should use state changes, not single-frame checks.

Example task completion assertion:

- Detect task tracker before execution.
- Detect task progress or completion hint after execution.
- Optionally OCR task text or completion text.
- Detect reward popup or claim result.
- Confirm the expected state appears across multiple frames.
- Save screenshots, bounding boxes, OCR text, timestamps, and confidence.

### Model Choice

MVP uses YOLO26 as the default visual detection baseline.

The engineering interface must still use a Detector abstraction:

- `YOLO26Detector`
- `OCRDetector`
- `TemplateDetector`
- `DetectorAdapter`

The adapter should output a unified structure:

- `label`
- `bbox`
- `confidence`
- `text`
- `timestamp`
- `source`

Model version, dataset version, thresholds, and evaluation results must be bound to project/game versions and recorded in execution reports.

## Data Assets

The team already has many screenshots and videos.

MVP data pipeline:

1. Collect historical screenshots, videos, and failure frames.
2. Extract frames from videos.
3. Clean and deduplicate frames.
4. Normalize resolution and tag game version/environment.
5. Define labels for task, reward, and exception detection.
6. Manually annotate the first dataset.
7. Split training/validation/test sets.
8. Evaluate YOLO26 using historical video replay.

## Automatic Case Generation

### Source Priority

Use mixed sources, but MVP prioritizes:

1. Historical structured cases.
2. Game node/API capability library.

Later phases add:

3. Long-running execution traces.
4. Requirement/design/play mode documentation.

### Node Capability Library

The current system can provide:

- Node name.
- Module/play mode.
- Input parameters.
- Preconditions.
- Execution action.
- Success state.
- Failure state.

Missing fields:

- Available environment.
- Risk level.
- Supported assertions.

These missing fields should be inferred first and manually corrected during review.

Inference examples:

- Available environment: inferred from project, version, environment tags, and historical success rate.
- Risk level: inferred from resource consumption, account state changes, economic impact, and whether it is allowed online.
- Supported assertions: inferred from success state, YOLO/OCR observations, and available evidence.

### Generated Case Output

Each generated case should produce three outputs:

1. Existing platform structured steps.
2. Behavior-tree draft.
3. Assertion configuration.

The structured steps keep compatibility with the existing platform. The behavior-tree draft preserves test intent, state checks, node selection, and recovery strategy for later dynamic execution. The assertion configuration defines YOLO26/OCR/screenshot temporal checks.

Generated cases must include:

- Case goal.
- Applicable project/version/environment.
- Account requirement.
- Step list and parameters.
- Expected state.
- Functional assertions.
- Recovery strategy.
- Risk level.
- Generation evidence.

### Review Flow

Generated cases enter a draft state first.

Flow:

1. Generate draft.
2. Run risk checks.
3. Human review.
4. Trial execution.
5. Promote to official case set.

No MVP-generated case should enter official regression without review and at least one successful trial run.

## Continuous Learning

The system should use large machine pools to improve testing accuracy over time.

The learning target is not "play the game better" as a primary goal. The primary goal is "test more accurately."

Execution pools:

- Exploration pool: development/test environments, allowed to run broader learning tasks.
- Regression pool: runs reviewed cases.
- Acceptance pool: runs controlled cases only.

Learning outputs:

- Better functional assertions.
- More accurate UI/state detection.
- Suggested new cases.
- Missing coverage discovery.
- Failure pattern summaries.
- Node and assertion confidence updates.

The system must distinguish:

- Observed execution traces.
- Inferred play/module models.
- Reviewed official test cases.

## Behavior Tree Role

Behavior trees are not the first execution format required by the current platform, but they are important as an intermediate representation.

MVP should generate behavior-tree drafts that represent:

- Test intent.
- State checks.
- Node alternatives.
- Failure recovery.
- Functional assertions.

Future dynamic execution can use these drafts to move away from fixed step order.

## Reporting

Reports should extend the current result model.

Each functional verification result should include:

- Pass / Fail / Unknown.
- Step where assertion was evaluated.
- Screenshot.
- YOLO bounding boxes.
- OCR result.
- Confidence.
- Temporal evidence frames.
- Failure or unknown reason.
- Model version.
- Dataset version.
- Case generation source if generated.

Reports should make it clear whether a case failed because:

- Function result did not appear.
- Visual evidence was insufficient.
- OCR was uncertain.
- An exception UI appeared.
- Existing execution failed before reaching verification.

## MVP Milestones

### M0: Functional Verification Prototype

- Build Detector abstraction.
- Integrate YOLO26 inference for screenshots.
- Integrate OCR.
- Define first label set.
- Run detection on historical screenshots/videos.
- Produce Pass / Fail / Unknown assertion result for task/reward/exception samples.

### M1: Existing Case Verification Integration

- Attach assertion configuration to existing structured cases.
- Execute current cases through the existing platform.
- Add functional evidence to reports.
- Support task/reward/exception detection.

### M2: Case Generation Drafts

- Import historical structured cases.
- Import node capability library.
- Generate new structured case drafts.
- Generate behavior-tree drafts.
- Generate assertion configurations.
- Add human review and trial-run flow.

### M3: Continuous Learning Loop

- Collect execution traces.
- Summarize success/failure patterns.
- Infer missing node fields.
- Suggest new cases and missing assertions.
- Feed reviewed results back into the capability library.

## Open Questions

- What is the exact export/import format for existing platform structured cases?
- What OCR engine should be used for Chinese game UI text?
- What labeling tool and dataset storage convention should be adopted?
- How will generated drafts be reviewed in the current platform UI?
- What report format can the existing platform ingest or display?
- How should screenshots/videos be sampled from historical executions?
