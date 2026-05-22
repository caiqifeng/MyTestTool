from pathlib import Path

import typer

from yolo_game_verify.assertions.temporal import evaluate_temporal_assertion
from yolo_game_verify.cases.loader import load_structured_case
from yolo_game_verify.cases.reporting import write_case_report
from yolo_game_verify.cases.runner import evaluate_structured_case
from yolo_game_verify.context import load_verification_context
from yolo_game_verify.data.manifest import build_manifest
from yolo_game_verify.data.reporting import write_dataset_manifest
from yolo_game_verify.data.scanner import scan_frame_assets
from yolo_game_verify.detectors.adapter import DetectorAdapter
from yolo_game_verify.detectors.template import TemplateDetector
from yolo_game_verify.generation.generator import generate_case_draft
from yolo_game_verify.generation.loader import load_node_capabilities
from yolo_game_verify.generation.reporting import write_generated_case_draft
from yolo_game_verify.learning.analyzer import summarize_learning
from yolo_game_verify.learning.loader import load_case_reports
from yolo_game_verify.learning.reporting import write_learning_summary
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


def _metadata_from_context(context: Path | None) -> dict[str, object]:
    if context is None:
        return {}
    return {"context": load_verification_context(context).model_dump(exclude_none=True)}


@app.command("evaluate-frames")
def evaluate_frames(
    frames: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True),
    required_label: str = typer.Option("reward_popup"),
    min_frames: int = typer.Option(2),
    out: Path = typer.Option(...),
    context: Path | None = typer.Option(None, exists=True, file_okay=True, dir_okay=False),
    template: Path | None = typer.Option(None, exists=True, file_okay=True, dir_okay=False),
    template_label: str = typer.Option("reward_popup"),
    template_threshold: float = typer.Option(0.9),
) -> None:
    evidence_frames = _load_frames(frames)
    if template is not None:
        adapter = DetectorAdapter(
            [TemplateDetector(label=template_label, template_path=template, threshold=template_threshold)]
        )
        evidence_frames = [adapter.enrich_frame(frame) for frame in evidence_frames]
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
        metadata={"required_label": required_label, "min_frames": min_frames} | _metadata_from_context(context),
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


@app.command("summarize-learning")
def summarize_learning_command(
    reports: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True),
    capabilities: Path = typer.Option(..., exists=True, file_okay=True, dir_okay=False),
    out: Path = typer.Option(...),
    context: Path | None = typer.Option(None, exists=True, file_okay=True, dir_okay=False),
) -> None:
    case_reports = load_case_reports(reports)
    node_capabilities = load_node_capabilities(capabilities)
    summary = summarize_learning(case_reports, node_capabilities)
    summary.metadata.update(_metadata_from_context(context))
    write_learning_summary(summary, out)
    typer.echo(f"learning-summary: {summary.total_reports} reports")


@app.command("prepare-dataset")
def prepare_dataset(
    frames: Path = typer.Option(..., exists=True, file_okay=False, dir_okay=True),
    project: str = typer.Option(...),
    game_version: str = typer.Option(...),
    environment: str = typer.Option(...),
    out: Path = typer.Option(...),
) -> None:
    assets = scan_frame_assets(frames)
    manifest = build_manifest(
        assets,
        project=project,
        game_version=game_version,
        environment=environment,
    )
    write_dataset_manifest(manifest, out)
    typer.echo(f"dataset-manifest: {manifest.unique_assets}/{manifest.total_assets} unique")
