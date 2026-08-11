<!-- SPDX-License-Identifier: MPL-2.0 -->

# Principles

## 1. One canonical source

Every rule, value list, and structural definition has exactly one authoritative
location. Other files link to it instead of maintaining competing copies.

## 2. Separate responsibilities

Architecture, schemas, registers, workflows, assets, automation, and runtime
state remain distinct. Each file belongs to one primary layer and one owner.

## 3. Prefer minimal changes

Improve an existing structure before adding another one. New fields, files,
types, and exceptions require a clear recurring need.

## 4. Structure before speed

Fast processing is useful only when ownership and placement remain correct.
Ambiguous information goes through the configured capture workflow.

## 5. Clarity before cleverness

Use descriptive names, stable fields, explicit paths, and simple rules. Avoid
hidden behavior and technical shorthand without practical value.

## 6. Humans and agents share the system

Rules must be understandable to people and deterministic enough for agent and
automation use.

## 7. Standards before assets

Schemas define structure, registers define concrete values, and workflows
define operation. Templates, prompts, skills, and automation apply these
definitions but do not invent replacements.

## 8. Preserve ownership boundaries

Updates may replace only unchanged managed files. Instance content,
configuration, and generated runtime state remain under local control.

## 9. Lifecycle is explicit

Capture, active use, completion, archival, and deletion are deliberate states
defined by the selected modules and instance policy.

## 10. Portability before local optimization

Core mechanics remain independent of vault names, people, organizations,
absolute paths, enabled modules, and external systems.
