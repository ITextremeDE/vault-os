---
name: git-commit-plan
description: Inspect a Git change scope and prepare or execute safe, coherent commits using instance policy.
---

# Git commit plan

## Purpose

Inspect the real repository state, separate unrelated changes, detect risky
files, and produce a useful commit history. Propose by default; stage, commit,
or push only when the user explicitly requests execution.

## Scope order

1. Files or topics named by the user.
2. Already staged changes.
3. Remaining working-tree changes only when no narrower scope exists.

Inspect branch, upstream divergence, staged and unstaged changes, additions,
deletions, renames, diff statistics, large files, binaries, generated files,
conflicts, and files outside the requested scope.

Load category names, prefixes, language, validation commands, and explicitly
accepted secret findings from the instance commit policy. Do not invent or
broaden exceptions.

## Planning

1. Identify the purpose of every in-scope change.
2. Assign the configured category.
3. Keep one coherent purpose per commit.
4. Separate independent or differently owned changes.
5. Keep dependent changes together when separation creates an inconsistent
   intermediate state.
6. Propose the commit order before execution when multiple commits are needed.

## Safety

Stop and report:

- credentials, private keys, or unexpected secret findings;
- conflict markers or unresolved merges;
- an unexpected branch, detached HEAD, or divergent history;
- staged and unstaged changes to the same file;
- unexpected deletion, mass rename, binary, archive, backup, cache, or export;
- changes outside the authorized scope.

Use only the exact path-and-rule combinations listed as accepted secret
findings. Never print secret values.

## Commit message

Use the configured prefix and language. The summary is one concrete line,
normally no longer than 72 characters and without a trailing period. The body
contains two to six short bullets grouped by purpose or effect. Mention only
validation that actually ran.

## Execution

Stage only reviewed files or hunks. After every commit, inspect its actual
content and the remaining working tree. After a push, verify the target remote
and commit identifier before reporting success.
