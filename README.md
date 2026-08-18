# Vault-OS

**Turn any Obsidian vault into a portable, AI-ready knowledge workspace without
giving up ownership of your files.**

**AI-first, local-first, and compatible with Obsidian Sync.** Vault-OS provides
versioned rules, schemas, workflows, reusable assets, validation, and agent
context without owning a vault's content, name, language, or identity. Shared
vault configuration can travel with ordinary Markdown files while AI clients,
search indexes, credentials, and runtime settings remain device-local.

For a concise overview and quick start, visit the
[Vault-OS project page on ITextreme](https://itextreme.de/vault-os).

Vault-OS helps you:

- keep knowledge in ordinary Markdown and YAML files you control;
- reproduce and safely update the working structure around that knowledge;
- work with provider-neutral instructions for authorized local AI agents; and
- use Obsidian Sync or another suitable file-sync service without treating
  device-local AI state as vault content.

It is not a pre-populated second brain, hosted service, Obsidian plugin, or AI
model.

## Status

Vault-OS `0.3.0` is the current published release. It adds instance-configured
plain-text or Wiki-link area values, keeps PARA dashboard folder queries aligned
with that choice, and standardizes the closing context/action section in German
content templates. Installation and update behavior have been validated against
clean vaults and synchronized temporary copies.

Use the `v0.3.0` tag for a reproducible installation. The `main` branch contains
ongoing development, and interfaces may continue to evolve throughout the
`0.x` release line.

## Requirements

- Python 3.10 or newer;
- Git to obtain or update the checkout;
- Obsidian to use the target directory as an Obsidian vault; and
- a backup before installing into an existing vault.

Vault-OS does not modify `.obsidian` and requires no Obsidian plugin for its
core.

An optional [recommended Obsidian profile](docs/how-to/obsidian-setup.md)
describes compatible editor settings, official core plugins, and carefully
scoped community-plugin choices. Vault-OS never applies that profile
automatically.

Codex, Claude Code, and [QMD](https://github.com/tobi/qmd) are optional runtime
choices. Vault-OS remains usable without them, but its workflows and context
model are designed primarily for collaboration with an authorized local AI
agent.

## Quick start

Clone the public repository and prepare an isolated Python environment:

```bash
git clone https://github.com/ITextremeDE/vault-os.git
cd vault-os
git checkout v0.2.0
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Install the recommended starter profile for personal knowledge management into
a new vault:

```bash
.venv/bin/python -m vault_os install "/path/to/My Vault" \
  --module para \
  --module inbox \
  --module journal \
  --module knowledge \
  --module templates

.venv/bin/python -m vault_os bootstrap "/path/to/My Vault"
.venv/bin/python -m vault_os doctor "/path/to/My Vault"
```

The installer may create the target directory. A successful health check ends
with `Status: healthy`. Then open the vault in Obsidian, start with its generated
`README.md` or `Dashboard.md`, and capture new material in the inbox.

For an existing vault, custom language or paths, and side-by-side adoption,
follow the complete [installation guide](docs/how-to/install.md).

A local coding agent such as Codex or Claude Code can perform the complete
installation when it has authorized filesystem and terminal access. Give it
the repository, exact target vault, desired profile, and permission boundaries,
then ask it to follow `AGENTS.md` and the
[agent-assisted installation procedure](docs/how-to/install.md#let-an-ai-agent-install-vault-os),
finish with `doctor`, and report every warning.

## What Vault-OS installs

The mandatory core combines operating rules, schemas, workflows, validation,
and a manifest-driven lifecycle for installation, updates, synchronization,
diffs, and health checks.

Fourteen optional modules add PARA, inbox, journal, knowledge processing,
contacts, publishing, templates, review, governance, Git, search, navigation,
agent conventions, and audits. Every module is disabled by default. The
[module catalog](docs/reference/modules.md) explains each module and suggests
useful profiles.

An installation contains the managed system, visible instance configuration,
a device-local release lock, and the configured user-owned inbox. The `para`
and `journal` modules add their configured directory structures. The optional
`bootstrap` command creates missing entry points such as `Profile.md`,
`README.md`, `Dashboard.md`, and directory READMEs without overwriting or
adopting existing content.

Vault name, language, paths, filenames, enabled modules, registers, and local
integration choices belong to the instance. `MindOS` is not embedded as a
required name or identity.

## How it works

Release manifests map package sources to target paths and checksums. The
installer validates and stages the complete change before recording it in
`.vault-os/lock.json`. Templates and views are materialized from each instance's
field and path mappings; English and German sources are included, with English
as the fallback for other languages.

Vault-OS distinguishes three ownership domains:

- **Managed files** belong to a Vault-OS release and are changed only through
  lifecycle commands.
- **Instance files** belong to the vault owner; updates never overwrite them.
- **Runtime files** are generated locally and are not release content.

Bootstrap files are ordinary user content and belong entirely to the vault
after creation.

Instance files use the visible `Vault-OS/` directory so Obsidian Sync and other
approved file synchronization can carry them between devices. Device-specific
release metadata, transactions, provider wrappers, client configuration, and
search indexes stay in the hidden `.vault-os/`, `.agents/`, `.claude/`,
`.codex/`, and `.qmd/` directories or the project-local `.mcp.json` file.

Before an update, every installed managed file must still match its recorded
checksum. A missing or locally modified managed file stops the entire operation
instead of being overwritten. `.obsidian`, ordinary vault content, credentials,
external schedules, indexes, and client permissions remain outside Vault-OS
ownership.

## Operate and update an installation

Edit `Vault-OS/config.yaml` to change modules or instance paths and
`Vault-OS/schema/fields.yaml` to change local field or value mappings and choose
`text` or `wiki-link` area values. Preview and apply afterward so managed
templates and views are materialized again:

```bash
.venv/bin/python -m vault_os diff "/path/to/My Vault"
.venv/bin/python -m vault_os update "/path/to/My Vault"
.venv/bin/python -m vault_os doctor "/path/to/My Vault"
```

Installation and updates are transactional. There is no automatic downgrade or
uninstall in version `0.1`; use a pre-change backup for release rollback or
removal. The complete operating procedure is documented in
[Upgrade, recover, and remove](docs/how-to/upgrade-recover-remove.md).

On another device, wait for the approved sync service to finish, use the same
Vault-OS package version, and rebuild only the device-local release record:

```bash
.venv/bin/python -m vault_os device-sync "/path/to/My Vault"
.venv/bin/python -m vault_os agent-init "/path/to/My Vault" --provider codex
.venv/bin/python -m vault_os doctor "/path/to/My Vault" --ai
```

`device-sync` does not start or control Obsidian Sync. It verifies the delivered
managed and instance files before writing `.vault-os/lock.json`. See the
[Obsidian setup guide](docs/how-to/obsidian-setup.md#use-obsidian-sync-on-more-than-one-device).

## AI and agent integration

Vault-OS is designed for direct work by humans and authorized local AI agents.
It supplies provider-neutral instructions, installed canonical skills, and
runtime context, but does not bundle a model, client, authentication, or
permission system.

Install useful agent modules and initialize one built-in provider:

```bash
.venv/bin/python -m vault_os install "/path/to/AI Vault" \
  --module agents \
  --module search \
  --module knowledge \
  --module audit \
  --module navigation \
  --module templates

.venv/bin/python -m vault_os agent-init "/path/to/AI Vault" \
  --provider codex

.venv/bin/python -m vault_os doctor "/path/to/AI Vault" --ai
```

Use `--provider claude` for Claude Code or omit the option to initialize all
registered adapters. The command generates a shared `AGENTS.md`, a thin
`CLAUDE.md` import when needed, and provider discovery wrappers under
`.agents/skills` or `.claude/skills`. Canonical skills remain below the
configured system root, normally `99 System/04 Assets/Skills`.

The common lifecycle depends on an extensible provider registry and contains no
Codex- or Claude-specific branch. Browser-only ChatGPT and claude.ai sessions do
not gain local vault access from these files.

Follow [Set up AI assistance](docs/how-to/ai-setup.md) for client installation,
provider initialization, permissions, QMD indexing, MCP, and end-to-end checks.

## Optional local search with QMD

[QMD](https://github.com/tobi/qmd) is the recommended optional local search
engine for AI-assisted Vault-OS installations. It provides keyword, semantic,
and hybrid retrieval and can expose the index through MCP.

Vault-OS does not bundle or install QMD. After installing it from upstream:

```bash
.venv/bin/python -m vault_os agent-init "/path/to/My Vault" \
  --provider codex \
  --qmd
cd "/path/to/My Vault"
qmd update
qmd embed
qmd status
```

The adapter creates a project-local `.qmd/index.yml`, configures `qmd mcp` for
the selected clients, and reports health through `doctor --ai`. Search results
remain candidates; an agent must retrieve the original Markdown note before
using it as evidence or changing it.

## Documentation

### How-to guides

- [Install Vault-OS](docs/how-to/install.md)
- [Configure Obsidian for Vault-OS](docs/how-to/obsidian-setup.md)
- [Set up AI assistance](docs/how-to/ai-setup.md)
- [Upgrade, recover, and remove](docs/how-to/upgrade-recover-remove.md)
- [Troubleshooting](docs/how-to/troubleshooting.md)
- [Release Vault-OS](docs/how-to/release.md)

### Reference

- [CLI commands and exit codes](docs/reference/cli.md)
- [Module catalog](docs/reference/modules.md)
- [Manifest and ownership contract](docs/reference/manifests.md)
- [Provider adapter contract](docs/reference/provider-adapters.md)

### Explanation and evidence

- [Architecture decisions](docs/adr/)
- [MindOS portability analysis](docs/analysis/mindos-portability-matrix.md)
- [Vault-OS 0.3.0 release validation](docs/validation/2026-08-18-v0.3.0-release.md)
- [Vault-OS 0.2.0 release validation](docs/validation/2026-08-18-v0.2.0-release.md)
- [Vault-OS 0.1.0 release validation](docs/validation/2026-08-12-v0.1.0-release.md)
- [Real-vault lifecycle validation](docs/validation/2026-08-11-real-vault-lifecycle.md)
- [Agent integration validation](docs/validation/2026-08-11-agent-integration.md)
- [Production vault migration validation](docs/validation/2026-08-11-production-vault-migration.md)

### Further reading

- [Vault-OS 0.1.0: A portable operating system for Obsidian vaults](https://itextreme.de/articles/vault-os-portables-betriebssystem-fuer-obsidian-vaults)

## Repository layout

```text
src/                      Portable core and optional module sources
instance-template/        Neutral instance configuration
manifests/                Ownership, paths, and checksums
vault_os/                 Lifecycle and provider adapters
docs/                     Guides, references, decisions, and evidence
tests/ and scripts/       Automated checks and validation tools
```

## Development and support

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/check_portability.py
.venv/bin/python scripts/validate_portability_matrix.py
.venv/bin/python scripts/validate_manifests.py
git diff --check
```

Questions, bug reports, and feature proposals belong in
[GitHub Issues](https://github.com/ITextremeDE/vault-os/issues). Contribution
rules are in [CONTRIBUTING.md](CONTRIBUTING.md). Report suspected vulnerabilities
through the private process in [SECURITY.md](SECURITY.md), not through a public
issue.

## License

Vault-OS is licensed under the [Mozilla Public License 2.0](LICENSE). Changes to
covered Vault-OS files remain available under the MPL when distributed. Files
created separately by a vault owner, including personal vault content, do not
become part of Vault-OS merely because they coexist in the same vault.

Vault-OS is an independent project and is not affiliated with or endorsed by
Obsidian, OpenAI, Anthropic, or QMD.
