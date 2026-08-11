<!-- SPDX-License-Identifier: MPL-2.0 -->

---
{{fields.kind}}: "{{values.kind.contact}}"
{{fields.type}}: "{{values.type.contact.person}}"
{{fields.status}}: "{{values.status.active}}"
{{fields.area}}:
aliases: []
tags: []
cssclasses: []
created:
{{moduleFields.job}}:
{{moduleFields.relationship}}: []
{{moduleFields.relevance}}:
{{moduleFields.last_contact}}:
---

# {{title}}

{{logo}}

{{photo}}

## 🧾 Identity

- **First name:**
- **Last name:**
- **Job:** `= default(this.{{moduleFields.job}}, "–")`

## 🤝 Relationship

- **Relationship type:** `= default(this.{{moduleFields.relationship}}, "–")`
- **Relevance:** `= default(this.{{moduleFields.relevance}}, "–")`
- **Last contact:** `= choice(this.{{moduleFields.last_contact}}, dateformat(this.{{moduleFields.last_contact}}, "yyyy-MM-dd"), "–")`

## 🗓️ Interactions

## 🧠 Context and notes

# 🧩 Context and actions

## 📚 Sources

## 🔗 References

## ✅ Tasks

- [ ]
