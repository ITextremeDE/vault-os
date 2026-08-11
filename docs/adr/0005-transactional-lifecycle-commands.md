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

- Vault-OS provides `install`, `update`, `diff`, and `doctor` commands.
- Instance configuration selects the system root and optional modules.
- A local release lock records the package version, manifest fingerprint, and
  installed checksums of managed files only.
- Installation validates the complete package and preflights all destinations.
  Instance seeds are create-only.
- Updates verify every file in the installed managed set before writing. A
  missing or locally changed file stops the complete update.
- Module deselection removes only unchanged managed files. Module selection may
  create missing instance seeds but never replaces existing instance files.
- Writes are staged and applied as one transaction with backups and rollback.
  The release lock is written last.
- `diff` and `doctor` are read-only. Lifecycle writes use an exclusive local
  operation lock.
- Path escape, symbolic-link traversal, broad targets, and any `.obsidian`
  target are rejected.

## Consequences

- A successful lifecycle command leaves a release-consistent managed file set
  and lock.
- Direct edits to managed files require explicit conflict resolution before an
  update; the updater never guesses which content should win.
- Instance configuration and content remain outside release ownership.
- Interrupted or failed writes are rolled back, while stale operation data can
  be diagnosed explicitly.
- Real-world vault adoption still requires a deliberate migration and conflict
  review; the installer does not treat an existing system tree as already
  managed.
