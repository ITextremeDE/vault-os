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

# 🧭 Projekte · {{title}}

## ✅ Offene Aufgaben

```dataview
TABLE WITHOUT ID
  task.text AS "Aufgabe",
  file.link AS "Notiz",
  task.due AS "Fällig"
FROM "{{paths.projects}}"
FLATTEN file.tasks AS task
WHERE !task.completed AND {{fields.area}} = this.{{fields.area}} AND file.name != this.file.name AND file.name != "README"
SORT task.due ASC, file.mtime DESC
```

## 📂 Aktive Projekte

![[{{paths.system}}/04 Assets/Bases/Project Dashboards.base#Aktive Projekte]]

## ⏳ Warten auf

![[{{paths.system}}/04 Assets/Bases/Project Dashboards.base#Warten auf]]

## ✅ Abgeschlossen, nicht archiviert

![[{{paths.system}}/04 Assets/Bases/Project Dashboards.base#Abgeschlossen, nicht archiviert]]

## 🕒 Zuletzt geändert

![[{{paths.system}}/04 Assets/Bases/Project Dashboards.base#Zuletzt geändert]]

## 🧭 Reflexion

- Welches Projekt braucht als Nächstes eine klare Entscheidung?
- Was ist abgeschlossen, aber noch nicht sauber archiviert?
- Wo blockiert ein offener Punkt den nächsten sinnvollen Schritt?
