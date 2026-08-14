<!-- SPDX-License-Identifier: MPL-2.0 -->

# Frontmatter

Vault-OS treats frontmatter as a configurable interface between content,
queries, agents, and automation.

## Contract

- The instance validation profile defines base fields and their order.
- Modules define their content kinds, types, statuses, and extension fields.
- Instance registers provide concrete controlled values such as areas.
- Required fields are explicit; absence and an empty value are not equivalent.
- Multi-value fields remain YAML lists, including when empty.
- Single-value relations use one Wiki link; multi-value relations use YAML
  lists of Wiki links.
- Date-only fields use the ISO `YYYY-MM-DD` format.
- Extension fields require one canonical definition and a recurring purpose.
- External references use verified ID/URL pairs; explicit instance pairs may
  preserve established field names that do not share a derived base.
- Secret values never belong in frontmatter.

The neutral profile uses `kind`, `type`, `status`, and `area`. An existing vault
may map these roles to other field names without changing the validation
engine. Managed templates and views are materialized from those mappings and
the configured paths during lifecycle operations.

Managed core files do not require frontmatter. A module or instance may opt its
own managed or content files into frontmatter validation.
