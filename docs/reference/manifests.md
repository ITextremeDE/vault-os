# Manifest reference

Vault-OS release contents and ownership are declared under `manifests/`.
`repository.json` is the entry point and references the four manifest domains.

## Common fields

| Field | Meaning |
| --- | --- |
| `schemaVersion` | Manifest contract version; currently `1` |
| `id` | Stable component identifier |
| `kind` | `core`, `module-catalog`, `module`, `instance`, or `runtime` |
| `owner` | `managed`, `instance`, or `runtime` |
| `targetRoot` | Logical destination root: `system` or `vault` |

All paths use repository-relative or target-root-relative POSIX syntax. Absolute
paths, parent traversal, and duplicate source or target paths are invalid.

## Managed files

Each managed entry in `core.json` or a module manifest contains:

- `origins`: one or more classified source paths from the extraction baseline;
- `source`: file in the release repository;
- `target`: destination relative to the configured system root;
- `sha256`: lowercase SHA-256 digest of the source file.

An entry may additionally declare `materialize: instance`. The lifecycle then
resolves reserved `fields`, `moduleFields`, `values`, and `paths` tokens from the
visible instance configuration before installing the managed artifact. Ordinary
Obsidian placeholders such as `{{title}}` and `{{date:YYYY-MM-DD}}` remain intact.
Materialization is valid only for managed entries.

A managed entry may declare `localizedSources`, keyed by language tag. Every
localized source has its own repository-relative `source` and `sha256`. The
ordinary `source` is the canonical English fallback and must not be repeated as
an `en` localization. The lifecycle selects the exact configured
`vault.language`, then its primary language subtag (`de-DE` → `de`), and finally
the canonical English source. Localized sources share the same target,
ownership, materialization rules, and conflict protection.

Managed files use `installMode: managed`. The updater replaces or removes an
installed managed file only when it still matches the installed checksum
recorded in the local release lock. For an ordinary managed file this equals the
source checksum; for a materialized file it is the checksum of the rendered
artifact. Any mismatch stops the complete update before files are changed.

`modules.json` lists optional module manifests. Every module owns a disjoint
source tree and installation targets that do not collide with core or another
module.

## Instance seeds

Instance seeds have a release source and checksum but use
`installMode: create-only`. Installation creates a missing target. Updates never
replace an existing target, regardless of whether it still resembles the seed.

Instance targets must be visible paths so ordinary vault synchronization can
carry them between devices. A dot-prefixed first path component is invalid.
The initial configuration seed becomes `Vault-OS/config.yaml` and defines the
vault name, language, system root, and selected modules.

The instance-owned field profile under `Vault-OS/schema/fields.yaml` maps
semantic field roles. Its optional `values.kind`, `values.type`, and
`values.status` objects map stored localized values to the stable identifiers
declared by managed models. When more than one stored value maps to the same
stable identifier, `preferredValues` selects the intended reverse mapping for a
materialization token such as `type.contact.person`. `moduleFields` maps stable
module-field identifiers to locally stored field names. `filenamePatterns` may override a managed
kind's filename rule for an established instance convention. Empty maps use
the managed identifiers and patterns directly. Module models may additionally
declare typed fields, instance registers, and type-specific requirements. The
register rule `allowScalar` permits a multi-value register to retain the common
single-value scalar form while still accepting YAML lists. Optional register
`description` and per-value `descriptions` preserve the meaning and boundary of
local controlled values. The external-reference policy requires matching URL
and ID/UID fields and rejects credentials or secret query parameters in URLs by
default. Explicit `pairs` support established field names that do not share the
configured suffix-derived base.

`agent-init` separately generates device-local integration state at
`.vault-os/integrations/agents.yaml`. It records selected providers, QMD
activation, and checksums of generated provider artifacts. It is not an
instance seed and is not synchronized as canonical instance configuration.

The instance-owned `Vault-OS/integrations/search.yaml` may describe externally
managed search indexes without transferring their device-local runtime. Every
index record declares `id`, `engine`, `management`, `collection`,
`capabilities`, `deviceLocal`, `providerBindings`, and `refreshPolicy`.
`management: external` records an integration choice only; Vault-OS does not
create, configure, refresh, or diagnose that external index. Absolute paths,
caches, models, credentials, and client-specific commands do not belong in the
synchronized contract.

## Bootstrap artifacts

`bootstrap` renders profile, README, dashboard, and optional PARA overview notes
from the installed configuration and field profile. These files are ordinary
user content and intentionally have no manifest entries or release checksums.
The command creates a missing target once, preserves every existing regular
file, and never lets `update` adopt the result.

Bootstrap filenames are instance configuration. The root filenames must be
unique, use the `.md` suffix, and cannot reuse provider instruction names such
as `AGENTS.md` or `CLAUDE.md`.

## Runtime artifacts

Runtime entries declare a target and generator but no release source or
checksum. The runtime manifest declares exactly one generated artifact at the
fixed target `.vault-os/lock.json`; another target is invalid. Runtime state
remains local to the device. Provider wrappers, client configuration, and QMD
indexes are also device-local even though they are not release-manifest entries.

## Release metadata and lock

`repository.json` declares the package version using Semantic Versioning. Every
successful installation creates `.vault-os/lock.json` with:

- the lock schema and product identifier;
- package version and manifest fingerprint;
- installation and last-update timestamps;
- the configured system root and selected modules;
- the target, owner, and installed checksum of every managed file.

The lock records only release-managed state. It does not claim ownership of
instance files. The lock is generated locally and written last in the same
transaction as managed file changes. On a secondary synchronized device,
`device-sync` recreates the lock only after verifying the complete delivered
file set against the selected package and current synchronized instance profile.

The lifecycle behavior and exit codes are defined in the
[CLI reference](cli.md).

## Validation

Run:

```bash
.venv/bin/python scripts/validate_manifests.py
```

The validator checks manifest structure, ownership rules, path safety, source
existence, checksums, duplicates, references, exact source-tree coverage, and
lineage from the portability matrix. Every core, module, instance, and split
source must have artifacts in exactly the ownership domains assigned by the
matrix. Runtime-only source history must not leak into release artifacts.
