# ADR 0002: Project governance and publication

- Status: Accepted
- Date: 2026-08-11

## Context

Vault-OS is intended to be freely available as an open-source ITextreme project.
It is not an open-core or paid product. The project needs one public contribution
surface and one independent internal mirror.

## Decision

- Vault-OS is licensed under the Mozilla Public License 2.0.
- `ITextremeDE/vault-os` on GitHub is the canonical public repository.
- `itextreme/vault-os` on Forgejo is the private operational mirror.
- Repository development remains private until the `0.1.0` acceptance criteria pass.
- Technical project documentation is written in English.
- German articles and videos may accompany releases through ITextreme.

## Consequences

- Distributed modifications to covered Vault-OS files remain available under the MPL.
- Separate vault content and instance-owned files are not subject to the MPL merely
  because they coexist with Vault-OS.
- Issues and pull requests belong on GitHub after publication.
- Forgejo provides an independent mirror but is not a second contribution surface.
