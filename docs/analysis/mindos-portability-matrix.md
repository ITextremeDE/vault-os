# MindOS Portability Analysis

This analysis classifies the complete tracked `99 System` tree of MindOS for
extraction into Vault-OS. The detailed, canonical classification is the
[portability matrix](../../analysis/mindos-portability-matrix.tsv).

## Source baseline

- Source repository: local MindOS vault
- Source tree: `99 System/**`
- Source revision: `3f6a243321bfa6bb8ace48281042bca31a57b92a`
- Analysis date: 2026-08-11
- Coverage: 119 of 119 tracked source files

The live validator compares the matrix paths with the tracked source paths.
Untracked vault content and files outside `99 System` are intentionally outside
this analysis.

## Result

| Decision | Files | Meaning |
| --- | ---: | --- |
| `core` | 15 | Mandatory, portable operating-system contract |
| `module` | 88 | Optional managed feature or agent tooling |
| `split` | 13 | One source file currently mixes ownership domains |
| `instance` | 2 | User-owned defaults that may only be seeded |
| `runtime` | 1 | Generated local state that must not be distributed |

| Action | Files | Meaning |
| --- | ---: | --- |
| `neutralize` | 67 | Remove source-vault identity, paths, examples, or assumptions |
| `extract` | 36 | Move reusable content with no structural ownership split |
| `split` | 13 | Separate managed logic from module or instance data |
| `seed` | 2 | Create editable initial instance data, never update it in place |
| `exclude` | 1 | Keep local and outside release artifacts |

Estimated extraction effort is 30 small, 76 medium, and 13 large items. These
are relative migration sizes, not delivery estimates.

## Architectural conclusion

MindOS already contains a usable Vault-OS design, but not a cleanly extractable
distribution. Most files are optional content-model, workflow, template, or
agent modules. The mandatory core is deliberately small.

The extraction must preserve four boundaries:

1. `src/core` owns only portable contracts, lifecycle rules, and engines.
2. `src/modules` owns optional schemas, workflows, templates, views, and agent
   tooling.
3. `instance-template` contains neutral seed configuration that becomes owned
   by the installed vault.
4. Runtime history and other generated local state never enter a release.

Neutralization is not a search-and-replace exercise. A file can stop saying
"MindOS" while still embedding its folder layout, organizations, external
systems, enabled modules, or personal defaults. Those dependencies must become
explicit configuration or module contracts.

## Files requiring structural separation

The 13 `split` decisions carry the main architectural risk:

- Five schema files mix universal mechanics with module-specific fields,
  content kinds, states, or naming rules.
- The area register mixes a portable register contract with entirely local
  values.
- The commit-message skill and its documentation mix reusable Git safeguards
  with local categories and policies.
- The Codex search skill mixes reusable retrieval behavior with local qmd
  collections and paths.
- The daily journal template mixes a reusable daily structure with personal,
  organizational, and system-specific sections.
- The validator mixes a reusable validation engine with the MindOS model and
  exclusions.
- The automation overview mixes a portable automation contract with concrete
  JSNexus, Codex, and n8n operations.
- The agent short context mixes general runtime rules with selected modules,
  paths, and instance read order.

The local content change log is the sole `runtime` file and must be excluded
from Vault-OS releases.

## Implementation status

The 15 pure core sources and all target-domain portions of the 13 mixed sources
have been extracted. Manifest validation now proves their lineage and domain
coverage. The remaining extraction scope consists of the files classified as
pure modules or instance data.

## Extraction order

1. Define manifests for core, modules, instance seeds, and generated runtime
   files.
2. Extract the 15 core files and make their contracts vault-name independent.
3. Split the 13 mixed files before copying their resulting components.
4. Extract optional modules in dependency order: schemas, PARA and knowledge,
   journal and contacts, then agent and audit tooling.
5. Add neutral instance seeds without update ownership.
6. Implement install, update, diff, and doctor behavior against the manifests.
7. Validate a clean installation and an update of MindOS without modifying
   instance-owned or locally changed files.

## Validation

Run the structural check by itself:

```bash
python3 scripts/validate_portability_matrix.py
```

When the MindOS source checkout is available, also verify exact live coverage:

```bash
python3 scripts/validate_portability_matrix.py \
  --source /path/to/MindOS
```

The source checkout is read only; the validator changes neither repository.
