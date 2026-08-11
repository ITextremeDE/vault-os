# CLI reference

Vault-OS provides five commands through its Python module and `bin/vault-os`.
From a release checkout, the most explicit form is:

```bash
.venv/bin/python -m vault_os COMMAND
```

The wrapper is equivalent when a Python environment containing the dependency
from `requirements.txt` is active.

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

There is no initial-install dry-run in version `0.1`. The installer preflights
all targets before applying a successful installation, but users adopting an
irreplaceable existing vault should test against a copy first. See the
[installation guide](../how-to/install.md).

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

`update` supports forward application of the selected package. It is not an
automatic downgrade or uninstall command. Recovery and removal boundaries are
documented in [Upgrade, recover, and remove](../how-to/upgrade-recover-remove.md).

## Doctor

```bash
./bin/vault-os doctor VAULT [--ai] [--json]
```

`doctor` checks package integrity, installation metadata, managed-file state,
configuration changes, and stale operation data without modifying the vault.
An available package update or unapplied configuration change is reported as a
warning unless a protected-file conflict makes the installation unhealthy.

With `--ai`, doctor also validates initialized provider instructions, registered
skill wrappers, generated checksums, and the configured QMD executable and MCP
artifacts. Agent validation is opt-in so a vault can use the portable core
without any AI client.

## Agent initialization

```bash
./bin/vault-os agent-init VAULT \
  [--provider codex|claude|all] [--qmd] [--qmd-command COMMAND] [--json]
```

`agent-init` requires an installed, healthy, current Vault-OS release. It
creates a provider-neutral root `AGENTS.md`; the default `all` provider also
creates `CLAUDE.md` importing that file. Installed managed skills are exposed
through provider-native wrappers under `.agents/skills` for Codex and
`.claude/skills` for Claude Code. The wrappers reference the canonical managed
skills instead of copying their instructions.

`all` means every adapter in the package provider registry. The built-in
registry currently contains `codex` and `claude`; CLI choices are derived from
that registry rather than hard-coded in the lifecycle command.

Provider selection is additive. Selecting another provider adds it to instance
state; it does not remove an initialized provider. QMD activation is also
persistent. Version `0.1` has no provider or QMD de-initialize command.

Generated artifacts and their checksums are recorded in the instance-owned
`.vault-os/integrations/agents.yaml`. A repeated command refreshes only
unchanged generated artifacts. Any local edit stops the complete operation.
Existing unowned `AGENTS.md` or `CLAUDE.md` files are never overwritten.

`--qmd` additionally creates a project-local `.qmd` index configuration and
adds a `qmd mcp` server to project-scoped Codex and Claude Code configuration.
Existing unrelated MCP configuration is preserved; an existing conflicting
`qmd` definition stops initialization. The command detects but does not install
QMD, download models, update the index, or generate embeddings.

## Safety boundaries

- All package sources are checked against their manifest checksums.
- All writes are staged and applied with backups and rollback.
- Concurrent lifecycle writes are prevented by a local operation lock.
- Absolute paths, parent traversal, symbolic-link traversal, filesystem roots,
  the user's home directory, and `.obsidian` targets are rejected.
- `.vault-os/config.yaml` and all other instance files remain owner-controlled.
- Agent adapter refreshes use the same operation lock and transactional writer
  as release lifecycle commands.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Command succeeded; `doctor` found no errors; `diff` found no conflicts |
| `1` | Invalid package, configuration, installation, filesystem operation, or unhealthy `doctor` result |
| `2` | A protected-file, path, installation, or concurrent-operation conflict was detected |

`--json` emits successful plans and doctor reports as structured JSON for
automation. Command errors remain concise messages on standard error.

Common errors and their safe resolution are listed in
[Troubleshooting](../how-to/troubleshooting.md).
