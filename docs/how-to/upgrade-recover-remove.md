# Upgrade, recover, and remove Vault-OS

Vault-OS separates release-managed files from vault-owned configuration and
content. Safe operation depends on preserving that ownership boundary.

## Before every change

1. Make a backup, snapshot, or clean version-control checkpoint of the vault.
2. Stop other processes that may write the same files.
3. Use the Vault-OS checkout for the release you intend to install.
4. Run `doctor` before changing configuration.

```bash
.venv/bin/python -m vault_os doctor "/path/to/My Vault"
```

Do not edit `.vault-os/lock.json` to force an operation. It is the installed
release record and managed-file checksum authority.

## Upgrade to a release

Update the package checkout and select the intended release tag:

```bash
git fetch --tags origin
git checkout "vX.Y.Z"
.venv/bin/python -m pip install -r requirements.txt
```

Preview and apply the target package:

```bash
.venv/bin/python -m vault_os diff "/path/to/My Vault"
.venv/bin/python -m vault_os update "/path/to/My Vault"
.venv/bin/python -m vault_os doctor "/path/to/My Vault"
```

`diff` is read-only. `update` validates all currently managed checksums before
writing, applies the complete plan transactionally, and updates the release lock
last. A conflict stops the operation without applying a partial update.

If agent adapters were initialized, refresh and validate them after the release
update:

```bash
.venv/bin/python -m vault_os agent-init "/path/to/My Vault" \
  --provider codex
.venv/bin/python -m vault_os doctor "/path/to/My Vault" --ai
```

Use the provider option originally selected for the vault. Omit it only when all
registered adapters are intended. Provider and QMD state is additive and
persistent in the current `0.x` release line; there is no automated
de-initialize command.

## Add or remove modules

Edit only the `modules` array in `Vault-OS/config.yaml`, using identifiers from
the [module catalog](../reference/modules.md). Then run:

```bash
.venv/bin/python -m vault_os diff "/path/to/My Vault"
.venv/bin/python -m vault_os update "/path/to/My Vault"
```

Selecting a module adds its managed files and any missing create-only instance
seeds. Deselecting a module removes only files that still match their installed
checksums. Ordinary content and existing instance files remain untouched.

Changing the configured system root is also performed through configuration,
`diff`, and `update`. Treat it as a migration: back up first and inspect the full
plan because every managed target moves.

## Add bootstrap files to an existing installation

After upgrading to `0.1.0-dev.6` or newer, review the `bootstrap` filenames in
`Vault-OS/config.yaml` and run:

```bash
.venv/bin/python -m vault_os bootstrap "/path/to/My Vault"
```

Older configurations may omit the `bootstrap` object; Vault-OS then uses the
documented neutral defaults in memory without rewriting the configuration.
Existing profile, README, dashboard, or overview files are preserved. Review
the newly created notes as user content; later package updates never change
them.

## Update synchronized secondary devices

Apply `update` on one primary device only. After the approved synchronization
service has delivered the complete result to another device, use the same
Vault-OS package version there and run:

```bash
.venv/bin/python -m vault_os device-sync "/path/to/My Vault"
.venv/bin/python -m vault_os agent-init "/path/to/My Vault" --provider codex
.venv/bin/python -m vault_os doctor "/path/to/My Vault" --ai
```

`device-sync` verifies synchronized managed checksums, the selected module set,
and all visible instance files before rebuilding only the local
`.vault-os/lock.json`. It never starts synchronization and never writes the
synchronized file set. Use `doctor` without `--ai` when no local provider was
initialized. The complete Obsidian Sync procedure is in the
[Obsidian setup guide](obsidian-setup.md#use-obsidian-sync-on-more-than-one-device).

## Migrate the pre-`0.1.0-dev.5` hidden instance layout

Earlier development builds stored both instance files and runtime state below
`.vault-os`, which prevented Obsidian Sync from carrying the instance between
devices. Running `update` with `0.1.0-dev.5` or newer reads the legacy
configuration, creates the canonical visible `Vault-OS/` files, updates
references between those files, and preserves user customizations.

Legacy hidden instance files are intentionally not deleted. They cease to be
canonical after a successful `update` and `doctor`. Keep the complete backup
until the migrated vault and a synchronized second-device copy have both been
validated. If cleaning up later, remove only reviewed legacy instance copies;
retain `.vault-os/lock.json`, `.vault-os/integrations/agents.yaml`, operation
locks, and transaction state because those remain device-local runtime data.

## Resolve a managed-file conflict

An update reports a conflict when a managed file is missing, locally changed,
or blocked by an existing new target.

1. Preserve the local file and determine why it differs.
2. Move legitimate vault-specific customization into ordinary content or an
   instance-owned configuration file.
3. Restore the managed file exactly from the previously installed Vault-OS
   release, or restore the complete vault from a known-good backup.
4. Run `doctor` and `diff` again.
5. Apply `update` only when the conflict is gone.

Do not replace a changed file with the new release merely to silence the old
checksum check. The updater must first see the exact previously installed
managed version; otherwise it cannot prove that no user change was discarded.

## Recover from an interrupted command

File changes are staged under `.vault-os/.transactions` and rolled back when a
write fails. The operation lock `.vault-os/operation.lock` prevents concurrent
writes and is normally removed automatically.

If `doctor` reports a stale operation lock:

1. confirm that no Vault-OS process is still running;
2. back up the vault;
3. remove only `.vault-os/operation.lock`; and
4. rerun `doctor` before another write.

If `doctor` reports stale transaction data, do not reuse it as a backup. The
transaction directory is implementation state. Preserve it for diagnosis,
restore the vault from its external backup if file state is uncertain, and
report the failure with the command output.

## Roll back a release

Vault-OS has transactional rollback for a failed command, but no automatic
rollback from an already successful release update. Restore the pre-update
vault backup or version-control checkpoint, then run `doctor` using the matching
Vault-OS release checkout.

Running an older package's `update` command is not a substitute for a supported
downgrade unless that release explicitly documents a downgrade path.

## Remove Vault-OS

The current `0.x` release line has no uninstall command. The safe removal
method is to restore a pre-install backup or migrate wanted content into a
clean vault.

Do not blindly delete every path in `.vault-os/lock.json`: module removal may
leave intentional instance-owned files, and a vault may contain unrelated
content beneath the same directory tree. Manual removal requires a reviewed,
vault-specific plan and is outside the automated lifecycle.
