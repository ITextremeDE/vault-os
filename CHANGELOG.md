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

### Changed

- Extended the neutral instance configuration with the system root and module selection.
- Added PyYAML as the explicit runtime dependency for frontmatter and instance configuration.
