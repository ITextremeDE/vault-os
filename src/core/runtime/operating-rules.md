<!-- SPDX-License-Identifier: MPL-2.0 -->

# Operating rules

Human and agent work follows the same ownership and structure rules.

## Default behavior

Read first, classify second, and make the smallest reversible change last.

## Interventions

- Preserve working structures and user-owned content.
- Add structure only for a clear recurring need.
- Treat changes to system rules as higher risk than content changes.
- Do not create new standards incidentally while performing operational work.
- Do not delete user content without explicit authorization.

## Conflicts

When rules appear to conflict, apply them in this order:

1. current user authorization and applicable host instructions;
2. Vault-OS runtime rules;
3. core operating principles;
4. the applicable schema contract;
5. instance registers and policy;
6. the applicable module workflow.

If ambiguity remains, inspect the relevant canonical source and choose the
smallest safe fallback. Use the configured capture location when classification
cannot yet be completed.

## Automation

Automation operates only on stable declared interfaces. Repeated special-case
logic is evidence that the owning schema, configuration, or workflow should be
reviewed.
