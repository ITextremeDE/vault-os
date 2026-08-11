<!-- SPDX-License-Identifier: MPL-2.0 -->

# 05 Automation and validation

Vault-OS validation is deterministic and read only by default. Validators may
inspect managed files, instance configuration, links, schemas, and register
values, but they do not repair content unless a separate explicit operation is
authorized.

## Contract

- Exit code `0` means that no blocking finding was detected.
- Exit code `1` means that reproducible findings exist.
- Exit code `2` means that validation could not run reliably.
- Reports identify locations and rules without exposing credentials or private
  content unnecessarily.
- Allowed values come from canonical schemas and instance registers, never
  from hidden duplicate lists in validator code.

`validate_vault.py` is the portable engine. It reads the instance validation
profile, selected module models, and instance registers instead of embedding a
vault-specific content model. Module models can declare string, date, register,
and Wiki-link-list fields, type-specific requirements, and filename patterns.
The instance field profile also defines the pairing and secret-handling policy
for external reference URLs. Runtime dependencies are declared by the
repository requirements.

From an installed vault root:

```bash
python3 "<system-root>/05 Automation/Validators/validate_vault.py" .
```

Use `--json` for machine-readable output. Repository-level validators verify
manifest integrity, portability boundaries, and extraction coverage.
