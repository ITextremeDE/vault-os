<!-- SPDX-License-Identifier: MPL-2.0 -->

# Status model

Status represents the lifecycle state of content. Concrete values and allowed
transitions belong to the module that owns the content kind.

## Rules

- Every allowed status is declared for a content kind.
- Status identifiers use their exact declared spelling.
- Free-form or undeclared values are invalid.
- Transitions should be explainable and domain-appropriate.
- Archival and reactivation are deliberate transitions, not automatic side
  effects of file placement.
- Priority, sentiment, and waiting reasons use separate fields when a module
  needs them.

The validator checks membership in the installed module schemas. Transition
enforcement may be added by a module when previous state is available.
