<!-- SPDX-License-Identifier: MPL-2.0 -->

# 02 Registers

Registers hold the concrete values allowed by a vault or an enabled module.
Examples include areas, relationship types, priorities, or other controlled
vocabularies.

The core defines the register contract. Concrete values are instance-owned and
must not be embedded in managed files. Modules may provide create-only seeds,
but updates never replace a vault owner's register values.

Field mechanics belong to `01 Schema`; operational use of register values
belongs to `03 Workflows`.
