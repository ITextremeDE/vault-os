# ADR 0005: Transactional lifecycle commands

- Status: Accepted
- Date: 2026-08-11

## Context

Installing or updating an operating layer inside an ordinary Obsidian vault
must not damage user content, silently overwrite local customizations, or leave
a partial release after a filesystem error. The manifest and ownership model
defines what Vault-OS may manage, but it also needs an enforceable lifecycle
and durable record of the installed release.

## Decision

- Vault-OS provides `install`, `bootstrap`, `update`, `diff`, `device-sync`, and
  `doctor` lifecycle commands.
- Instance configuration selects the system root and optional modules.
- A local release lock records the package version, manifest fingerprint, and
  installed checksums of managed files only.
- Installation validates the complete package and preflights all destinations.
  Instance seeds are create-only.
- Installation creates the configured inbox directory. When their modules are
  enabled, it also creates all configured PARA roots and the journal root with
  daily, weekly, and yearly directories. These directories are user-owned, are
  not recorded in the release lock, and a conflicting file or symbolic link
  stops installation before writes.
- Updates verify every file in the installed managed set before writing. A
  missing or locally changed file stops the complete update.
- Managed sources marked for instance materialization are rendered from the
  current synchronized configuration and field profile. The lock records the
  installed artifact checksum, so configuration changes can update those files
  without weakening local-change protection.
- Module deselection removes only unchanged managed files. Module selection may
  create missing instance seeds but never replaces existing instance files.
- Writes are staged and applied as one transaction with backups and rollback.
  The release lock is written last.
- `diff` and `doctor` are read-only. Lifecycle writes use an exclusive local
  operation lock.
- `device-sync` verifies files delivered by an external synchronization service
  and writes only the device-local release lock.
- `bootstrap` creates missing user-owned start files transactionally without
  adding them to release ownership or overwriting existing files.
- Path escape, symbolic-link traversal, broad targets, and any `.obsidian`
  target are rejected.

## Consequences

- A successful lifecycle command leaves a release-consistent managed file set
  and lock.
- Direct edits to managed files require explicit conflict resolution before an
  update; the updater never guesses which content should win.
- Changing instance field or path mappings requires an update to rematerialize
  affected managed templates and views.
- Instance configuration and content remain outside release ownership.
- A newly installed vault has the operational directory structure required by
  its selected modules without making later content release-managed.
- Interrupted or failed writes are rolled back, while stale operation data can
  be diagnosed explicitly.
- Real-world vault adoption still requires a deliberate migration and conflict
  review; the installer does not treat an existing system tree as already
  managed.
