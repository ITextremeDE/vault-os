---
name: os-correction
description: Implement explicitly selected OS-audit findings from canonical source to dependent assets.
---

# OS correction

Require explicit finding IDs or a precise, unambiguous OS defect. If alternatives
differ materially, explain them and wait for selection. Correct the canonical
source first, then update only dependent assets or runtime summaries needed to
restore consistency.

Do not change content notes, delete rules without replacement, introduce new
layers or schema values, or perform unrelated cleanup. Validate the selected
finding and report authorization, changed files, dependent updates, closed
findings, and residual drift.
