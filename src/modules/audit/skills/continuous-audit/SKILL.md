---
name: continuous-audit
description: Perform a lightweight recurring vault health check and escalate only meaningful new drift.
---

# Continuous audit

Run the configured deterministic validator first. Then inspect only new or
worsening structure, metadata, naming, link, asset, runtime, inbox, and content
signals. Compare with the last meaningful baseline when one exists; do not repeat
known static findings as if they were new.

Return a concise state assessment, finding IDs, affected locations, observed
trends, and one next action: none, small correction, OS audit, content audit, or
full vault audit. Do not imitate a full audit or change files without explicit
authorization.
