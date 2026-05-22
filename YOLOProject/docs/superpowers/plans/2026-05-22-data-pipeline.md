# Data Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prepare historical screenshot assets for detector labeling and replay evaluation.

**Architecture:** Add a `data` package that scans image directories, computes content hashes, deduplicates frames, and writes a manifest with project/game/environment context. Video frame extraction remains out of scope for this small offline slice.

**Tech Stack:** Python 3.11+, pytest, pydantic, typer, standard library hashing.

---

## Scope

Implements image scanning, deduplication, manifest generation, and CLI export.

Does not implement video extraction, annotation tooling, or model training.
