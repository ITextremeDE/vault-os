# ADR 0007: Synchronized instance and device-local runtime

- Status: Accepted
- Date: 2026-08-11

## Context

Vault-OS is local-first but must support one vault on multiple devices.
Obsidian Sync transfers ordinary vault files but excludes dot-prefixed files
and folders other than `.obsidian`. The original development layout stored
instance configuration below `.vault-os`, so another device could receive the
managed system files without the configuration required to operate them.

Release locks, operation state, provider discovery wrappers, client-specific
configuration, and search indexes describe one device and must not become
shared canonical state. Mixing both categories below one hidden root made the
ownership and synchronization boundary ambiguous.

## Decision

- Canonical instance configuration, registers, policies, integration choices,
  validation settings, and agent context live below the fixed visible
  `Vault-OS/` directory.
- Instance-manifest targets with a dot-prefixed first component are invalid.
- `.vault-os` contains device-local release locks, operation transactions, and
  generated agent-integration state only.
- Provider wrappers and client data below `.agents`, `.claude`, `.codex`,
  `.qmd`, and `.mcp.json` are initialized separately on every device.
- Visible generated `AGENTS.md` and `CLAUDE.md` may synchronize. Their content
  is deterministic from synchronized inputs and does not vary with local QMD
  activation.
- One primary device applies `update`. Secondary devices wait for the external
  synchronization service, check out the identical Vault-OS package version,
  and run `device-sync`.
- `device-sync` verifies the complete managed file set and every applicable
  instance file. It writes only `.vault-os/lock.json` and refuses incomplete,
  modified, or stale synchronized state.
- Updates migrate legacy hidden instance files into the visible root, preserve
  their content, update references between migrated instance paths, and leave
  the legacy copies in place for reviewed cleanup.
- Vault-OS does not configure, start, monitor, or own Obsidian Sync and never
  modifies `.obsidian`.

## Consequences

- Obsidian Sync can carry the complete canonical Vault-OS instance when **Sync
  all other types** is enabled.
- Each device has an independently verifiable release record and independently
  initialized AI runtime without conflicting synchronized indexes or client
  settings.
- A synchronized partial update cannot silently become trusted local state.
- Multi-device updates are intentionally serialized through one primary
  device; concurrent lifecycle updates are unsupported.
- Legacy development installations require one explicit migration update and a
  later reviewed cleanup of obsolete hidden instance copies.

The external synchronization behavior is documented by Obsidian under
[Sync settings](https://obsidian.md/help/sync/settings).
