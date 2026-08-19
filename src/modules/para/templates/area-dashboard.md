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

## 🎯 Focus

## ✅ Open tasks

```dataview
TABLE WITHOUT ID
  task.text AS "Task",
  file.link AS "Note",
  task.due AS "Due"
FROM "{{paths.projects}}" OR "{{paths.areas}}"
FLATTEN file.tasks AS task
WHERE !task.completed AND {{fields.area}} = this.{{fields.area}} AND file.name != "README"
SORT task.due ASC, file.mtime DESC
```

## 📂 Active projects

![[{{paths.system}}/04 Assets/Bases/Project Dashboards.base#Active projects]]

## 👥 Contacts

![[{{paths.system}}/04 Assets/Bases/Area Dashboards.base#Contacts]]

## 🔗 Relevant links

![[{{paths.system}}/04 Assets/Bases/Area Dashboards.base#Relevant links]]

## 🕒 Recently changed

![[{{paths.system}}/04 Assets/Bases/Area Dashboards.base#Recently changed]]

## 🧭 Reflection

- What matters most in this area now?
- Which ongoing topic needs structure rather than attention?
- Where is a clear decision, link, or next action missing?
