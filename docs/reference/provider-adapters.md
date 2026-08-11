# Provider adapter reference

Vault-OS keeps agent instructions and canonical skills independent of any AI
vendor. Client-specific discovery and configuration live behind provider
adapters in `vault_os/providers`.

## Layers

1. Package skill sources live under `src/modules/<module>/skills`.
2. Installed canonical skills live below the configured system root, normally
   `99 System/04 Assets/Skills`.
3. Provider adapters generate thin discovery wrappers in the location expected
   by the client. Built-in adapters currently use `.agents/skills` for Codex
   and `.claude/skills` for Claude Code.

Provider wrappers contain metadata and a reference to the installed canonical
`SKILL.md`; they do not copy its complete instructions.

## Contract

An adapter subclasses `ProviderAdapter` and declares:

- a stable lowercase `provider_id`;
- a human-readable `display_name`;
- a project-local `skill_root` outside `.obsidian`; and
- search-ignore patterns for its generated discovery files.

Adapters may additionally provide:

- thin client-specific instruction artifacts;
- project-local QMD or MCP configuration; and
- provider-specific doctor checks.

Register the adapter in `vault_os/providers/__init__.py`. The common lifecycle
then derives CLI selection, generated skill targets, QMD exclusions, refreshes,
and diagnostics from the registry. It contains no provider-specific branch.

## Ownership and safety

- `AGENTS.md` is the shared generated instruction source.
- `AGENTS.md` and thin visible instruction imports may synchronize between
  devices; their content must not depend on device-local QMD activation.
- Installed system-root skills are the canonical operational copies.
- Generated provider artifacts are checksum-protected and refreshed only while
  unchanged.
- Provider wrappers, integration state, client configuration, and indexes in
  dot-prefixed paths are initialized independently on every device.
- Existing client configuration is merged only by the owning adapter.
- Global client settings and `.obsidian` remain outside Vault-OS ownership.

Adding a provider requires adapter code, documentation, and tests in the
package. Version `0.1` does not load untrusted third-party adapters dynamically.
