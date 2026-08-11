<!-- SPDX-License-Identifier: MPL-2.0 -->

# Area register

An area assigns content to one durable responsibility or context.

## Contract

- Area values are instance-owned strings.
- A file has at most one area unless a module explicitly defines another
  relationship model.
- Values use their exact registered spelling.
- A new area represents an ongoing context, not a finite project.
- Content kinds may declare that an area is required or optional.
- Updates may seed a missing register but never replace its values.

The neutral area register starts empty. Each vault owner defines active and
historical values in the instance register.
