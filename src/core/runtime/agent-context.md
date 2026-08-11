<!-- SPDX-License-Identifier: MPL-2.0 -->

# Agent context

This document is the portable operational minimum for agent work in a vault.

## Short rules

- Read applicable host instructions and canonical vault rules first.
- Preserve existing structure and instance-owned content.
- Prefer extending the natural existing file over creating a parallel one.
- Use only values declared by installed schemas and instance registers.
- Use stable, unambiguous internal links.
- Keep changes small, reversible, and traceable.
- Do not delete content or perform external writes without authorization.
- Do not invent parallel standards, templates, or value lists.

## Default check

1. What outcome was requested?
2. Does a natural target already exist?
3. Which installed module owns the content?
4. Which kind, type, status, and register values are valid?
5. Which workflow applies?
6. What is the smallest sufficient change?

The instance runtime profile supplies the configured system root, capture
location, enabled modules, and read order. This managed file never embeds those
local choices.
