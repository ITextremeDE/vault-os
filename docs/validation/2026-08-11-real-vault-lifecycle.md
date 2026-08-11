# Real-vault lifecycle validation

- Date: 2026-08-11
- Verdict: Passed
- Packages: `0.1.0-dev.1` to `0.1.0-dev.2`

## Acceptance target

Verify that Vault-OS can be installed and updated inside an established
Obsidian vault without changing pre-existing content, instance-owned
configuration, or `.obsidian` state. Verify that a locally changed managed file
stops an update before any partial release change is applied.

## Scope and method

- A complete temporary copy of the existing source vault was used; only its
  `.git` directory was excluded.
- The source vault was never used as an installation target.
- The copy contained 1,261 pre-existing file and symbolic-link entries.
- All optional modules were selected.
- Managed files were installed under the previously absent `98 Vault-OS`
  system root so the legacy `99 System` tree remained instance-owned.
- Instance field roles, localized values, validation exclusions, and area
  register values were configured in `.vault-os` inside the temporary copy.
- Every pre-existing entry was compared with its source counterpart after the
  lifecycle operations using file hashes or symbolic-link targets.

## Results

| Check | Result |
| --- | --- |
| Initial installation | 103 managed files and 11 instance seeds installed |
| Initial health | `doctor` healthy; `diff` empty |
| Pre-existing entries | 1,261 unchanged; none missing |
| Write boundary | No new files outside `.vault-os` and `98 Vault-OS` |
| Release update | One managed file updated; 102 unchanged |
| Instance ownership | Ten existing instance files preserved |
| Updated health | `doctor` healthy; 103 managed files consistent |
| Portable validator | Zero errors and zero warnings with the instance profile |
| Managed-file conflict | `diff` and `update` returned exit code `2` |
| Conflict atomicity | No release, lock, or instance file was partially changed |

The first validator run exposed that localized stored values could not be
resolved to stable model identifiers. `0.1.0-dev.2` adds instance-owned value
mappings for kind, type, and status. Repeating the update and validator checks
then passed without rewriting existing vault content.

## Boundary

This validates side-by-side adoption and the lifecycle safety contract. It does
not migrate or replace the source vault's legacy `99 System` tree and does not
install Vault-OS into the live vault. That deliberate production migration is a
separate operational decision, not part of the `0.1.0` lifecycle acceptance.
