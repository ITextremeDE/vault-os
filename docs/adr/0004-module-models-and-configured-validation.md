# ADR 0004: Module models and configured validation

- Status: Accepted
- Date: 2026-08-11

## Context

The source vault stored general schema mechanics, concrete content kinds,
instance field names, register values, and validator assumptions in the same
files. Copying that model would bind Vault-OS to one language, workflow set,
folder layout, and vault owner.

## Decision

- Core Markdown documents define schema mechanics only.
- Core and optional modules provide machine-readable JSON model fragments.
- Model fragments own stable content-kind identifiers, types, statuses, and
  module fields.
- Instance YAML maps semantic field roles, supplies register values, selects
  modules, and configures paths and validation behavior.
- Instance field profiles may map localized stored kind, type, and status
  values to the stable identifiers used by module models.
- The portable validator loads installed model fragments and instance data at
  runtime. It contains no built-in vault name, content catalog, field names,
  areas, external-system paths, or secret exceptions.
- Stable identifiers use English technical names. Display language and
  user-facing templates may be localized separately.

## Consequences

- Modules can add content models without changing validator code.
- Existing vaults can retain local field names through configuration.
- Core files remain valid when no optional productivity or knowledge module is
  selected.
- Duplicate content kinds across installed models are deterministic errors.
- PyYAML is a runtime dependency for instance configuration and Markdown
  frontmatter parsing.
- Model or configuration schema changes require explicit migration support.
