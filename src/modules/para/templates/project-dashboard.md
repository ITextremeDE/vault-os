<!-- SPDX-License-Identifier: MPL-2.0 -->

---
{{fields.kind}}: "{{values.kind.system}}"
{{fields.type}}: "{{values.type.dashboard}}"
{{fields.status}}: "{{values.status.active}}"
{{fields.area}}:
aliases: []
tags: []
cssclasses: []
created:
---

# {{title}}

## Open tasks

```dataview
TASK
FROM "{{paths.projects}}"
WHERE !fullyCompleted AND {{fields.area}} = this.{{fields.area}} AND file.name != this.file.name AND file.name != "README"
SORT file.mtime DESC
```

## Active projects

```dataview
TABLE file.link AS Project, {{fields.type}} AS Type, {{fields.status}} AS Status
FROM "{{paths.projects}}"
WHERE {{fields.kind}} = "{{values.kind.project}}" AND {{fields.area}} = this.{{fields.area}} AND {{fields.status}} != "{{values.status.completed}}" AND {{fields.status}} != "{{values.status.archived}}" AND file.name != "README"
SORT file.mtime DESC
```

## Waiting

```dataview
TABLE file.link AS Project, {{fields.type}} AS Type
FROM "{{paths.projects}}"
WHERE {{fields.kind}} = "{{values.kind.project}}" AND {{fields.area}} = this.{{fields.area}} AND {{fields.status}} = "{{values.status.waiting}}" AND file.name != "README"
SORT file.mtime DESC
```

## Completed, not archived

```dataview
TABLE file.link AS Project, {{fields.type}} AS Type
FROM "{{paths.projects}}"
WHERE {{fields.kind}} = "{{values.kind.project}}" AND {{fields.area}} = this.{{fields.area}} AND {{fields.status}} = "{{values.status.completed}}" AND file.name != "README"
SORT file.mtime DESC
```

## Recently changed

```dataview
TABLE file.link AS Note, {{fields.type}} AS Type, {{fields.status}} AS Status
FROM "{{paths.projects}}"
WHERE {{fields.area}} = this.{{fields.area}} AND file.name != this.file.name AND file.name != "README"
SORT file.mtime DESC
LIMIT 10
```
