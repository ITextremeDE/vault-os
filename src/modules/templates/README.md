<!-- SPDX-License-Identifier: MPL-2.0 -->

# Template module

Templates are centrally managed structural starting points. They apply installed
schema, register, and workflow rules without redefining them. Add a template only
for a recurring content shape, keep placeholders explicit, and maintain one
canonical template per purpose.

Portable sources use reserved instance-materialization tokens for semantic
fields, values, module fields, and configured paths. Install and update resolve
those tokens before the managed templates reach Obsidian. Native placeholders
such as `{{title}}` and date expressions remain for Obsidian itself.

The canonical template source is English. A managed entry may provide complete
localized sources for other languages. Vault-OS selects the exact configured
language, then its primary language subtag, and finally English as the fallback.
Localization changes presentation and guidance, never semantic identifiers,
field mappings, paths, or ownership.

Templates are intentionally useful structures rather than empty skeletons. They
may include prompts, Dataview queries, and recurring context sections, but must
remain independent of a specific vault, person, organization, or external
service.
