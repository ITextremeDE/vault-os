# Changelog

All notable changes to Vault-OS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial repository structure and project boundaries.
- MPL-2.0 licensing and repository ownership model.
- Neutral example configuration for independently named vaults.
- Automated check against source-vault and personal identifiers in distributable files.
- Complete file-by-file portability matrix for the initial MindOS system source.
- Matrix validator with optional live coverage checks against the source repository.
- Portable extraction of all 15 source files classified as pure core.
- Versioned manifests for managed core files, optional modules, instance seeds, and runtime artifacts.
- Manifest validation for ownership rules, path safety, checksums, source coverage, and extraction lineage.
- Complete domain split of the 13 mixed source files.
- Portable extraction of all 88 sources classified as optional modules.
- Neutral instance-owned contact relationship and relevance register seeds.
- Optional audit, governance, inbox, navigation, publishing, review, agent, and template modules.
- Manifest tests that require lineage coverage for pure module and instance sources as well as split sources.
- Machine-readable schema models for core, PARA, knowledge, contacts, and journal content.
- Neutral Git commit and local conversation-search skills with instance-owned policy.
- Configuration-driven, read-only vault validation without embedded source-vault assumptions.
- Neutral instance seeds for schema fields, registers, integrations, journal policy, validation, and agent context.
- Transactional `install`, `update`, `diff`, and `doctor` lifecycle commands.
- Local release locks with package fingerprints and managed-file checksums.
- Preflight conflict protection, package-integrity checks, rollback behavior,
  and create-only preservation of instance files.
- Integration tests for clean installation, safe updates, module changes,
  conflicts, symbolic-link protection, package tampering, and rollback.
- Hash-verified lifecycle acceptance against a temporary copy of an existing
  real-world vault.
- Provider-neutral `AGENTS.md` generation with native Codex and Claude Code
  instruction and skill discovery.
- Extensible provider registry that confines discovery paths, instruction
  shims, MCP configuration, and client diagnostics to adapter modules.
- Transactional `agent-init` command with checksum-protected provider adapters
  and `doctor --ai` health checks.
- Optional project-local QMD collection and MCP integration for Codex and
  Claude Code.
- Portable vault-search skill with retrieval-first evidence rules.
- Shared repository `AGENTS.md` with a thin Claude Code import adapter.
- Complete public user documentation for prerequisites, installation into new
  and existing vaults, agent-assisted installation, module selection, AI and
  QMD setup, upgrades, recovery, removal boundaries, and troubleshooting.
- Recommended Obsidian settings and core-plugin profile with module mappings,
  community-plugin boundaries, and explicit `.obsidian` ownership.
- Regression coverage for module field validation, runtime-lock ownership,
  release-metadata gating, and semantic Codex QMD configuration merging.
- Automated acceptance checks and a maintainer release procedure.
- `device-sync` verification for rebuilding device-local release metadata after
  Obsidian Sync or another approved file synchronization service has delivered
  a complete vault copy.
- Regression coverage for synchronized secondary-device setup and migration
  from the legacy hidden instance layout.
- Transactional, idempotent `bootstrap` command for a user-owned profile, root
  README, dashboard, and optional PARA project and area overviews.
- Instance-configurable bootstrap filenames with schema-aware frontmatter and
  localized semantic value mappings.

### Changed

- Extended the neutral instance configuration with the system root and module selection.
- Added PyYAML as the explicit runtime dependency for frontmatter and instance configuration.
- Allowed instance field profiles to map localized stored values to stable
  Vault-OS kind, type, and status identifiers.
- Documented the provider-neutral AI runtime boundary and QMD as an optional
  external local-search recommendation.
- Extended configured vault validation to module field types, lazy instance
  registers, type-specific requirements, filename patterns, and safe external
  reference pairs.
- Fixed the runtime contract to the single local release lock at
  `.vault-os/lock.json`.
- Moved canonical instance configuration and seeds from hidden `.vault-os`
  paths to the visible, synchronization-compatible `Vault-OS/` directory while
  keeping release, provider, client, and index state device-local.
- Made generated shared agent instructions independent of device-local QMD
  activation.
- Advanced the development package to `0.1.0-dev.5` for synchronized instance
  and device-local runtime separation.
- Advanced the development package to `0.1.0-dev.6` for the user-owned vault
  bootstrap contract.

### Fixed

- Preserved semantically compatible inline Codex QMD definitions and rejected
  conflicting or invalid TOML before writing.
- Prevented `agent-init` from running against package metadata newer than the
  installed release lock.
- Prevented external-reference diagnostics from exposing secret URL values.
- Excluded generated agent instructions and device-local provider wrappers from
  ordinary vault-content frontmatter validation.
