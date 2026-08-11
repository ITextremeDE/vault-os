# ADR 0008: User-owned vault bootstrap

- Status: Accepted
- Date: 2026-08-11

## Context

The portable core installs the operating layer, while `agent-init` creates
provider instructions. A new vault still lacks a human entry point, personal or
team context, and initial navigation. Treating those notes as managed files or
instance seeds would let release ownership leak into user content. Hard-coding
`Ich.md` would also make one language and one source-vault convention part of
the portable product.

## Decision

- Vault-OS provides an explicit `bootstrap` command after installation.
- The command creates a profile note, root README, and root dashboard. With the
  `para` module enabled, it also creates global project and area overviews below
  their configured roots.
- Bootstrap filenames come from the instance configuration. The neutral profile
  default is `Profile.md`; an instance may select `Ich.md` or another Markdown
  filename.
- Generated frontmatter uses the installed field-role and semantic-value
  mappings, so the notes pass the configured validator without embedding one
  language's metadata vocabulary.
- Bootstrap files are ordinary user content. They have no manifest entries,
  release checksums, generated-state registry, or update behavior.
- Existing regular files are preserved byte-for-byte. Unsafe targets stop the
  complete transaction before any missing file is created.
- Repeating `bootstrap` creates only missing files. It never merges, adopts,
  refreshes, or deletes user content.
- `AGENTS.md` remains owned by the separate provider-neutral `agent-init`
  lifecycle because it must stay consistent with installed agent adapters.

## Consequences

- A fresh installation can become navigable without pretending to know the
  user's identity, projects, areas, or priorities.
- Personal filenames and all later content remain instance decisions.
- Bootstrap output synchronizes as ordinary visible Markdown and requires no
  device-local reconstruction.
- Dynamic dashboards remain an optional later customization; the portable
  bootstrap does not depend on Dataview or another community plugin.
