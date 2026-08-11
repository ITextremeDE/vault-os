---
name: os-audit
description: Audit Vault-OS layers, canonical rules, assets, and runtime for structural drift.
---

# OS audit

Read canonical rules first, derive the installed target architecture, and then
check schema, registers, workflows, assets, automation, and runtime against it.
Look for mixed ownership, normative contradictions, missing contracts, duplicated
rules, stale paths, broken links, asset drift, runtime drift, migration remnants,
and weak automation interfaces.

Treat documented history as history, not an active defect. Report only material
findings with IDs, priority, concrete locations, evidence, and a proposed remedy.
Do not change files. Use `references/criteria.md` for detailed review axes.
