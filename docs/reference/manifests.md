# Manifest reference

Vault-OS release contents and ownership are declared under `manifests/`.
`repository.json` is the entry point and references the four manifest domains.

## Common fields

| Field | Meaning |
| --- | --- |
| `schemaVersion` | Manifest contract version; currently `1` |
| `id` | Stable component identifier |
| `kind` | `core`, `module-catalog`, `instance`, or `runtime` |
| `owner` | `managed`, `instance`, or `runtime` |
| `targetRoot` | Logical destination root: `system` or `vault` |

All paths use repository-relative or target-root-relative POSIX syntax. Absolute
paths, parent traversal, and duplicate source or target paths are invalid.

## Managed files

Each entry in `core.json` contains:

- `origin`: classified source path from the extraction baseline;
- `source`: file in the release repository;
- `target`: destination relative to the configured system root;
- `sha256`: lowercase SHA-256 digest of the source file.

Managed files use `installMode: managed`. A future updater may replace an
installed file only when it still matches the checksum recorded in the local
release lock.

## Instance seeds

Instance seeds have a release source and checksum but use
`installMode: create-only`. Installation creates a missing target. Updates never
replace an existing target, regardless of whether it still resembles the seed.

The initial configuration seed becomes `.vault-os/config.yaml` and defines the
vault name, language, system root, and selected modules.

## Runtime artifacts

Runtime entries declare a target and generator but no release source or
checksum. They use `installMode: generated` and remain local to the installed
vault.

## Validation

Run:

```bash
python3 scripts/validate_manifests.py
```

The validator checks manifest structure, ownership rules, path safety, source
existence, checksums, duplicates, references, exact coverage of `src/core`, and
exact lineage from all `core` decisions in the portability matrix.
