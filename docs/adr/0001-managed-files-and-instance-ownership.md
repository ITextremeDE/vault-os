# ADR 0001: Managed files and instance ownership

- Status: Accepted
- Date: 2026-08-11

## Context

Vault-OS must be installable in independently named Obsidian vaults and must be
updatable without replacing local content or configuration. A copied starter
vault does not provide a reliable update path. Git submodules and symbolic links
also introduce unnecessary coupling to Git clients, filesystem behavior, and
sync implementations.

## Decision

Vault-OS will be distributed as ordinary files through a manifest-driven
installer and updater.

Each installed file has one owner:

- `managed`: supplied and versioned by Vault-OS;
- `instance`: created or maintained by the vault owner;
- `runtime`: generated locally and never supplied as release content.

Managed files are identified by release metadata and checksums. Updates replace
only unchanged managed files. If an installed managed file differs from its
recorded checksum, the updater stops and reports the conflict.

Vault-specific configuration and extensions live outside managed files. The
portable core uses neutral terms such as `vault` and obtains the chosen vault
name from instance configuration.

## Consequences

- A vault remains a normal directory that works with Obsidian Sync and Git.
- Users can choose any vault name without rewriting core files.
- Local content and configuration have a mechanically enforceable protection boundary.
- Customizing a managed file directly is unsupported and becomes a visible update conflict.
- Installation state and file ownership require a versioned manifest and local lock data.
