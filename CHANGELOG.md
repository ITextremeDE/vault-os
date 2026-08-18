# Changelog

All notable changes to Vault-OS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-08-18

### Added

- Added an instance-owned `formats.area` contract for choosing plain-text or
  Wiki-link area values while retaining canonical plain names in the area
  register.

### Changed

- Standardized German content templates on `# 🧩 Kontext & Aktionen` with a
  horizontal separator before the closing context and action section.
- Materialized PARA dashboard views now derive folder names from linked area
  notes when an instance selects Wiki-link area values.
- Advanced the development package to `0.3.0-dev.2` for configurable area
  representation including dashboard targets inside named area folders.
- Advanced the development package to `0.3.0-dev.3` for the German content
  template convention correction.

## [0.2.0] - 2026-08-18

### Changed

- Replaced positional organization/function pairs in contacts with validated
  role relation notes that link one person and one organization and can carry
  their own function, status, and optional validity period.
- Prefer the note's declared `created` property in managed Bases views and use
  the filesystem creation time only as a fallback.
- Qualify frontmatter columns in managed Bases views with `note.` so configured
  display names are applied consistently instead of falling back to lowercase
  property keys.
- Centralized repeated contact-role queries in one managed Bases asset with
  dedicated person-role and organization-contact views.
- Centralized repeated contact relationship and job displays in one managed
  Bases asset with context-aware views for the embedding contact note.
- Centralized project- and area-scoped PARA dashboard queries in managed Bases
  assets with live and archive views driven by the embedding dashboard's area.
- Replaced file- and property-based Dataview output in managed contact,
  conversation, project, and area templates with embedded Obsidian Bases views;
  retained Dataview only for individual Markdown task aggregation that Bases
  cannot represent.
- Advanced the development package to `0.2.0-dev.5` for normalized contact
  roles, metadata-first creation dates, reliable Bases column titles, and
  reusable contact and PARA dashboard views.

## [0.1.0] - 2026-08-12

### Added

- A private security-reporting policy for the public repository.
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
- Instance mappings for localized module fields, established filename
  conventions, and scalar-or-list registers during legacy-vault migration.
- Evidence for a validated side-by-side production-vault migration with
  preserved content and Git history.
- Instance-aware lifecycle materialization for managed templates and Bases
  views using configured field names, localized values, module fields, and paths.
- Explicit external-reference ID/URL pairs for established non-derived field
  names and documented per-value semantics for instance registers.
- Context-qualified preferred value mappings for deterministic materialization
  when a localized profile maps several stored values to one stable identifier.
- Complete German managed-template sources alongside the canonical English
  templates, with exact-language, primary-language, and English fallback.
- Rich template structures for all 21 contact, journal, knowledge, PARA, and
  publishing purposes, including portable Dataview queries and recurring
  context sections recovered from the original MindOS design.
- A portable index contract for documenting externally managed search runtimes
  without synchronizing device-local commands, models, caches, or indexes.

### Changed

- Reworked the README around the product value, verified installation paths,
  first-use guidance, provider-neutral AI setup, and concise support routing.
- Extended acceptance CI to cover the minimum supported Python 3.10 and the
  current Python 3.14 runtime.
- Replaced the README task checklist with a concise release status so
  operational planning remains in the designated project system.
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
- Advanced the development package to `0.1.0-dev.7` for required inbox
  directory creation during installation.
- Advanced the development package to `0.1.0-dev.8` for the user-owned inbox
  README bootstrap contract.
- Advanced the development package to `0.1.0-dev.9` for complete configured
  PARA and journal directory scaffolding.
- Advanced the development package to `0.1.0-dev.10` for localized legacy
  content validation.
- Advanced the development package to `0.1.0-dev.11` for instance-materialized
  managed artifacts and strengthened instance semantics.
- Advanced the development package to `0.1.0-dev.12` for localized, structurally
  complete managed templates.
- Advanced the development package to `0.1.0-dev.13` for explicit externally
  managed search-index contracts.

### Fixed

- Ignored macOS `.DS_Store` metadata when checking manifest source coverage
  without hiding other undeclared package files.
- Extended portability checks to installation-relevant manifest paths while
  preserving historical extraction origins as evidence.
- Corrected stale public-repository, package-content, and extraction status
  wording in the pre-release documentation.
- Preserved semantically compatible inline Codex QMD definitions and rejected
  conflicting or invalid TOML before writing.
- Prevented `agent-init` from running against package metadata newer than the
  installed release lock.
- Prevented external-reference diagnostics from exposing secret URL values.
- Excluded generated agent instructions and device-local provider wrappers from
  ordinary vault-content frontmatter validation.
- Created the configured `paths.inbox` directory during installation instead
  of leaving a new vault without its operational capture path.
- Added the missing create-only README to the configured inbox during vault
  bootstrap so its purpose is visible and the directory is not empty.
- Added the missing resources and archive roots plus the journal root and
  configurable daily, weekly, and yearly subdirectories, with create-only
  bootstrap READMEs for every structural directory.
- Prevented direct Obsidian template use and the review Bases view from ignoring
  localized instance fields, values, module fields, and configured paths.
- Restored the explicit authorization boundary for changes to top-level vault
  directories in both managed operating rules and generated agent instructions.
- Prevented portable extraction from replacing established rich templates with
  minimal English skeletons.

[Unreleased]: https://github.com/ITextremeDE/vault-os/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/ITextremeDE/vault-os/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ITextremeDE/vault-os/releases/tag/v0.1.0
