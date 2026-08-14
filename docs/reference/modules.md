# Module catalog

The portable core is always installed. Every module is optional and disabled by
default. Select modules with repeated `--module ID` options, use
`--all-modules`, or edit the installed `modules` array before `diff` and
`update`.

No hard dependencies between modules are currently enforced. Some combinations
are more useful together, especially for agent-assisted work.

| ID | Purpose | Main installed assets |
| --- | --- | --- |
| `agents` | Conventions for reusable agent prompts and skills | Prompt and skill contracts |
| `audit` | Detect and correct operating-system and content drift | Audit routing, OS/content/vault audit and correction skills |
| `contacts` | Structured people, organizations, representatives, and role relations | Schema, workflow, prompts, templates, reusable role and contact-detail Bases views, instance registers |
| `git` | Safe commits governed by instance policy | Commit-planning skill |
| `governance` | Normalize notes and record relevant content changes | Closing block, normalization prompt, change-log workflow |
| `inbox` | Capture and route unclassified material | Inbox workflow and import skill |
| `journal` | Daily, weekly, and yearly reflection | Schema, workflow, prompts, templates, configured period directories and READMEs |
| `knowledge` | Process conversations into working notes, insights, and durable knowledge | Schema, workflows, prompts, templates, processing skills |
| `navigation` | Open existing notes through Obsidian without changing them | Obsidian navigation skill |
| `para` | Organize projects, areas, resources, and archives | Schema, filing/archiving workflows, templates, reusable dashboard Bases views, configured roots and READMEs |
| `publishing` | Prepare creator content | Article, video, and website templates |
| `review` | Review content state | Review workflow and Obsidian Bases view |
| `search` | Search vault notes and configured local conversation sources | Vault and conversation search skills |
| `templates` | Create validated notes from installed templates | Template contract and creation skill |

The `contacts`, `knowledge`, and `para` templates and the `contacts`, `para`, and `review`
modules' `.base` files need an Obsidian version with Bases support to render
their dynamic views. PARA task views remain Dataview queries because Bases does
not expose individual Markdown tasks. Templates and the Bases views are materialized from
the instance field, value, module-field, and path mappings during install and
update. The 22 content templates ship as complete English and German variants;
`vault.language` selects the presentation language while semantic mappings stay
instance-owned. Unsupported template languages fall back to English. Vault-OS
does not install or configure Obsidian plugins.
The [recommended Obsidian profile](../how-to/obsidian-setup.md) maps the
relevant modules to core plugins and explains the optional community-plugin
boundaries.

## Suggested profiles

These profiles are recommendations, not hidden defaults.

### Minimal portable core

Install no optional modules. This provides ownership, schema, lifecycle,
validation, and runtime conventions without a productivity method.

### Personal knowledge vault

```text
para, inbox, journal, knowledge, templates, review
```

This combines PARA organization, capture, reflection, knowledge processing,
template creation, and review.

### AI-assisted knowledge vault

```text
agents, search, knowledge, audit, navigation, templates
```

Add `para`, `inbox`, `journal`, or `contacts` according to the vault's actual
content. Skills become provider-discoverable only after `agent-init`.

### Creator vault

```text
para, knowledge, publishing, templates, review
```

Add `git` only when the vault is version-controlled and its instance commit
policy has been reviewed.

## Inspect exact contents

The catalog is declared in `manifests/modules.json`; each entry references a
module manifest under `manifests/modules`. Those manifests are the canonical
source for exact installed paths and checksums.
