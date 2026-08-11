# ADR 0006: Provider-neutral agent adapters

- Status: Accepted
- Date: 2026-08-11

## Context

Vault-OS already supplies portable runtime rules and Agent Skills, but agent
clients discover project instructions and skills through provider-specific
locations. Codex reads `AGENTS.md` and `.agents/skills`; Claude Code reads
`CLAUDE.md` and `.claude/skills`. QMD can provide the same local search through
MCP, but each client uses a different project configuration format.

Copying the complete rules and skills into every provider directory would
create competing canonical sources. Writing directly into global client
configuration would also break vault portability and exceed the authority of a
vault installer.

## Decision

- The root `AGENTS.md` is the generated provider-neutral instruction source.
- The common agent lifecycle depends on a provider-adapter contract and
  registry, not on provider identifiers, discovery paths, or configuration
  formats. Provider modules own those details.
- Built-in Codex and Claude Code adapters are registered separately. Claude
  Code receives a thin `CLAUDE.md` that imports `AGENTS.md`.
- Each adapter exposes provider-native skill wrappers. Each wrapper preserves
  the canonical skill metadata and directs the client to the managed `SKILL.md`
  in the configured Vault-OS system root.
- `agent-init` is separate from release installation so AI integration remains
  optional and explicit. Both providers are initialized by default.
- Generated adapter artifacts are recorded with checksums in instance state.
  A refresh may replace only the previously generated unchanged version.
- Existing unrelated provider configuration is preserved. Provider-owned QMD
  sections are added only when they do not collide with an existing definition.
- QMD integration is project-local, optional, credential-free, and uses the
  external `qmd mcp` command. Vault-OS neither installs QMD nor creates models
  or embeddings.
- Provider configuration never modifies `.obsidian` or global agent settings.
- A further local client is integrated by implementing and registering another
  adapter. The shared lifecycle, QMD index generator, CLI choices, and doctor
  orchestration require no provider-specific branch.

## Consequences

- Core vault behavior and skill content remain independent of the chosen model
  vendor while Codex and Claude Code use their native discovery mechanisms.
- Provider-specific code is confined to `vault_os/providers`; the shared
  orchestrator remains provider-neutral.
- A user can initialize one or both clients without duplicating maintained
  operating rules.
- Locally edited generated adapters cause an explicit conflict instead of
  silent data loss.
- Project-scoped MCP configuration still requires client trust and an installed
  QMD executable. Model behavior and user permissions remain client concerns;
  adapter presence alone is not a security boundary.
- Browser-only ChatGPT and claude.ai sessions do not receive local vault access
  from these files.
