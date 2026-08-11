---
name: vault-search
description: Search an installed Vault-OS vault for relevant notes and retrieve original files before using results as evidence.
---

# Vault search

Use for vault-wide orientation, prior knowledge, related notes, or locating the
natural file to update.

1. Read `Vault-OS/integrations/search.yaml` and respect its source precedence.
2. Prefer the configured QMD MCP tools when available. Otherwise use the QMD
   CLI, and fall back to ordinary filesystem search when QMD is unavailable.
3. Scope searches to the local vault collection. Start with keyword search and
   use hybrid or semantic search only when terminology is uncertain.
4. Treat every hit as a candidate. Retrieve and read the original Markdown
   file before quoting it, relying on it, linking it, or changing it.
5. Prefer a current canonical note over journals, conversations, sessions, or
   generated indexes. State material coverage limits when claiming completeness.

Useful QMD CLI patterns:

```bash
qmd search "exact terms" -c vault --json -n 10
qmd query "natural-language question" -c vault --json -n 10
qmd get "qmd://vault/path/to/note.md"
qmd status
```

Never treat an index, cache, search snippet, or agent session as more
authoritative than the retrieved vault file.
