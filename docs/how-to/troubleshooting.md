# Troubleshooting

Run commands from the Vault-OS checkout and use the checkout's virtual
environment explicitly:

```bash
.venv/bin/python -m vault_os doctor "/path/to/My Vault" --json
```

Add `--ai` when diagnosing initialized agent adapters or QMD.

## `ModuleNotFoundError: No module named 'yaml'`

The command is using a Python environment without PyYAML. Prepare and use the
repository environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m vault_os --help
```

Running `./bin/vault-os` without activating the environment may select the
system Python. Either activate `.venv` first or keep using
`.venv/bin/python -m vault_os`.

## `install conflicts`

The target already contains at least one path that Vault-OS would manage, or it
already has installation metadata. The installer does not overwrite or adopt
such files.

- Use a different empty vault for a new installation.
- Use `--system-root` with an unused directory for side-by-side adoption.
- Preserve and deliberately migrate legacy files; do not rename or delete them
  merely to make the error disappear.

## `managed file was changed locally`

The installed file no longer matches its recorded checksum. Preserve the local
version, move legitimate customization to vault-owned content, and restore the
exact file from the previously installed release. Then rerun `doctor` and
`diff`. See [Resolve a managed-file conflict](upgrade-recover-remove.md#resolve-a-managed-file-conflict).

## `managed file is missing`

Restore the missing file from the previously installed release or restore the
vault backup. Do not copy the replacement from a newer release before the old
installation has passed its checksum check.

## `another operation or a stale operation lock exists`

Another lifecycle command may still be running. Do not remove the lock until
that possibility has been excluded. If it is stale, follow
[Recover from an interrupted command](upgrade-recover-remove.md#recover-from-an-interrupted-command).

## `agent adapter target was changed locally`

Generated `AGENTS.md`, `CLAUDE.md`, or a provider skill wrapper was edited after
initialization. The refresh stops to avoid data loss. Preserve the changes,
move durable vault-specific context into an instance-owned note referenced by
`.vault-os/runtime/agent-context.yaml`, restore the generated artifact, and run
`agent-init` again.

There is no automatic merge for pre-existing or locally changed agent
instruction files.

## QMD command is not available

Confirm that QMD works in the same environment used by the client:

```bash
command -v qmd
qmd --version
```

If necessary, refresh the adapter with the absolute executable path:

```bash
.venv/bin/python -m vault_os agent-init "/path/to/My Vault" \
  --qmd \
  --qmd-command "/full/path/to/qmd"
```

Then run `qmd update`, `qmd embed`, and `qmd status` from the vault root before
repeating `doctor --ai`.

## Existing QMD or MCP configuration conflicts

Vault-OS preserves unrelated provider configuration but refuses to replace an
existing server named `qmd` with a different definition. Compare the existing
`.codex/config.toml` or `.mcp.json` entry with the project-local adapter. Keep
one explicit owner for the `qmd` definition; do not maintain two competing
configurations.

## `doctor` reports an unapplied configuration change

Configuration was edited after the last successful update. Inspect and apply
it:

```bash
.venv/bin/python -m vault_os diff "/path/to/My Vault"
.venv/bin/python -m vault_os update "/path/to/My Vault"
```

## Exit codes

- `0`: success or a healthy doctor result;
- `1`: invalid package, configuration, installation, filesystem operation, or
  unhealthy doctor result; and
- `2`: protected-file, path, installation, or concurrent-operation conflict.

Use `--json` when collecting diagnostic evidence. Do not publish vault content,
credentials, absolute private paths, or complete instance configuration in an
issue. Include the Vault-OS package version, installed version, command, exit
code, and redacted error text.
