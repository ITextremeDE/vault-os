# ADR 0009: Localized managed templates

- Status: Accepted
- Date: 2026-08-11

## Context

The first portable extraction reduced established MindOS templates to short
English skeletons. Field and path materialization made those files technically
portable but did not preserve their useful structure, Dataview queries,
guidance, or presentation. Hard-coding the German originals as the only package
source would restore one vault while making Vault-OS language-dependent.

Tokenizing every sentence would make templates unreadable and translations
fragile. Treating the old files as local edits would also conflict with managed
ownership and future updates.

## Decision

- Every managed template keeps one complete canonical English source.
- A manifest entry may provide complete `localizedSources`, each protected by
  its own checksum.
- The lifecycle chooses the exact configured `vault.language`, then its primary
  language subtag, and finally English as the fallback.
- Language selection occurs before field, value, module-field, and path
  materialization. All variants therefore share one semantic and ownership
  contract.
- The initial package provides complete English and German variants for all 21
  content templates and the template-module README.
- Reusable structure from MindOS is retained, while references to a particular
  person, organization, vault, task system, or external service remain outside
  the portable language sources.

## Consequences

- MindOS can use rich German templates without maintaining conflicting local
  copies of managed files.
- English remains a complete default rather than a degraded fallback.
- Additional languages require whole reviewed sources, manifest checksums, and
  normal release validation.
- Personal defaults and integration-specific behavior remain in visible
  instance configuration or user content instead of being mistaken for German
  localization.
