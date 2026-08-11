<!-- SPDX-License-Identifier: MPL-2.0 -->

---
{{fields.kind}}: "{{values.kind.contact}}"
{{fields.type}}: "{{values.type.organization}}"
{{fields.status}}: "{{values.status.active}}"
{{fields.area}}:
aliases: []
tags: []
cssclasses: []
created:
{{moduleFields.relationship}}: []
{{moduleFields.relevance}}:
{{moduleFields.last_contact}}:
---

# {{title}}

## Organization

## Relationship

## Representatives

```dataview
TABLE file.link AS Representative, {{fields.status}} AS Status, {{moduleFields.last_contact}} AS "Last contact"
FROM "{{paths.contacts}}"
WHERE {{fields.type}} = "{{values.type.representative}}" AND contains({{moduleFields.organizations}}, this.file.link)
SORT default({{moduleFields.last_contact}}, date("1900-01-01")) DESC, file.name ASC
```

## Interactions

## Context and notes

## Sources

## References

## Tasks

- [ ]
