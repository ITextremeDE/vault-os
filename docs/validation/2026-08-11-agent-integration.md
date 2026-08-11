# Agent integration validation

- Date: 2026-08-11
- Package: `0.1.0-dev.6`
- Scope: temporary primary and synchronized secondary vaults only

## Executed checks

A temporary primary vault was installed with the `agents`, `search`,
`knowledge`, and `para` modules. `bootstrap` created the profile, root README,
root dashboard, project overview, and area overview. The installed vault
validator reported zero errors and warnings after `agent-init --provider codex`
registered six skill wrappers.

The primary was copied to a secondary temporary vault while excluding the
documented device-local `.vault-os`, `.agents`, `.claude`, `.codex`, `.qmd`,
and `.mcp.json` paths.

`device-sync` on the secondary vault verified 65 managed files and eight visible
instance files, created one local release lock, and changed no synchronized
file. A local `agent-init --provider codex` then recreated the six wrappers;
the synchronized `AGENTS.md` already matched and was preserved. `doctor --ai`
reported the secondary installation healthy with no warnings or errors.

Codex CLI `0.147.0-alpha.6.5` was then executed as an ephemeral, read-only
session with the secondary temporary vault as its working directory. It read the
generated `AGENTS.md`, local `.agents/skills` wrappers, and all five synchronized
bootstrap notes. It returned the expected count and canonical profile type:

```text
bootstrap_files=5
profile_type=operating-document
```

The command exited successfully. A complete file-checksum snapshot before and
after the read-only session was identical. Host-level Codex
warnings about unrelated locally installed skills did not affect the Vault-OS
adapter result.

## Not executed

- Claude Code was not available on `PATH`; its adapter is covered structurally
  by automated integration tests, not by an actual client session.
- QMD was not available on `PATH`; its configuration merge and conflict
  handling are covered by automated tests, but indexing, embeddings, and MCP
  retrieval were not exercised.
- Obsidian Sync itself was not invoked. The file transfer reproduced its
  documented Vault-OS boundary by excluding all device-local hidden paths.
- No real vault and no `.obsidian` directory were read or modified.
