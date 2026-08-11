# Contributing to Vault-OS

Vault-OS is developed in the open. Contributions should keep the operating
layer portable, local-first, and independent from any specific vault owner.

## Before contributing

- Open or reference an issue for changes that affect architecture or public behavior.
- Keep portable system files separate from example or instance-specific data.
- Do not include personal information, credentials, absolute local paths, or
  content copied from a private vault.
- Keep changes small and include validation appropriate to their impact.

## Validate a change

```bash
python3 -m unittest discover -s tests
python3 scripts/check_portability.py
git diff --check
```

By submitting a contribution, you agree to license it under the Mozilla Public
License 2.0.
