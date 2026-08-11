<!-- SPDX-License-Identifier: MPL-2.0 -->

# Type model

A type refines one content kind without expanding the top-level kind catalog.

## Rules

- Every type belongs to exactly one kind within its owning module.
- Type identifiers are declared and are not free-form labels.
- A new type needs recurring use and a clear distinction from existing types.
- Templates and workflows may depend on declared types.
- The same display label may appear in different modules only when its stable
  identifier remains unambiguous in the installed schema.

Concrete type catalogs are module-owned machine-readable data.
