# Absence Assertions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Support assertions that verify exception UI labels are absent across temporal evidence.

**Architecture:** Extend `TemporalAssertion` with an `expected` mode. Existing positive assertions keep the default `present`; exception checks can use `absent` to fail when the label appears.

**Tech Stack:** Python 3.11+, pytest, pydantic.

---
