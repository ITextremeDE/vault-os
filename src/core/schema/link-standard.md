<!-- SPDX-License-Identifier: MPL-2.0 -->

# Link standard

Internal links should remain stable, readable, and unambiguous.

## Wiki links

Use Obsidian Wiki links for internal relationships. Include the full vault-
relative path when a filename could be ambiguous or when a system file is
referenced.

Use a short meaningful alias rather than displaying a long path:

```text
[[Projects/Example Project|Example Project]]
```

## When to link

Create a link when another file is a relevant source, target, or contextual
relationship. Do not link every occurrence of a term merely to increase link
density.

When a module defines a structured relationship field, store the relationship
there. Body links may add context but do not replace structured data.

## Stability rules

- Respect an existing canonical target and spelling.
- Prefer one consistent alias for repeated references.
- Do not create shadow files solely to shorten links.
- When renaming a file, verify inbound links and weigh the migration cost.
- Content does not link to a system rule merely because it follows that rule.
