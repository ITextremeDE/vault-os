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
TASK
FROM "{{paths.projects}}" OR "{{paths.areas}}"
WHERE !fullyCompleted AND {{fields.area}} = this.{{fields.area}} AND file.name != "README"
SORT file.mtime DESC
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
