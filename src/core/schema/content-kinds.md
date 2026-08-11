<!-- SPDX-License-Identifier: MPL-2.0 -->

# Content kinds

A content kind states what a file fundamentally represents. The core defines
the mechanism, not a universal catalog of user content.

## Rules

- Every kind has a stable identifier.
- A kind is owned by exactly one installed component.
- New kinds require a recurring, clearly distinct purpose.
- Types refine a kind; they do not replace it.
- Status describes lifecycle, not priority, mood, or importance.
- Module manifests provide machine-readable kind definitions.
- Duplicate kind identifiers across installed modules are invalid.

The optional PARA, knowledge, contacts, and journal modules provide the initial
portable catalog extracted from the source vault.
