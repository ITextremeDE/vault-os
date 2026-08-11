# Configure Obsidian for Vault-OS

Vault-OS needs no Obsidian plugin for its portable core. The settings and
plugins below are a recommended operating profile, not an installation
requirement. Apply them manually in Obsidian after installing Vault-OS.

Vault-OS never creates, changes, or synchronizes `.obsidian`. That directory
belongs to the vault owner and Obsidian, including when Obsidian Sync or another
approved synchronization method manages it.

## Recommendation levels

- **Required** means an installed module needs the feature for a named asset to
  work as documented.
- **Recommended** means the setting or core plugin supports safe everyday use.
- **Optional** means it is useful only for a specific workflow.
- **Not a default** means enable it only after accepting the stated ownership,
  portability, or security trade-off.

## Configure the editor

The exact labels can vary slightly by Obsidian version and operating system.

### Files and links

Use these settings as the portable baseline:

| Setting | Recommendation | Reason |
| --- | --- | --- |
| New link format | `Absolute path in vault` | Keeps targets unambiguous when filenames repeat. |
| Automatically update internal links | On | Preserves links when notes are renamed in Obsidian. |
| Use Wikilinks | On | Matches the Vault-OS link standard. |
| Default location for new notes | Configured instance inbox, normally `00 Inbox` | Gives uncategorized notes one predictable entry point. |
| Confirm file deletion | On | Prevents an accidental command from silently removing content. |
| Deleted files | System trash or Obsidian trash | Keeps normal deletion recoverable; do not use permanent deletion as the default. |

Choose the attachment folder deliberately for the vault. Vault-OS does not
declare a universal attachment path because an existing vault may already have
a stable convention.

Do not exclude the configured system root from search merely because Vault-OS
manages it. Its rules and workflows should remain inspectable. Managed files
must still be changed only through Vault-OS lifecycle commands.

### Properties and pasted content

- Set **Properties in document** to **Source** when exact YAML representation
  matters. Vault-OS schemas distinguish missing fields, empty values, lists,
  and ISO dates.
- Keep **Convert pasted HTML to Markdown** enabled unless a particular workflow
  intentionally needs raw HTML.
- Choose source or live preview as the default editing mode according to user
  preference; Vault-OS does not depend on either mode.

### Updates and recovery

- Enable **Automatic updates** and keep Obsidian on current stable releases.
  Avoid early-access builds for an important production vault unless the vault
  is backed up and used to test the next release deliberately.
- Keep **File recovery** enabled, but do not treat it as a backup. Recovery
  snapshots are device-local and use configurable retention.
- Back up the vault independently before Vault-OS lifecycle changes, plugin
  installations, or bulk edits.

## Enable core plugins

These official core plugins form the recommended baseline:

- File explorer;
- Search;
- Quick switcher;
- Command palette;
- Properties view;
- Backlinks;
- Outgoing links; and
- File recovery.

They improve navigation, inspection, and recovery without adding a third-party
dependency to Vault-OS.

Some optional Vault-OS modules benefit from additional core plugins:

| Vault-OS module | Core plugin | Level | Configuration |
| --- | --- | --- | --- |
| `review` | Bases | Required for the installed `.base` view | Enable Bases; the view itself is supplied by the module. |
| `journal` | Daily notes | Optional | Point it to the installed instance's journal location and filename policy. Its template may point to `<system-root>/04 Assets/Templates/Journal/Daily Note.md`. Do not invent a second journal structure. |
| `navigation` | Daily notes | Required for its `obsidian://daily` action | Enable it when the navigation skill should open or create today's journal note. |
| `templates` | Templates | Optional | Point the template folder to `<system-root>/04 Assets/Templates` when templates should be inserted manually. Treat those template files as managed. |

The journal and template workflows remain usable through installed Vault-OS
workflows, prompts, and agent skills. Their corresponding Obsidian core plugins
are not hard dependencies for the modules as a whole.

## Evaluate community plugins

No community plugin is part of the Vault-OS baseline. Community plugins run
third-party code inside Obsidian and must be evaluated like any other software
dependency: inspect the source and maintenance state, install one change at a
time, back up first, and review updates before applying them.

Leave **Restricted mode** enabled when no community plugin is needed. Turning
it off is a vault-owner decision, not a Vault-OS installation step.

| Plugin | Position | Use it when | Boundary |
| --- | --- | --- | --- |
| [Dataview](https://github.com/blacksmithgu/obsidian-dataview) | Optional | Existing notes or advanced dashboards already use Dataview queries. | Prefer the official Bases core plugin for new portable views when it is sufficient. Review DataviewJS as executable code rather than passive note content. |
| [Obsidian Git](https://github.com/Vinzent03/obsidian-git) | Optional for advanced users | Git is the deliberate version-control workflow for the vault. | Start with automatic pull and push disabled. Do not let multiple sync tools race over the same files; Git history is not the only backup. |
| [Tasks](https://github.com/obsidian-tasks-group/obsidian-tasks) | Optional | Tasks are intentionally managed inside this vault. | Do not create a competing task system when an external task manager is canonical. |
| [Templater](https://github.com/SilentVoid13/Templater) | Not a default | Core Templates and Vault-OS skills cannot express a required automation. | Templates may execute JavaScript or system commands. Keep them reviewed, scoped, and portable. |
| [Linter](https://github.com/platers/obsidian-linter) | Not a default | The vault owner has an explicit formatting policy for content. | Exclude managed and generated artifacts or formatting will create checksum conflicts. |

When using Linter or any similar bulk formatter, exclude at least:

- the configured Vault-OS system root;
- `.vault-os`, `.agents`, `.claude`, and `.qmd`;
- generated root files such as `AGENTS.md` and `CLAUDE.md`; and
- any other path owned by an installer, indexer, or provider adapter.

QuickAdd, Meta Bind, Omnisearch, and similar plugins may be useful for a
specific vault, but Vault-OS should not recommend or depend on them without a
concrete module or workflow that needs them.

## Apply the profile safely

1. Back up the vault and its Obsidian configuration.
2. Open **Settings** and apply the file, link, property, deletion, and recovery
   recommendations.
3. Enable the recommended core plugins.
4. Enable Bases when the `review` module is installed and its view will be
   used.
5. Configure Daily notes or Templates only when their corresponding module
   workflow needs Obsidian commands.
6. Add community plugins one at a time and verify the vault after each change.
7. Run the Vault-OS `doctor` lifecycle command after bulk tools have touched
   vault files. A managed checksum warning is a protection signal, not
   something to suppress.

## Further reading

- [Obsidian settings](https://help.obsidian.md/settings)
- [Core plugins](https://help.obsidian.md/plugins)
- [Bases](https://help.obsidian.md/bases)
- [Properties](https://help.obsidian.md/properties)
- [Daily notes](https://help.obsidian.md/plugins/daily-notes)
- [Templates](https://help.obsidian.md/plugins/templates)
- [File recovery](https://help.obsidian.md/plugins/file-recovery)
- [Community plugins](https://help.obsidian.md/community-plugins)
