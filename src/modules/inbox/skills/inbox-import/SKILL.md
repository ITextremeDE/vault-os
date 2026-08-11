---
name: inbox-import
description: Inspect Markdown or PDF imports and route them without rewriting sources or bypassing authorization.
---

# Inbox import

Use for files in the configured import inbox when their semantic destination must
be determined. Keep originals until a separate authorized decision removes them.

1. List and read the selected Markdown or reliably extracted PDF.
2. Determine whether it is worth importing and search for a natural target note.
3. Classify it using installed kinds, types, statuses, areas, and templates.
4. If an existing note is a plausible target, ask before changing or merging it.
5. For a new note, preserve source wording; use the template only for metadata and
   stable structural blocks. Normalize only technical extraction damage.
6. Move recognizable imported metadata into allowed fields without duplicating it
   in the body.
7. Compare the source with related notes for confirmation, extension,
   contradiction, or obsolescence. Keep source capture and derived edits separate.
8. Record authorized content changes and leave uncertain cases in the inbox.

Never invent schema values, rewrite the source as a default, or infer a target
from file format alone.
