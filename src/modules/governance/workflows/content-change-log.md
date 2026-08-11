<!-- SPDX-License-Identifier: MPL-2.0 -->

# Content change log

The instance may maintain one chronological runtime log for material changes to
content notes. Log creation, material edits, moves, renames, lifecycle changes,
archiving, reactivation, authorized deletion, and review corrections. Do not log
pure formatting, spelling, or release-managed system changes.

Each entry records date, vault-relative scope, operation, and a concise change
description. Newest entries come first. Never fabricate history. `modified`
records a note change and `reviewed` records a completed review; neither replaces
the log. Runtime history remains instance-owned and is never shipped by Vault-OS.
