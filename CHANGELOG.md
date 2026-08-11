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

### Changed

- Extended the neutral instance configuration with the system root and module selection.
- Added PyYAML as the explicit runtime dependency for frontmatter and instance configuration.
- Allowed instance field profiles to map localized stored values to stable
  Vault-OS kind, type, and status identifiers.
- Documented the provider-neutral AI runtime boundary and QMD as an optional
  external local-search recommendation.
- Advanced the development package to `0.1.0-dev.3` for provider adapters and
  agent health validation.
