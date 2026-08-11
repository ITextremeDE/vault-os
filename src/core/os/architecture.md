<!-- SPDX-License-Identifier: MPL-2.0 -->

# Architecture

Vault-OS separates portable operating logic from the identity, content, and
configuration of a concrete vault.

## Goal

The system keeps stable rules, formal structure, concrete values, reusable
tools, and runtime behavior independently maintainable and transferable.

## Layer model

Vault-OS uses seven logical layers:

1. `00 OS` defines purpose, architecture, and principles.
2. `01 Schema` defines portable structural rules.
3. `02 Registers` defines contracts for concrete allowed values.
4. `03 Workflows` defines operational application of the rules.
5. `04 Assets` contains reusable templates, prompts, skills, and blocks.
6. `05 Automation` contains deterministic evaluation and maintenance logic.
7. `06 Runtime` governs agents and other runtime components.

## Ownership model

Every installed artifact has exactly one owner:

- `managed`: versioned core or module content supplied by Vault-OS;
- `instance`: configuration or content maintained by the vault owner;
- `runtime`: state generated locally by tooling.

Managed files are updated only through release tooling. Instance and runtime
files are never replaced by a Vault-OS update.

## Canonical-source rule

Every rule has one canonical location:

- principles belong to `00 OS`;
- structural mechanics belong to `01 Schema`;
- concrete values belong to `02 Registers`;
- operational behavior belongs to `03 Workflows`;
- assets apply rules but do not redefine them;
- runtime documents reduce rules for execution but do not duplicate the system.

## Extension model

The core defines only mechanics required by every installation. Optional
content models, folder strategies, workflows, integrations, views, and agent
tools are modules. A vault selects modules and supplies its own values through
instance configuration.
