---
name: create-from-template
description: Create a new content note from an installed template with validated metadata, path, and filename.
---

# Create from template

Use when a matching installed template exists and a genuinely new note is needed.

1. Determine content kind and type before choosing a template.
2. Resolve target root, filename, schema, and registers from installed module and
   instance configuration.
3. Prefer an existing canonical note when it is the natural destination.
4. Copy the template structure, then build content metadata for the target note;
   never copy release-document metadata as target metadata.
5. Resolve path and naming placeholders from instance configuration, then replace
   or remove every remaining placeholder and validate the final note.
6. Record the new content in the configured change log.

Report the template, destination, filename, key metadata, and unresolved choices.
