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

## `bootstrap conflicts`

A configured bootstrap target is not a safe regular-file destination. The
command preflights every target and creates nothing when one target conflicts.

- If the target is an existing regular file, Vault-OS preserves it and does not
  report a conflict.
- If the target is a directory or symbolic link, choose another filename in
  `Vault-OS/config.yaml` or resolve the target manually after making a backup.
- If bootstrap requires the current package, run `doctor`, `diff`, and
  `update` before trying again.

Do not move existing content merely to make Vault-OS replace it; bootstrap does
not merge or adopt user files.

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
`Vault-OS/runtime/agent-context.yaml`, restore the generated artifact, and run
`agent-init` again.

There is no automatic merge for pre-existing or locally changed agent
instruction files.

## `device sync conflicts`

`device-sync` found an incomplete or inconsistent synchronized file set and did
not create or refresh the local release lock.

- **Managed file is missing or does not match:** wait for synchronization to
  finish and confirm that the local checkout is the exact package version used
  on the primary device.
- **Synchronized instance file is missing:** enable Obsidian Sync's **Sync all
  other types** setting and ensure `Vault-OS/` is not excluded.
- **Unselected managed file is still present:** wait until synchronization has
  delivered the deletion from the primary device.

Do not copy `.vault-os/lock.json` from another device and do not edit it by
hand. Rerun `device-sync`, then `doctor`, only after the synchronized state is
complete.

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
existing server named `qmd` with a different definition. A semantically
identical definition is preserved as-is. Invalid TOML or JSON is also rejected
instead of being rewritten. Compare the existing `.codex/config.toml` or
`.mcp.json` entry with the project-local adapter. Keep one explicit owner for
the `qmd` definition; do not maintain two competing configurations.

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
