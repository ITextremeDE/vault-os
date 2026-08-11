# CLI reference

Vault-OS provides four lifecycle commands through `bin/vault-os`. Run the
wrapper from a release checkout with a Python environment active that contains
the dependency declared in `requirements.txt`.

## Install

```bash
./bin/vault-os install VAULT [--config FILE] [--name NAME] \
  [--system-root PATH] [--module ID ... | --all-modules] [--json]
```

Installation may create the vault directory. It validates the complete package
before changing the vault, installs managed core and selected module files,
creates missing instance seeds, and writes `.vault-os/lock.json` last.

The vault name defaults to the target directory name. With no module option,
only the core is installed. `--module` may be repeated; `--all-modules` selects
the complete catalog. `--config` supplies an instance configuration instead of
the neutral seed, while `--name` and `--system-root` override its corresponding
values.

Installation stops without partial changes when a managed destination, the
instance configuration, or the release lock already exists. Existing
create-only instance files other than the configuration are preserved.

## Diff and update

```bash
./bin/vault-os diff VAULT [--json]
./bin/vault-os update VAULT [--json]
```

Edit `.vault-os/config.yaml` to change the selected modules or system root.
`diff` calculates the resulting plan without changing files. `update` applies
the same plan transactionally and writes the new lock last.

Before an update starts, every file recorded as managed in the installed lock
must exist and still match its recorded checksum. A missing or locally changed
managed file stops the complete update. Deselected module files are removed
only after this check. Existing instance files are never overwritten; newly
applicable instance seeds are created only when missing.

## Doctor

```bash
./bin/vault-os doctor VAULT [--json]
```

`doctor` checks package integrity, installation metadata, managed-file state,
configuration changes, and stale operation data without modifying the vault.
An available package update or unapplied configuration change is reported as a
warning unless a protected-file conflict makes the installation unhealthy.

## Safety boundaries

- All package sources are checked against their manifest checksums.
- All writes are staged and applied with backups and rollback.
- Concurrent lifecycle writes are prevented by a local operation lock.
- Absolute paths, parent traversal, symbolic-link traversal, filesystem roots,
  the user's home directory, and `.obsidian` targets are rejected.
- `.vault-os/config.yaml` and all other instance files remain owner-controlled.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Command succeeded; `doctor` found no errors; `diff` found no conflicts |
| `1` | Invalid package, configuration, installation, filesystem operation, or unhealthy `doctor` result |
| `2` | A protected-file, path, installation, or concurrent-operation conflict was detected |

`--json` emits successful plans and doctor reports as structured JSON for
automation. Command errors remain concise messages on standard error.
