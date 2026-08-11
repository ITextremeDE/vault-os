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
