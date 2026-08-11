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

{{logo}}

## 🧾 Organization

- **Name:**
- **Organization type:**

## 🤝 Relationship

- **Relationship type:** `= default(this.{{moduleFields.relationship}}, "–")`
- **Relevance:** `= default(this.{{moduleFields.relevance}}, "–")`
- **Last contact:** `= choice(this.{{moduleFields.last_contact}}, dateformat(this.{{moduleFields.last_contact}}, "yyyy-MM-dd"), "–")`

## 👥 Representatives

```dataview
TABLE file.link AS Representative, {{fields.status}} AS Status, choice({{moduleFields.last_contact}}, dateformat({{moduleFields.last_contact}}, "yyyy-MM-dd"), "–") AS "Last contact"
FROM "{{paths.contacts}}"
WHERE {{fields.type}} = "{{values.type.representative}}" AND contains({{moduleFields.organizations}}, this.file.link)
SORT default({{moduleFields.last_contact}}, date("1900-01-01")) DESC, file.name ASC
```

## 🗓️ Interactions

## 🧠 Context and notes

# 🧩 Context and actions

## 📚 Sources

## 🔗 References

## ✅ Tasks

- [ ]
