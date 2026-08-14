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

## ✅ Open tasks

```dataview
TASK
FROM "{{paths.projects}}"
WHERE !fullyCompleted AND {{fields.area}} = this.{{fields.area}} AND file.name != this.file.name AND file.name != "README"
SORT file.mtime DESC
```

## 📂 Active projects

![[{{paths.system}}/04 Assets/Bases/Project Dashboards.base#Active projects]]

## ⏳ Waiting

![[{{paths.system}}/04 Assets/Bases/Project Dashboards.base#Waiting]]

## ✅ Completed, not archived

![[{{paths.system}}/04 Assets/Bases/Project Dashboards.base#Completed, not archived]]

## 🕒 Recently changed

![[{{paths.system}}/04 Assets/Bases/Project Dashboards.base#Recently changed]]

## 🧭 Reflection

- Which project needs a clear decision next?
- What is complete but not yet cleanly archived?
- Where does an unresolved issue block the next useful step?
