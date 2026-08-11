---
name: obsidian-navigation
description: Open an existing note in the configured Obsidian vault without changing content.
---

# Obsidian navigation

Use only to locate and open existing notes. Resolve the vault name and logical
content roots from instance configuration; never hard-code them.

For today's daily note, use `obsidian://daily?vault=<encoded-vault-name>` and let
Obsidian resolve the date. For a concrete note, find an exact vault-relative path
and use `obsidian://open?vault=<encoded-vault-name>&file=<encoded-path>`. Prefer
exact matches in the relevant configured content root. If several candidates are
plausible, present them and ask instead of guessing. Do not create, edit, move, or
delete files.
