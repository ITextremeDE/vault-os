# Production vault migration validation

- Date: 2026-08-11
- Verdict: Passed
- Package: `0.1.0-dev.10`

## Acceptance target

Migrate an established content vault into a freshly installed Vault-OS
instance without copying the legacy managed-system tree, Obsidian settings,
trash, or device-local runtime from the source. Preserve user content, the
historical content-change log, and Git history while adapting only references
and entry-point filenames required by the new ownership model.

## Method

1. Install all 14 modules and bootstrap the configured entry points in a new
   target vault.
2. Build the complete migration in a temporary copy first.
3. Copy the six configured content roots and the user-owned profile, dashboard,
   README, Git attributes, and Git ignore policy.
4. Map the nine structural `_README.md` entry points to the installed
   `README.md` convention and update affected live links.
5. Move the instance-owned historical content-change log into the visible
   synchronized runtime profile.
6. Configure localized base and module fields, local register values, legacy
   filename patterns, Git policy, search sources, journal policy, and
   automation contracts.
7. Validate the temporary result before transferring it without deletions to
   the production target.

## Results

| Check | Result |
| --- | --- |
| Source user files | 1,061 present; none missing |
| Byte-identical user files | 1,045 |
| Deliberately adapted user files | 16 entry points or managed-link references |
| Historical content-change log | Byte-identical |
| Profile and dashboard | Byte-identical |
| Git history | Original HEAD and remote preserved |
| Legacy managed-system tree | Not copied |
| Managed Vault-OS state | 104 files current; no pending lifecycle changes |
| Portable content validator | Zero errors and zero warnings |
| Vault-OS health | Healthy, including initialized AI integration |
| `.obsidian` and trash | Not copied or modified |

The original source vault remained unchanged and available as the recovery
copy. The production migration remains uncommitted so its complete Git diff can
be reviewed before publication.

## Runtime limitations

QMD and Claude Code were unavailable on the migration device and were not
initialized or exercised. The existing Codex integration passed structural
health checks; this migration did not repeat the earlier executed-client smoke
test.
