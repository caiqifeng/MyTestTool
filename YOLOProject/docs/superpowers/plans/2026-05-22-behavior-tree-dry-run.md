# Behavior Tree Dry Run Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dry-run generated behavior-tree drafts with injected node handlers.

**Architecture:** Add a minimal behavior-tree runner that supports `sequence`, `selector`, `condition`, and `action` node types. The runner is deterministic and offline; action/condition behavior is supplied by injected callables so it does not replace platform execution.

**Tech Stack:** Python 3.11+, pytest, pydantic, typer.

---
