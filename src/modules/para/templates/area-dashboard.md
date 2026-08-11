<!-- SPDX-License-Identifier: MPL-2.0 -->

---
kind: system
type: dashboard
status: active
area:
aliases: []
tags: []
cssclasses: []
created:
---

# {{area}}

## Focus

## Open tasks

```dataview
TASK
FROM "{{paths.projects}}/{{area}}" OR "{{paths.areas}}/{{area}}"
WHERE !fullyCompleted
SORT file.mtime DESC
```

## Active projects

```dataview
TABLE file.link AS Project, type AS Type, status AS Status
FROM "{{paths.projects}}/{{area}}"
WHERE kind = "project" AND status != "completed" AND status != "archived"
SORT file.mtime DESC
```

## Contacts

```dataview
TABLE file.link AS Contact, type AS Type, status AS Status, last_contact AS "Last contact"
FROM "{{paths.contacts}}"
WHERE area = "{{area}}"
SORT default(last_contact, date("1900-01-01")) DESC, file.name ASC
```

## Relevant links

```dataview
TABLE file.link AS Note, type AS Type, status AS Status
FROM "{{paths.projects}}/{{area}}" OR "{{paths.areas}}/{{area}}" OR "{{paths.resources}}"
WHERE area = "{{area}}" AND file.name != this.file.name
SORT file.mtime DESC
LIMIT 10
```

## Reflection

- What matters most in this area now?
- Which topic needs structure or a decision?
