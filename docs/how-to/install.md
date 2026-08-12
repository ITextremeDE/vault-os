# Install Vault-OS

This guide installs Vault-OS from a release checkout into a new or existing
Obsidian vault. Vault-OS writes ordinary files into the target directory and
does not modify `.obsidian`.

## Requirements

- Python 3.10 or newer;
- Git when obtaining or updating a source checkout;
- Obsidian when the target directory is to be used as an Obsidian vault; and
- a current backup or version-control checkpoint before changing an existing
  vault.

Codex, Claude Code, and QMD are optional and are covered by the
[AI setup guide](ai-setup.md).

## Obtain Vault-OS

Vault-OS has not yet published `0.1.0`. Until then, a checkout of `main` is a
development build rather than a stable release.

Clone the public repository:

```bash
git clone https://github.com/ITextremeDE/vault-os.git
cd vault-os
```

For a released version, check out its tag before installation rather than using
an arbitrary development commit.

## Prepare Python

From the Vault-OS checkout:

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m vault_os --help
```

Runtime dependencies are declared in `requirements.txt`. Keep the virtual
environment in the Vault-OS checkout, not in the target vault.

## Let an AI agent install Vault-OS

You do not have to execute the installation manually. A local coding agent or
LLM client such as Codex or Claude Code can inspect this repository, prepare the
Python environment, run the lifecycle commands, and validate the result when it
has explicitly authorized filesystem and terminal access.

Give the agent the exact target vault, desired modules, whether the vault is new
or existing, and the actions it may perform. For example:

```text
Install Vault-OS from this checkout into "/path/to/My Vault".

- Follow docs/how-to/install.md and the repository AGENTS.md.
- Use the modules para, inbox, journal, knowledge, and templates.
- Treat this as an existing vault: inspect it first and confirm that a current
  backup or clean version-control checkpoint exists before writing.
- Do not modify .obsidian or unrelated vault content.
- Use the repository virtual environment and Vault-OS lifecycle commands; do
  not copy managed files manually.
- Run vault_os doctor after installation and report every warning or skipped
  check.
- Do not commit, push, publish, or delete anything unless I authorize it.
```

For a new empty vault, replace the backup instruction accordingly. The user
still decides the target, modules, backup strategy, and permissions. Review the
agent's final command output before opening or migrating important content.

A browser-only ChatGPT, claude.ai, or other hosted chat without local tools can
write commands and answer questions, but it cannot perform the installation on
the user's computer.

## Install a new vault

The target directory may already exist or may be created by the installer:

```bash
.venv/bin/python -m vault_os install "/path/to/My Vault" \
  --module para \
  --module inbox \
  --module journal \
  --module knowledge \
  --module templates

.venv/bin/python -m vault_os doctor "/path/to/My Vault"
```

The directory name becomes the vault name unless `--name` is supplied. Open
the directory as a vault in Obsidian after installation. Obsidian creates and
owns its own `.obsidian` configuration.

Installation creates the directory configured as `paths.inbox`, such as
`00 Inbox` or `00 Eingang`. With `para`, it also creates the configured
projects, areas, resources, and archive roots. With `journal`, it creates the
journal root plus the configured daily, weekly, and yearly directories. All of
these directories are user-owned: Vault-OS does not add them to the release
lock or manage files later placed inside them.

The example installs a practical personal-knowledge profile. See the
[module catalog](../reference/modules.md) before choosing modules. With no
module option, Vault-OS installs only its portable core. `--all-modules`
installs the complete catalog.

## Create the user-owned start files

After a successful installation, optionally bootstrap the vault's entry points:

```bash
.venv/bin/python -m vault_os bootstrap "/path/to/My Vault"
```

The command creates missing files only:

- `Profile.md` as stable personal or team context;
- root `README.md` as the vault entry point;
- root `Dashboard.md` as the compact orientation page;
- a `README.md` inside the configured inbox as its durable entry point;
- with `para`, `README.md` overviews below projects, areas, resources, and
  archive; and
- with `journal`, READMEs below the journal root and its configured daily,
  weekly, and yearly directories.

These are ordinary user-owned notes, not release-managed files. Existing files
are reported as preserved and never read as templates, adopted, merged, or
overwritten. If any target is a directory, symbolic link, or otherwise unsafe,
the complete bootstrap stops without creating partial files. Repeating the
command is safe and creates only files that are still missing.

Configure filenames in `Vault-OS/config.yaml` before bootstrapping:

```yaml
bootstrap:
  profileFile: Ich.md
  readmeFile: README.md
  dashboardFile: Dashboard.md
  overviewFile: README.md
