<!-- SPDX-License-Identifier: MPL-2.0 -->

# 06 Runtime

This layer defines the operating behavior of agents and other runtime
components. It may provide concise execution rules and references to canonical
system sources, but it does not duplicate the complete operating model.

Generated logs, lock data, caches, and observations are runtime-owned local
state. They are not distributed as managed content and are never copied back
into a Vault-OS release.
