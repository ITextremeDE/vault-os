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
- Instance field profiles may map stable module-field identifiers to localized
  stored names and override filename patterns for established vault
  conventions without rewriting existing content.
- Multi-value instance registers may explicitly accept either one scalar value
  or a YAML list so established content shapes remain valid.
- Instance registers may document their overall purpose and every controlled
  value without moving those local semantics into the portable model.
- External-reference policy may declare explicit ID/URL field pairs when an
  established pair does not follow the configured suffix convention.
- Managed templates and views use reserved semantic tokens. Lifecycle commands
  materialize those tokens from the current instance field profile and path
  configuration while preserving native Obsidian placeholders.
- A context-qualified `preferredValues` entry resolves the reverse direction
  explicitly when multiple stored values map to one stable identifier.
- The portable validator loads installed model fragments and instance data at
  runtime. It contains no built-in vault name, content catalog, field names,
  areas, external-system paths, or secret exceptions.
- Stable identifiers use English technical names. Stored field names and values
  in installed templates and views follow the instance mappings.

## Consequences

- Modules can add content models without changing validator code.
- Existing vaults can retain local field names through configuration.
- Existing vaults can retain deliberate filename conventions while new vaults
  inherit the stricter managed defaults.
- Direct Obsidian template insertion and Bases views use the same localized
  metadata contract as validator and agent workflows.
- Core files remain valid when no optional productivity or knowledge module is
  selected.
- Duplicate content kinds across installed models are deterministic errors.
- PyYAML is a runtime dependency for instance configuration and Markdown
  frontmatter parsing.
- Model or configuration schema changes require explicit migration support.
