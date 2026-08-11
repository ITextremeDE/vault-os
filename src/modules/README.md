# Vault-OS modules

This directory contains optional, release-managed capabilities that are not
required by every vault. The extracted catalog provides agent assets, audits,
contacts, Git policy support, governance, inbox processing, journal, knowledge,
navigation, PARA, publishing, content review, local conversation search, and
template-driven creation.

A module may depend on documented core interfaces, but it must not depend on a
specific vault name or owner. Every installable module has its own manifest and
must use targets that do not collide with core or another module.
