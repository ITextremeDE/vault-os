# ADR 0003: Manifests and installation roots

- Status: Accepted
- Date: 2026-08-11

## Context

Vault-OS needs deterministic package contents and installation destinations
without hard-coding the name or system-folder layout of a concrete vault. The
ownership model in ADR 0001 also requires managed, instance, and runtime files
to behave differently during installation and updates.

## Decision

The repository uses JSON manifests with schema version `1`:

- `repository.json` is the manifest entry point;
- `core.json` lists required managed files and their source checksums;
- `modules.json` is the catalog of optional managed components;
- `instance.json` lists create-only instance seeds;
- `runtime.json` declares generated local artifacts without release sources.

Manifest targets are relative POSIX paths. Managed core targets use the logical
root `system`, resolved from `paths.system` in the instance configuration.
Instance seeds and runtime state use the logical root `vault`; the configuration
seed is installed at `.vault-os/config.yaml` and runtime lock data is generated
at `.vault-os/lock.json`.

Source checksums protect package integrity. The installed lock file will record
release checksums used by the updater to detect local changes to managed files.
Checksums do not transfer ownership of instance seeds to Vault-OS after their
initial creation.

## Consequences

- A vault may choose a system folder without rewriting managed source files.
- Manifest validation can prove exact core coverage and package integrity.
- Instance configuration is created once and never overwritten by updates.
- Runtime state has no distributable source file.
- Changing the manifest schema or logical-root semantics requires an explicit
  migration.
