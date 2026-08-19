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
TABLE WITHOUT ID
  task.text AS "Aufgabe",
  file.link AS "Notiz",
  task.due AS "Fällig"
FROM "{{paths.projects}}" OR "{{paths.areas}}"
FLATTEN file.tasks AS task
WHERE !task.completed AND {{fields.area}} = this.{{fields.area}} AND file.name != "README"
SORT task.due ASC, file.mtime DESC
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
