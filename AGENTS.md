# AGENTS.md — Vault-OS repository

## Scope

This repository builds the portable Vault-OS operating layer for independently
named Obsidian vaults. Repository development and an installed vault are
different scopes: edit package sources here, and use lifecycle commands for a
target vault.

## Project boundaries

- Keep Vault-OS provider-neutral, AI-first, local-first, and independent of any source
  vault, user, organization, language, or fixed system-root name.
- Do not read from or modify a source or other real vault unless the user
  explicitly places that vault in scope.
- Never target `.obsidian`; Obsidian settings and synchronization are outside
  Vault-OS ownership.
- Preserve the managed, instance, and runtime ownership model defined in
  `docs/adr/0001-managed-files-and-instance-ownership.md`.
- Treat files generated in an installed vault as user data. Never overwrite a
  locally changed file silently.

## Change workflow

1. Read the relevant ADR, manifest contract, implementation, and tests first.
2. Make the smallest coherent change and preserve unrelated working-tree edits.
3. Update manifest entries and SHA-256 checksums whenever package sources
   change. Advance the development version when package behavior changes.
4. Update the CLI reference, changelog, and an ADR when their established
   contracts are affected.
5. Do not commit, push, publish, or modify a real vault without explicit user
   authorization.

## Validation

Create and activate the documented virtual environment before running checks.
The acceptance suite is:

```bash
python3 -m unittest discover -s tests
python3 scripts/check_portability.py
python3 scripts/validate_portability_matrix.py
python3 scripts/validate_manifests.py
git diff --check
```

Report skipped runtime checks and distinguish a missing local dependency from a
product failure. Do not claim Codex, Claude Code, QMD, or a remote publication
was tested unless that client or service was actually exercised.

## Agent integration

- `AGENTS.md` is the canonical shared instruction source.
- `CLAUDE.md` imports this file; do not duplicate these rules there.
- Codex project skills use `.agents/skills`; Claude Code project skills use
  `.claude/skills`.
- Provider adapters must point to canonical managed Vault-OS skills instead of
  forking their complete instructions.
- Provider-specific discovery, configuration, and diagnostics belong in
  `vault_os/providers`; keep the common lifecycle free of provider branches.
- QMD is an optional external dependency. Search hits are candidates; retrieve
  the original source before treating a result as evidence.
