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

# Projects · {{area}}

## Open tasks

```dataview
TASK
FROM "{{paths.projects}}/{{area}}"
WHERE !fullyCompleted AND file.name != this.file.name
SORT file.mtime DESC
```

## Active projects

```dataview
TABLE file.link AS Project, type AS Type, status AS Status
FROM "{{paths.projects}}/{{area}}"
WHERE kind = "project" AND status != "completed" AND status != "archived"
SORT file.mtime DESC
```

## Waiting

```dataview
TABLE file.link AS Project, type AS Type
FROM "{{paths.projects}}/{{area}}"
WHERE kind = "project" AND status = "waiting"
SORT file.mtime DESC
```

## Completed, not archived

```dataview
TABLE file.link AS Project, type AS Type
FROM "{{paths.projects}}/{{area}}"
WHERE kind = "project" AND status = "completed"
SORT file.mtime DESC
```

## Recently changed

```dataview
TABLE file.link AS Note, type AS Type, status AS Status
FROM "{{paths.projects}}/{{area}}"
WHERE file.name != this.file.name
SORT file.mtime DESC
LIMIT 10
```