```

Journal period directories are instance paths rather than portable fixed
names. For a German vault, for example:

```yaml
paths:
  journal: 05 Journal
  journalDaily: 05 Journal/Täglich
  journalWeekly: 05 Journal/Wöchentlich
  journalYearly: 05 Journal/Jährlich
```

Each value is one Markdown filename. `profileFile` defaults to the neutral
`Profile.md`; names such as `Ich.md` therefore remain an instance choice.
`AGENTS.md` is not a bootstrap file: it is generated separately by `agent-init`
because its content depends on the installed Vault-OS and provider adapters.

## Install into an existing vault

1. Make a backup or clean version-control checkpoint of the vault.
2. Stop other tools that may write files during installation.
3. Choose a system root that does not collide with existing content.
4. Run `install` and then `doctor`.

For side-by-side adoption, use an unused system root:

```bash
.venv/bin/python -m vault_os install "/path/to/Existing Vault" \
  --system-root "Vault-OS System" \
  --module para \
  --module knowledge

.venv/bin/python -m vault_os doctor "/path/to/Existing Vault"
```

Installation preflights the complete package before writing. If a managed
target, `Vault-OS/config.yaml`, or `.vault-os/lock.json` already exists, the
operation stops without a partial installation. Existing instance-owned seed
files are preserved.

There is no separate dry-run command for the first installation. For a complex
or irreplaceable vault, test the command against a copy first. Migrating a
legacy system tree into the Vault-OS ownership model is not automatic; install
side by side and migrate deliberately.

## Customize name, language, paths, and modules

For more than a name or system-root override, copy the neutral configuration
and edit the copy before installation:

```bash
cp instance-template/vault-os.yaml vault-os.local.yaml
```

Set `vault.name`, `vault.language`, the entries under `paths`, and `modules`,
then install with:

```bash
.venv/bin/python -m vault_os install "/path/to/My Vault" \
  --config vault-os.local.yaml
```

Paths are relative to the vault root. Absolute paths, `..`, `.obsidian`, the
filesystem root, and the user's home directory are rejected as targets.

`vault.language: de` installs the complete German template variants;
`de-DE` falls back to the same primary-language package. English is the
canonical fallback for languages without a packaged translation. Language
selection changes headings and guidance, while configured field names, stored
values, module fields, and paths are still materialized from the instance.

After installation, `Vault-OS/config.yaml` is the instance-owned canonical
configuration. Edit that installed file for later module or path changes; do
not keep two competing configuration sources. Field roles, localized stored
values, and module fields live in `Vault-OS/schema/fields.yaml`. Run `update`
after changing either file; this rematerializes managed templates and views
without adopting either instance file into release ownership.

## What installation creates

- the configured system root, normally `99 System`, containing managed core and
  selected-module files;
- visible `Vault-OS/` instance configuration, registers, policies, integration
  choices, validation settings, and agent context;
- `.vault-os/lock.json`, which records the installed release and checksums; and
- the configured inbox plus enabled PARA and journal directories when they do
  not already exist; their contents remain user-owned.

The visible `Vault-OS/` directory is intended to synchronize with ordinary
vault files. Hidden `.vault-os`, `.agents`, `.claude`, `.codex`, `.qmd`, and
`.mcp.json` paths contain device-local state. Do not copy or synchronize those
paths as a substitute for initializing each device.

Managed files must not be edited directly. Put vault-specific values and
customizations in instance-owned files or ordinary vault content. The updater
uses the lock to reject missing or locally modified managed files.

## Next steps

- Apply the optional [recommended Obsidian profile](obsidian-setup.md).
- When using Obsidian Sync on multiple devices, follow the
  [multi-device procedure](obsidian-setup.md#use-obsidian-sync-on-more-than-one-device).
- Set up a local AI client with the [AI setup guide](ai-setup.md).
- Learn safe upgrades and recovery in
  [Upgrade, recover, and remove](upgrade-recover-remove.md).
- Use [Troubleshooting](troubleshooting.md) when a command reports a conflict.
