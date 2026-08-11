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

## Focus

## Open tasks

```dataview
TASK
FROM "{{paths.projects}}" OR "{{paths.areas}}"
WHERE !fullyCompleted AND {{fields.area}} = this.{{fields.area}} AND file.name != "README"
SORT file.mtime DESC
```

## Active projects

```dataview
TABLE file.link AS Project, {{fields.type}} AS Type, {{fields.status}} AS Status
FROM "{{paths.projects}}"
WHERE {{fields.kind}} = "{{values.kind.project}}" AND {{fields.area}} = this.{{fields.area}} AND {{fields.status}} != "{{values.status.completed}}" AND {{fields.status}} != "{{values.status.archived}}" AND file.name != "README"
SORT file.mtime DESC
```

## Contacts

```dataview
TABLE file.link AS Contact, {{fields.type}} AS Type, {{fields.status}} AS Status, {{moduleFields.last_contact}} AS "Last contact"
FROM "{{paths.contacts}}"
WHERE {{fields.area}} = this.{{fields.area}} AND file.name != "README"
SORT default({{moduleFields.last_contact}}, date("1900-01-01")) DESC, file.name ASC
```

## Relevant links

```dataview
TABLE file.link AS Note, {{fields.type}} AS Type, {{fields.status}} AS Status
FROM "{{paths.projects}}" OR "{{paths.areas}}" OR "{{paths.resources}}"
WHERE {{fields.area}} = this.{{fields.area}} AND file.name != this.file.name AND file.name != "README"
SORT file.mtime DESC
LIMIT 10
```

## Reflection

- What matters most in this area now?
- Which topic needs structure or a decision?
