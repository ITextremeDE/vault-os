<!-- SPDX-License-Identifier: MPL-2.0 -->

# Vault-OS system

This directory is the portable operating layer of a Vault-OS instance. It
contains managed rules and contracts, not the vault owner's content or
configuration.

## Layers

- `00 OS`: architecture, principles, and system change rules
- `01 Schema`: portable structural conventions
- `02 Registers`: contracts for instance-owned value lists
- `03 Workflows`: contracts for optional operational workflows
- `04 Assets`: contracts for templates, prompts, skills, and reusable blocks
- `05 Automation`: deterministic validation and maintenance contracts
- `06 Runtime`: rules for agents and other runtime components

Optional modules extend these layers. They may add managed schemas, workflows,
and assets, but must not redefine core rules.

## Ownership

- Managed files are supplied by Vault-OS and updated only when their installed
  checksum still matches the recorded release state.
- Instance files belong to the vault owner and are never replaced by updates.
- Runtime files are generated locally and are not release content.

Every rule and value list has one canonical source. Operational files refer to
that source instead of maintaining competing copies.

## Reading order

Start with the architecture and principles in `00 OS`, then read the relevant
schema, register, workflow, asset, validation, or runtime document.
