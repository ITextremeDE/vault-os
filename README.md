# Vault-OS

**A portable, AI-first and local-first framework for Obsidian vaults.**

Vault-OS provides versioned rules, schemas, workflows, reusable assets,
validation, and agent context without owning a vault's content, name, language,
or identity. Use Obsidian Sync for vault content and shared configuration while
AI clients, search indexes, credentials, and runtime settings remain
device-local.

It is not a pre-populated second brain, hosted service, Obsidian plugin, or AI
model. It is an inspectable file-based system that is managed alongside the
vault owner's content without taking ownership of that content.

## Status

Vault-OS is under active development and has not reached its first public
release. Installation and update behavior have been validated against a clean
vault and a hash-verified copy of an existing real-world vault. A deliberate
side-by-side production migration into a fresh Vault-OS instance has also been
completed and validated. Publishing `0.1.0` remains pending.

Use the current `main` branch for evaluation and development, not as a stable
release contract.

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
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Install a practical personal-knowledge profile into a new vault:

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

The installer may create the target directory. Open it in Obsidian after the
command succeeds. For an existing vault, custom language or paths, and
side-by-side adoption, follow the complete [installation guide](docs/how-to/install.md).

A local coding agent such as Codex or Claude Code can also perform the complete
installation when it has authorized filesystem and terminal access. Give it the
target vault, desired modules, and permission boundaries, then ask it to follow
the [agent-assisted installation procedure](docs/how-to/install.md#let-an-ai-agent-install-vault-os).
A browser-only LLM can explain the process but cannot install local files.

## What Vault-OS installs

The mandatory core provides:

- operating principles and change rules;
- portable schema and metadata conventions;
- instance registers and runtime contracts;
- deterministic validation; and
- manifest-driven installation, update, device synchronization, diff, and
  health checks.

Fourteen optional modules add PARA, inbox, journal, knowledge processing,
contacts, publishing, templates, review, governance, Git, search, navigation,
agent conventions, and audits. Every module is disabled by default. The
[module catalog](docs/reference/modules.md) explains each module and suggests
useful profiles.

Every installation creates the configured inbox directory. With `para`, it
also creates the configured projects, areas, resources, and archive roots; with
`journal`, the configured journal root and its daily, weekly, and yearly
subdirectories. These directories and everything later placed inside them
remain user-owned and are not recorded as managed release content.

Vault name, language, folder names, enabled modules, registers, and local
integration choices belong to the installed instance. `MindOS` is not embedded
as a required name or identity.

The optional `bootstrap` command adds a user-owned vault entry point after
installation: a profile note, root `README.md`, `Dashboard.md`, and READMEs for
the configured inbox and enabled PARA and journal structures. It creates
missing files only and never adopts or overwrites existing content. Filenames
are configured below `bootstrap` in `Vault-OS/config.yaml`; for example,
`profileFile: Ich.md` produces the German filename without making it a product
default.

## How it works

Release manifests map package sources to target paths and checksums. The
installer validates the complete package, stages all writes, and records the
installed release in `.vault-os/lock.json` only after a successful transaction.
Managed templates and views are materialized during the lifecycle from the
installed field profile and path configuration. Their portable sources remain
stable while each vault receives directly usable field names, values, and paths.
Templates use complete English sources by default and complete German sources
when `vault.language` is `de` or a regional variant such as `de-DE`. Languages
without a packaged translation fall back to English.

Vault-OS distinguishes three ownership domains:

- **Managed files** belong to a Vault-OS release and are changed only through
  lifecycle commands.
- **Instance files** belong to the vault owner and are created only when
  missing; updates never overwrite them.
- **Runtime files** are generated locally and are not release content.

Bootstrap files are ordinary user content. They are neither managed release
files nor instance seeds, and their content belongs entirely to the vault after
creation.

Instance files use the visible `Vault-OS/` directory so Obsidian Sync and other
approved file synchronization can carry them between devices. Device-specific
release metadata, transactions, provider wrappers, client configuration, and
search indexes stay in hidden `.vault-os`, `.agents`, `.claude`, `.codex`, and
`.qmd` paths, including the project-local `.mcp.json` file.

Before an update, every installed managed file must still match its recorded
checksum. A missing or locally modified managed file stops the entire operation
instead of being overwritten. `.obsidian`, ordinary vault content, credentials,
external schedules, indexes, and client permissions remain outside Vault-OS
ownership.

## Operate and update an installation

Edit `Vault-OS/config.yaml` to change modules or instance paths and
`Vault-OS/schema/fields.yaml` to change local field or value mappings. Preview
and apply afterward so managed templates and views are materialized again:

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
  --module audit

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
- [Real-vault lifecycle validation](docs/validation/2026-08-11-real-vault-lifecycle.md)
- [Agent integration validation](docs/validation/2026-08-11-agent-integration.md)
- [Production vault migration validation](docs/validation/2026-08-11-production-vault-migration.md)

## Repository layout

```text
src/core/                 Portable core files
src/modules/              Optional Vault-OS modules
instance-template/        Neutral instance configuration
manifests/                Ownership, source, target, and checksum declarations
vault_os/                 Lifecycle and provider-adapter implementation
bin/                      Executable command wrapper
analysis/                 Canonical source classification data
scripts/                  Development and validation tools
tests/                    Automated checks and test vaults
docs/how-to/              Installation and operating guides
docs/reference/           Technical contracts and catalogs
docs/adr/                 Architecture decision records
docs/analysis/            Human-readable analysis results
docs/validation/          Release acceptance evidence
.github/workflows/        Automated acceptance checks
```

## Current implementation

- All 15 pure core sources, all 88 pure module sources, both pure instance
  sources, and all portions of the 13 mixed sources have been extracted into
  their assigned ownership domains.
- The package contains a required core, 14 optional modules, neutral instance
  seeds, and one declared runtime lock. The manifests are the canonical source
  for exact package contents.
- Transactional installation, user-owned bootstrap, update, diff, device
  synchronization, doctor, release locking, integrity validation, conflict
  protection, provider adapters, and optional QMD MCP integration are
  implemented.
- The lifecycle has passed automated clean-vault tests and hash-verified
  acceptance against a temporary copy of an existing real-world vault.
- A production vault has been migrated side by side into a fresh installation;
  the legacy source remained unchanged as the recovery copy.

## Release status

The extraction, lifecycle, provider-adapter, documentation, and production-vault
migration milestones are complete. Version `0.1.0` remains an unreleased
development build; operational release work is tracked outside this README.

## Development validation

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/check_portability.py
.venv/bin/python scripts/validate_portability_matrix.py
.venv/bin/python scripts/validate_manifests.py
git diff --check
```

Contribution rules are in [CONTRIBUTING.md](CONTRIBUTING.md). Report suspected
vulnerabilities through the private process in [SECURITY.md](SECURITY.md).

## License

Vault-OS is licensed under the [Mozilla Public License 2.0](LICENSE). Changes to
covered Vault-OS files remain available under the MPL when distributed. Files
created separately by a vault owner, including personal vault content, do not
become part of Vault-OS merely because they coexist in the same vault.

Vault-OS is an independent project and is not affiliated with or endorsed by
Obsidian, OpenAI, Anthropic, or QMD.
