<!-- SPDX-License-Identifier: MPL-2.0 -->

# Decision logic

Structural decisions should be consistent, explainable, and free of unnecessary
special cases.

## Default sequence

1. Understand the existing structure.
2. Read the applicable canonical rule.
3. Choose the smallest useful and reversible change.

## Existing file or new file

Extend an existing file when the information belongs to its established scope
and does not form an independently useful unit.

Create a new file when the information has a distinct purpose, should be
referenced independently, and has no natural existing home.

## Place or capture

Place information directly when its type, owner, and destination are clear.
Otherwise capture it in the configured inbox and defer classification until the
missing context is available.

## Core, module, instance, or runtime

- Put a rule in the core only if every Vault-OS installation requires it.
- Put optional managed behavior in a module.
- Put names, values, selections, credentials, and local policy in instance
  configuration or content.
- Put generated observations and tool state in runtime storage.

## Escalation

When a decision remains unclear, inspect the layers in this order:

1. operating principles;
2. schema mechanics;
3. instance registers;
4. the applicable workflow;
5. the smallest reversible fallback.

Do not create parallel structures, undocumented value sets, or permanent rules
for a single exceptional case.
