<!-- SPDX-License-Identifier: MPL-2.0 -->

# 01 Schema

This layer owns the portable mechanics used to describe vault content, such as
link behavior and the contracts through which modules contribute fields,
content kinds, states, and naming rules.

The core does not prescribe a complete content model. Optional modules define
their own schema extensions, while concrete allowed values remain instance
data under `02 Registers`.
