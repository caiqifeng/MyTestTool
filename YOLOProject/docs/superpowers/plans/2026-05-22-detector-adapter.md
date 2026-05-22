# Detector Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run one or more detectors over evidence frames before temporal assertion evaluation.

**Architecture:** Add a small detector adapter that applies detector protocols to `EvidenceFrame` paths and appends normalized detections. Wire a template detector option into the offline `evaluate-frames` command for deterministic local smoke runs.

**Tech Stack:** Python 3.11+, pytest, typer, OpenCV template detector.

---
