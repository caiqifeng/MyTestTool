# Verification Metadata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bind functional verification reports to game, model, dataset, and execution metadata.

**Architecture:** Add a shared `VerificationContext` model and thread it through M0 frame reports, M1 case reports, M2 generated drafts, and M3 learning summaries via existing metadata fields. Keep metadata optional for backward compatibility.

**Tech Stack:** Python 3.11+, pytest, pydantic, typer.

---

## Scope

Implements:

- Shared verification context model.
- JSON context loader.
- CLI `--context` option for report-producing commands.
- Report metadata enrichment.

Does not implement:

- Real platform API metadata ingestion.
- Model registry.
- Dataset storage.

## Tasks

1. Add `VerificationContext` model and loader.
2. Enrich `evaluate-frames`, `evaluate-case`, `generate-case-draft`, and `summarize-learning` outputs.
3. Add example context JSON and README usage.
