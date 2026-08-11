<!-- SPDX-License-Identifier: MPL-2.0 -->

# 05 Automation

This layer documents stable interfaces between a vault and automation that
reads, validates, or deliberately changes it.

## Automation contract

For every integration, record only durable operational facts:

- purpose and observable effect;
- canonical implementation or configuration source;
- allowed read and write scope;
- input, output, validation, and error behavior;
- responsible runtime and recovery owner.

Active schedules, credentials, prompts, task bindings, and current runtime
state remain in their canonical external system. Vault-OS documents the
interface, not a second copy of the implementation.

Automations should be idempotent where practical, expose failures, avoid silent
overwrites, and have a clear pause and recovery path. Local Obsidian settings
are outside the portable core.

Concrete automations are instance configuration and are never inferred from a
source vault.
