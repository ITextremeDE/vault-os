<!-- SPDX-License-Identifier: MPL-2.0 -->

# Change principles

Changes to the operating layer are deliberate, infrequent, and traceable.

## Valid reasons

Change the system when a real model gap exists, recurring friction can be
removed, a rule is contradictory, or portability and maintainability improve
materially.

Do not change it merely because one case is unusual, another wording looks
nicer, or process discipline would be easier to avoid with more structure.

## Change sequence

1. Describe the problem precisely.
2. Identify the owning layer and ownership domain.
3. Inspect the existing canonical rule.
4. Apply the smallest effective change.
5. Check consequences for modules, assets, automation, and runtime behavior.
6. Record migration and rollback requirements when compatibility changes.

## Anti-duplication rule

Change the canonical source. Update downstream files only when a reference or
short operational summary would otherwise become incorrect.

## Removal rule

Unused structure should be simplified or removed only through an explicit,
reviewable change that preserves user content and supports rollback.
