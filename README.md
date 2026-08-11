# Vault-OS

Vault-OS is a portable, local-first operating layer for Obsidian vaults.
It provides versioned system rules, schemas, workflows, reusable assets,
automation foundations, and runtime conventions without owning a vault's
content or identity.

## Status

Vault-OS is under active development and has not reached its first public
release. Installation and update behavior have been validated against both a
clean vault and a hash-verified copy of an existing real-world vault. Publishing
the initial `0.1.0` release remains pending.

## Goals

- Keep the operating layer separate from vault-specific content and settings.
- Allow every user to choose the name and language of their vault.
- Install a new vault without personal, organizational, or source-vault data.
- Update managed Vault-OS files without overwriting local content or
  customizations.
- Keep the system transparent, inspectable, and usable as ordinary files.

## Non-goals

- Shipping a pre-populated personal vault.
- Prescribing a user's projects, areas, contacts, or private workflows.
- Hiding the system behind a hosted service or proprietary file format.
- Modifying `.obsidian` settings as part of the portable core.

## Ownership model

Vault-OS distinguishes between three ownership domains:

- **Managed files** belong to a specific Vault-OS release and are updated only
  through the Vault-OS tooling.
- **Instance files** belong to the vault owner and are never overwritten by a
  Vault-OS update.
- **Runtime files** are generated locally and never supplied as release
  content.

The updater uses manifests and checksums recorded in the local release lock. If
a managed file was changed locally, an update stops before writing anything and
reports the conflict instead of overwriting the file.

## Repository layout

```text
src/core/                 Portable core files
src/modules/              Optional Vault-OS modules
instance-template/        Neutral instance configuration
manifests/                Ownership, source, target, and checksum declarations
vault_os/                 Lifecycle command implementation
bin/                      Executable command wrapper
analysis/                 Canonical source classification data
scripts/                  Development and validation tools
tests/                    Automated checks and test vaults
docs/adr/                 Architecture decision records
docs/analysis/            Human-readable analysis results
docs/reference/           Technical contracts and formats
docs/validation/          Evidence from release acceptance checks
```

The current extraction baseline is documented in the
[MindOS portability analysis](docs/analysis/mindos-portability-matrix.md).
The [manifest reference](docs/reference/manifests.md) defines the current
package contract.

## Lifecycle commands

The repository is directly executable after installing the Python dependency:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
source .venv/bin/activate
./bin/vault-os install "/path/to/My Vault" --module para --module knowledge
./bin/vault-os doctor "/path/to/My Vault"
```

Change the selected modules or other instance settings in
`.vault-os/config.yaml`, inspect the result, and then apply it:

```bash
./bin/vault-os diff "/path/to/My Vault"
./bin/vault-os update "/path/to/My Vault"
```

Installation and updates are transactional. Existing instance files are
preserved, locally changed managed files stop an update, and `.obsidian` is
never modified. See the [CLI reference](docs/reference/cli.md) for the complete
contract.

## AI and agent integration

Vault-OS is designed for direct work by humans and AI agents. It provides the
portable rules, schemas, workflows, prompts, skills, validation, and runtime
context that an agent needs to operate consistently inside a vault. It does not
bundle an AI model, agent client, or permission system.

An agent runtime must still have explicitly authorized access to the vault and
must load both its host instructions and the installed Vault-OS context.
Agent-facing assets can be selected during installation, for example:

```bash
./bin/vault-os install "/path/to/My Vault" \
  --module agents \
  --module search \
  --module knowledge \
  --module audit
```

Installing these modules places their managed prompts and skills in the
configured system root. Registering those skills with Codex, Claude Code, or
another agent runtime remains the responsibility of a provider adapter.
Vault-OS keeps the portable core independent from any one AI vendor.

Instance-owned integration settings live under `.vault-os`:

- `runtime/agent-context.yaml` defines the capture path and source read order;
- `integrations/search.yaml` declares approved search sources and precedence;
- `integrations/automation.yaml` records automation contracts and ownership.

Credentials, active schedules, model selection, tool permissions, indexes,
caches, and current runtime state remain in their canonical external systems.

### Recommended local search: QMD

[QMD](https://github.com/tobi/qmd) is the recommended optional local search
engine for agent-assisted Vault-OS installations. It is an external project
licensed under the MIT License. QMD indexes Markdown and provides BM25
full-text search, vector search, and local LLM reranking. It can be used from
its CLI or through its MCP server.

QMD is a good fit because it keeps the searchable index local while giving an
agent a faster orientation path than scanning an entire vault. Search hits are
still candidates: the agent must retrieve the relevant original note before
using it as evidence or changing content.

Vault-OS does not bundle, fork, install, update, or relicense QMD. Install it
separately using its upstream documentation. A provider adapter may then:

1. detect the configured QMD executable and compatible version;
2. create or select a collection scoped to the installed vault;
3. define explicit refresh and embedding behavior;
4. expose QMD to the agent through CLI or MCP;
5. register the portable local-search skill;
6. report executable, collection, index, and MCP health without exposing data.

The current Vault-OS release provides the provider-neutral configuration and
search skill, but not this automatic adapter. Without QMD, an agent may still
use ordinary filesystem search such as `rg`; semantic and hybrid retrieval are
then unavailable.

## Current implementation

- All 15 pure core sources, all 88 pure module sources, both pure instance
  sources, and all portions of the 13 mixed sources have been extracted into
  their assigned ownership domains.
- The current package contains 25 core files, 78 files in 14 optional modules,
  11 instance seeds, and one declared runtime artifact.
- The validator is vault-neutral and loads module models, field mappings, and
  register values from installed and instance-owned configuration.
- The sole runtime-history source remains deliberately excluded from release
  content; runtime state is generated and owned by each installation.
- Transactional installation, update, diff, doctor, release locking, package
  integrity validation, and managed-file conflict protection are implemented.
- Clean-vault installation and update behavior are covered by automated
  integration tests. The lifecycle has also passed a hash-verified installation,
  update, validation, and conflict test against a temporary copy of an existing
  real-world vault.

## Development roadmap

1. [x] Classify the existing operating layer by ownership and portability.
2. [x] Extract and neutralize the portable core.
3. [x] Implement deterministic install, update, diff, and doctor commands.
4. [x] Validate installation in a clean test vault.
5. [x] Validate updates without changing instance-owned files in test vaults.
6. [x] Validate installation and updates against an existing real-world vault.
7. [ ] Publish version `0.1.0`.

## Validation

The vault validator requires PyYAML. Prepare an isolated environment once:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Run the repository checks with:

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/check_portability.py
.venv/bin/python scripts/validate_portability_matrix.py
.venv/bin/python scripts/validate_manifests.py
```

The [real-vault lifecycle report](docs/validation/2026-08-11-real-vault-lifecycle.md)
records the pre-release acceptance evidence and its remaining migration boundary.

## License

Vault-OS is licensed under the [Mozilla Public License 2.0](LICENSE). Changes to
covered Vault-OS files remain available under the MPL when distributed. Files
created separately by a vault owner, including personal vault content, are not
made part of Vault-OS merely because they coexist in the same vault.

Vault-OS is an independent project and is not affiliated with or endorsed by
Obsidian.
