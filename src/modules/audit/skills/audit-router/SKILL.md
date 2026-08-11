---
name: audit-router
description: Route observed vault drift to the smallest audit that can establish a reliable finding.
---

# Audit router

This skill classifies signals; it does not perform deep analysis or corrections.
Choose exactly one primary action: no action, continuous audit, OS audit, content
audit, or full vault audit.

1. Identify structure, metadata, link, OS-drift, content, or quality signals.
2. Distinguish an isolated event from a pattern or worsening trend.
3. Decide whether the likely scope is OS, content, or both.
4. Select the smallest audit with useful explanatory power.
5. Give each trigger an ID, priority, evidence location, and rationale.

Recommend direct correction only for an exceptionally clear, local, single-path
problem where an audit adds no information. Otherwise audit before correction.
Use `references/trigger-rules.md` for thresholds and escalation guidance.
