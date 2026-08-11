<!-- SPDX-License-Identifier: MPL-2.0 -->

---
kind: contact
type: organization
status: active
area:
aliases: []
tags: []
cssclasses: []
created:
relationship: []
relevance:
last_contact:
---

# {{title}}

## Organization

## Relationship

## Representatives

```dataview
TABLE file.link AS Representative, status AS Status, last_contact AS "Last contact"
FROM "{{paths.contacts}}"
WHERE type = "representative" AND contains(organizations, this.file.link)
SORT default(last_contact, date("1900-01-01")) DESC, file.name ASC
```

## Interactions

## Context and notes

## Sources

## References

## Tasks

- [ ]
