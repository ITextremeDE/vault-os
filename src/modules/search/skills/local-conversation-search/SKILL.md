---
name: local-conversation-search
description: Find and summarize earlier local agent conversations using configured sources without treating them as canonical knowledge.
---

# Local conversation search

## Purpose

Find earlier agent conversations, decisions, plans, or wording before
reconstructing them from memory. Use only sources declared in the instance
search integration.

## Workflow

1. Extract strong search terms, likely dates, project context, and the requested
   result type.
2. Search configured indexes before raw session stores.
3. Narrow by date and repository context when available.
4. Read only the most likely results and relevant message context.
5. Record source identifier, title, date, and evidence strength.
6. Distinguish sourced facts from inference.

Do not dump complete conversations. If no result is found, report the terms and
source classes checked and suggest better terms or a narrower period.

## Output

For each relevant result, provide date, title, source, relevance, a short
summary, and any uncertainty. Sort by relevance and then recency.

Conversation history is not canonical knowledge. When a result has durable
value, propose the appropriate installed capture or knowledge workflow. Create
or modify vault content only with explicit authorization.
