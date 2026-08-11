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

```dataview
TABLE file.link AS Projekt, {{fields.type}} AS Typ, {{fields.status}} AS Status, dateformat(file.ctime, "dd.MM.yyyy") AS Erstellt, dateformat(file.mtime, "dd.MM.yyyy") AS Geändert
FROM "{{paths.projects}}"
WHERE {{fields.kind}} = "{{values.kind.project}}" AND {{fields.area}} = this.{{fields.area}} AND {{fields.status}} != "{{values.status.completed}}" AND {{fields.status}} != "{{values.status.archived}}" AND file.name != "README"
SORT file.mtime DESC
```

## 👥 Kontakte

```dataview
TABLE file.link AS Kontakt, {{fields.type}} AS Typ, {{fields.status}} AS Status, choice({{moduleFields.last_contact}}, dateformat({{moduleFields.last_contact}}, "dd.MM.yyyy"), "–") AS "Letzter Kontakt", dateformat(file.ctime, "dd.MM.yyyy") AS Erstellt, dateformat(file.mtime, "dd.MM.yyyy") AS Geändert
FROM "{{paths.contacts}}"
WHERE {{fields.area}} = this.{{fields.area}} AND file.name != "README"
SORT default({{moduleFields.last_contact}}, date("1900-01-01")) DESC, file.name ASC
```

## 🔗 Relevante Verknüpfungen

```dataview
TABLE file.link AS Datei, {{fields.type}} AS Typ, {{fields.status}} AS Status, dateformat(file.ctime, "dd.MM.yyyy") AS Erstellt, dateformat(file.mtime, "dd.MM.yyyy") AS Geändert
FROM "{{paths.projects}}" OR "{{paths.areas}}" OR "{{paths.resources}}"
WHERE {{fields.area}} = this.{{fields.area}} AND file.name != this.file.name AND file.name != "README"
SORT file.mtime DESC
LIMIT 10
```

## 🕒 Zuletzt geändert

```dataview
TABLE file.link AS Datei, {{fields.type}} AS Typ, {{fields.status}} AS Status, dateformat(file.ctime, "dd.MM.yyyy") AS Erstellt, dateformat(file.mtime, "dd.MM.yyyy") AS Geändert
FROM "{{paths.projects}}" OR "{{paths.areas}}" OR "{{paths.resources}}"
WHERE {{fields.area}} = this.{{fields.area}} AND file.name != this.file.name AND file.name != "README"
SORT file.mtime DESC
LIMIT 10
```

## 🧭 Reflexion

- Was ist in diesem Bereich aktuell wirklich wichtig?
- Welches laufende Thema braucht Struktur statt nur Aufmerksamkeit?
- Wo fehlt eine klare Entscheidung, Verknüpfung oder nächste Aktion?
