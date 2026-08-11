# Vault-OS modules

This directory contains optional, release-managed capabilities that are not
required by every vault. The initial extracted modules provide PARA, knowledge,
contacts, journal, Git commit-planning, and local conversation-search behavior.

A module may depend on documented core interfaces, but it must not depend on a
specific vault name or owner. Every installable module has its own manifest and
must use targets that do not collide with core or another module.
