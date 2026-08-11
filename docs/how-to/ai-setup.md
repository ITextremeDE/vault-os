# Set up AI assistance

Vault-OS does not include an AI model or grant an agent access to a vault. It
generates project instructions and thin skill-discovery adapters for local
clients that the user has installed and explicitly authorized.

Built-in adapters currently support Codex and Claude Code. The shared Vault-OS
core remains independent of both providers.

## Install a supported client

Install and authenticate at least one local client using its official
documentation:

- [Codex CLI](https://developers.openai.com/codex/cli/)
- [Claude Code](https://code.claude.com/docs/en/overview)

A browser-only ChatGPT or claude.ai conversation cannot read local Vault-OS
files merely because the adapters exist.

## Install useful agent modules

Agent clients can use the core without optional skills. A practical AI-enabled
knowledge setup adds:

```bash
.venv/bin/python -m vault_os install "/path/to/My Vault" \
  --module agents \
  --module search \
  --module knowledge \
  --module audit \
  --module navigation \
  --module templates
```

For an existing Vault-OS installation, add the module identifiers to
`Vault-OS/config.yaml`, then run `diff` and `update` as described in the
[upgrade guide](upgrade-recover-remove.md).

The optional `bootstrap` command may create the user-owned profile, README,
dashboard, and PARA overview notes before provider initialization. It does not
create `AGENTS.md`; provider-neutral agent instructions remain the explicit
responsibility of `agent-init`.

## Initialize provider discovery

Initialize only the client you use:

```bash
.venv/bin/python -m vault_os agent-init "/path/to/My Vault" \
  --provider codex
```

or:

```bash
.venv/bin/python -m vault_os agent-init "/path/to/My Vault" \
  --provider claude
```

Omitting `--provider` initializes every registered adapter. Provider selection
is additive: rerunning the command with another provider adds it and does not
remove an initialized provider. When refreshing only one selected provider,
repeat the same `--provider` option. Version `0.1` has no provider de-initialize
command.

`agent-init` safely refreshes unchanged generated adapters and refuses to
overwrite a locally modified artifact. It also refuses to run when the
installed release lock differs from the package metadata; run `diff` and
`update` first.

The command creates:

- `AGENTS.md` as the shared instruction source;
- `CLAUDE.md` as a thin import when Claude Code is selected;
- `.agents/skills/<name>/SKILL.md` wrappers for Codex; and
- `.claude/skills/<name>/SKILL.md` wrappers for Claude Code.

`AGENTS.md` and `CLAUDE.md` are visible shared instructions. Provider wrappers,
QMD data, client configuration, and the generated integration record at
`.vault-os/integrations/agents.yaml` are device-local. On a second synchronized
device, run `device-sync` and then `agent-init` locally; do not copy the hidden
runtime folders from another device.

The actual installed skills remain canonical below the configured system root,
normally `99 System/04 Assets/Skills`. Provider wrappers reference those files
instead of copying their instructions.

If `AGENTS.md`, `CLAUDE.md`, or a generated skill path already contains
unmanaged content, initialization stops. Back up the existing instructions and
decide how to consolidate them. Vault-specific supplemental context can live in
an ordinary Markdown note whose path is added to `readOrder` in
`Vault-OS/runtime/agent-context.yaml`; rerunning `agent-init` then includes that
note in the generated startup order. There is no automatic instruction merge.

## Start the client

Launch the selected client with the vault as its working directory:

```bash
cd "/path/to/My Vault"
codex
```

or:

```bash
cd "/path/to/My Vault"
claude
```

The client still controls filesystem permissions, command approvals, model
selection, authentication, and network access. Vault-OS instructions guide
behavior but are not a security boundary.

From the Vault-OS checkout, validate the generated integration:

```bash
.venv/bin/python -m vault_os doctor "/path/to/My Vault" --ai
```

Within the client, verify that it can name the loaded Vault-OS instruction file
and discover an installed skill. Claude Code also exposes `/memory`, `/skills`,
and `/mcp` diagnostics. Do not claim a client works until an actual session has
successfully read the vault.

Automated tests validate the generated Codex and Claude Code artifacts and the
QMD configuration contracts. A dated client run is stronger evidence than
those structural tests. Current executed-client evidence and explicitly skipped
clients are recorded under [`docs/validation`](../validation/).

## Add QMD search

[QMD](https://github.com/tobi/qmd) is an optional external local-search engine.
Vault-OS does not bundle, install, update, or relicense it. Current upstream QMD
requires Node.js 22 or newer, or Bun, and can be installed with:

```bash
npm install -g @tobilu/qmd
qmd --version
```

Enable the project-local integration from the Vault-OS checkout:

```bash
.venv/bin/python -m vault_os agent-init "/path/to/My Vault" \
  --provider codex \
  --qmd
```

Use the provider already selected for the vault, or omit `--provider` only when
all registered adapters are wanted.

If `qmd` is not on `PATH`, pass an explicit executable:

```bash
.venv/bin/python -m vault_os agent-init "/path/to/My Vault" \
  --qmd \
  --qmd-command "/full/path/to/qmd"
```

Build the project-local index from the vault root:

```bash
cd "/path/to/My Vault"
qmd update
qmd embed
qmd status
```

`qmd update` builds the text index. `qmd embed` enables semantic and hybrid
search and may download local models on first use. QMD stores the project index
under `.qmd`; Vault-OS generates `.qmd/.gitignore` so runtime index data is not
committed accidentally.

`agent-init --qmd` adds a project-scoped `qmd mcp` definition to the selected
providers. It preserves unrelated provider configuration and an already
compatible `qmd` definition, but stops on a conflicting definition. Finish
with:

```bash
.venv/bin/python -m vault_os doctor "/path/to/My Vault" --ai
```

Search results are candidates, not canonical knowledge. Agents must retrieve
the original Markdown note before using a result as evidence or changing it.

QMD activation is persistent in the instance integration state. Version `0.1`
has no automatic QMD de-initialize command; restoring the pre-activation backup
is the safe reversal path.

### Use an externally managed QMD runtime

An existing device-local QMD service or client plugin can remain externally
managed. Do not also pass `agent-init --qmd`; that would create a second
project-local index and competing MCP configuration.

Describe only the portable contract in the synchronized
`Vault-OS/integrations/search.yaml` file:

```yaml
indexes:
  - id: vault-qmd
    engine: qmd
    management: external
    collection: vault
    capabilities:
      - lexical
      - semantic
      - mcp
    deviceLocal: true
    providerBindings:
      - codex
    refreshPolicy: Refresh before retrieval when the configured freshness limit is exceeded.
```

Do not put absolute paths, model files, caches, credentials, or machine-specific
commands in the synchronized record. Configure and verify those on each device
with the external runtime's own status and refresh commands. In this mode,
`doctor --ai` intentionally reports the Vault-OS-managed QMD integration as
disabled; that is not a claim about the external runtime.

## Provider-neutral extension

Additional local clients can implement the
[provider adapter contract](../reference/provider-adapters.md). Provider code
owns discovery paths and configuration formats; the common lifecycle contains
no provider-specific branch.
