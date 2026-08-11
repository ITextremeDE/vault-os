# Vault-OS

Vault-OS is a portable, local-first operating layer for Obsidian vaults.
It provides versioned system rules, schemas, workflows, reusable assets,
automation foundations, and runtime conventions without owning a vault's
content or identity.

## Status

Vault-OS is under active development and has not reached its first public
release. The initial `0.1.0` release will be published only after installation
and update behavior have been validated against both a clean vault and an
existing real-world vault.

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

The updater will use a manifest and recorded checksums. If a managed file was
changed locally, an update must stop and report the conflict instead of
overwriting the file.

## Repository layout

```text
src/core/                 Portable core files
src/modules/              Optional Vault-OS modules
instance-template/        Neutral instance configuration
manifests/                Ownership, source, target, and checksum declarations
analysis/                 Canonical source classification data
scripts/                  Development and validation tools
tests/                    Automated checks and test vaults
docs/adr/                 Architecture decision records
docs/analysis/            Human-readable analysis results
docs/reference/           Technical contracts and formats
```

The current extraction baseline is documented in the
[MindOS portability analysis](docs/analysis/mindos-portability-matrix.md).
The [manifest reference](docs/reference/manifests.md) defines the current
package contract.

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
- Installation, update, diff, doctor, and release-lock behavior are not yet
  implemented.

## Development roadmap

1. Classify the existing operating layer by ownership and portability.
2. Extract and neutralize the portable core.
3. Implement deterministic install, update, diff, and doctor commands.
4. Validate installation in a clean vault.
5. Validate updates without changing instance-owned files.
6. Publish version `0.1.0`.

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

## License

Vault-OS is licensed under the [Mozilla Public License 2.0](LICENSE). Changes to
covered Vault-OS files remain available under the MPL when distributed. Files
created separately by a vault owner, including personal vault content, are not
made part of Vault-OS merely because they coexist in the same vault.

Vault-OS is an independent project and is not affiliated with or endorsed by
Obsidian.
