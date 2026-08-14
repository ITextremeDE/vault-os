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

# 🧠 {{title}}

## 🎯 Fokus

## ✅ Offene Aufgaben

```dataview
TASK
FROM "{{paths.projects}}" OR "{{paths.areas}}"
WHERE !fullyCompleted AND {{fields.area}} = this.{{fields.area}} AND file.name != "README"
SORT file.mtime DESC
```

## 📂 Aktive Projekte

![[{{paths.system}}/04 Assets/Bases/Project Dashboards.base#Aktive Projekte]]

## 👥 Kontakte

![[{{paths.system}}/04 Assets/Bases/Area Dashboards.base#Kontakte]]

## 🔗 Relevante Verknüpfungen

![[{{paths.system}}/04 Assets/Bases/Area Dashboards.base#Relevante Verknüpfungen]]

## 🕒 Zuletzt geändert

![[{{paths.system}}/04 Assets/Bases/Area Dashboards.base#Zuletzt geändert]]

## 🧭 Reflexion

- Was ist in diesem Bereich aktuell wirklich wichtig?
- Welches laufende Thema braucht Struktur statt nur Aufmerksamkeit?
- Wo fehlt eine klare Entscheidung, Verknüpfung oder nächste Aktion?
