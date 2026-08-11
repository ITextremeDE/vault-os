"""Built-in provider adapters and their registry."""

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from .base import ProviderAdapter, ProviderHealth, ProviderRegistry, SkillAdapter
from .claude import ClaudeProviderAdapter
from .codex import CodexProviderAdapter


PROVIDER_REGISTRY = ProviderRegistry(
    (
        ClaudeProviderAdapter(),
        CodexProviderAdapter(),
    )
)


def provider_ids() -> tuple[str, ...]:
    """Return every provider id registered by this package."""

    return PROVIDER_REGISTRY.ids()


__all__ = [
    "PROVIDER_REGISTRY",
    "ProviderAdapter",
    "ProviderHealth",
    "ProviderRegistry",
    "SkillAdapter",
    "provider_ids",
]
