from pathlib import Path

import typer

from yolo_game_verify.assertions.temporal import evaluate_temporal_assertion
from yolo_game_verify.cases.loader import load_structured_case
from yolo_game_verify.cases.reporting import write_case_report
from yolo_game_verify.cases.runner import evaluate_structured_case
from yolo_game_verify.generation.generator import generate_case_draft
from yolo_game_verify.generation.loader import load_node_capabilities
from yolo_game_verify.generation.reporting import write_generated_case_draft
from yolo_game_verify.models import EvidenceFrame, TemporalAssertion, VerificationReport
from yolo_game_verify.reporting.json_report import write_json_report

app = typer.Typer(help="YOLO game functional verification tools.")


@app.callback()
def main() -> None:
    """Run YOLO game functional verification commands."""


def _load_frames(frame_dir: Path) -> list[EvidenceFrame]:
    image_paths = sorted(
        path for path in frame_dir.iterdir() if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}
    )
    return [EvidenceFrame.from_path(index, path) for index, path in enumerate(image_paths)]


@app.command("evaluate-frames")
def evaluate_frames(
    frames: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True),
    required_label: str = typer.Option("reward_popup"),
    min_frames: int = typer.Option(2),
    out: Path = typer.Option(...),
) -> None:
    evidence_frames = _load_frames(frames)
    assertion = TemporalAssertion(
        assertion_id=f"{required_label}_visible",
        required_label=required_label,
        min_frames=min_frames,
    )
    result, reason = evaluate_temporal_assertion(assertion, evidence_frames)
    report = VerificationReport(
        case_id="offline_frame_evaluation",
        result=result,
        reason=reason,
        frames=evidence_frames,
        metadata={"required_label": required_label, "min_frames": min_frames},
    )
    write_json_report(report, out)
    typer.echo(f"{report.result}: {report.reason}")


@app.command("evaluate-case")
def evaluate_case(
    case: Path = typer.Option(..., exists=True, file_okay=True, dir_okay=False),
    out: Path = typer.Option(...),
) -> None:
    structured_case = load_structured_case(case)
    report = evaluate_structured_case(structured_case)
    write_case_report(report, out)
    typer.echo(f"{report.result}: {report.reason}")


@app.command("generate-case-draft")
def generate_case_draft_command(
    case: Path = typer.Option(..., exists=True, file_okay=True, dir_okay=False),
    capabilities: Path = typer.Option(..., exists=True, file_okay=True, dir_okay=False),
    out: Path = typer.Option(...),
) -> None:
    structured_case = load_structured_case(case)
    node_capabilities = load_node_capabilities(capabilities)
    draft = generate_case_draft(structured_case, node_capabilities)
    write_generated_case_draft(draft, out)
    typer.echo(f"{draft.review_state}: {draft.draft_id}")
