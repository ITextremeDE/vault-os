<!-- SPDX-License-Identifier: MPL-2.0 -->

# Area register

An area assigns content to one durable responsibility or context.

## Contract

- Area values are instance-owned canonical plain names.
- A file has at most one area unless a module explicitly defines another
  relationship model.
- Values use their exact registered spelling.
- The instance field profile chooses whether frontmatter stores that name as
  text or as a Wiki link to the area's note or dashboard. Link syntax never
  belongs in this register; a dashboard link retains the registered name as its
  display alias.
- A new area represents an ongoing context, not a finite project.
- Content kinds may declare that an area is required or optional.
- Updates may seed a missing register but never replace its values.

The neutral area register starts empty. Each vault owner defines active and
historical values in the instance register.
