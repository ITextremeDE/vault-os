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
TASK
FROM "{{paths.projects}}"
WHERE !fullyCompleted AND {{fields.area}} = this.{{fields.area}} AND file.name != this.file.name AND file.name != "README"
SORT file.mtime DESC
```

## 📂 Aktive Projekte

```dataview
TABLE file.link AS Projekt, {{fields.type}} AS Typ, {{fields.status}} AS Status, dateformat(file.ctime, "dd.MM.yyyy") AS Erstellt, dateformat(file.mtime, "dd.MM.yyyy") AS Geändert
FROM "{{paths.projects}}"
WHERE {{fields.kind}} = "{{values.kind.project}}" AND {{fields.area}} = this.{{fields.area}} AND {{fields.status}} != "{{values.status.completed}}" AND {{fields.status}} != "{{values.status.archived}}" AND file.name != "README"
SORT file.mtime DESC
```

## ⏳ Warten auf

```dataview
TABLE file.link AS Projekt, {{fields.type}} AS Typ, dateformat(file.ctime, "dd.MM.yyyy") AS Erstellt, dateformat(file.mtime, "dd.MM.yyyy") AS Geändert
FROM "{{paths.projects}}"
WHERE {{fields.kind}} = "{{values.kind.project}}" AND {{fields.area}} = this.{{fields.area}} AND {{fields.status}} = "{{values.status.waiting}}" AND file.name != "README"
SORT file.mtime DESC
```

## ✅ Abgeschlossen, nicht archiviert

```dataview
TABLE file.link AS Projekt, {{fields.type}} AS Typ, dateformat(file.ctime, "dd.MM.yyyy") AS Erstellt, dateformat(file.mtime, "dd.MM.yyyy") AS Geändert
FROM "{{paths.projects}}"
WHERE {{fields.kind}} = "{{values.kind.project}}" AND {{fields.area}} = this.{{fields.area}} AND {{fields.status}} = "{{values.status.completed}}" AND file.name != "README"
SORT file.mtime DESC
```

## 🕒 Zuletzt geändert

```dataview
TABLE file.link AS Datei, {{fields.type}} AS Typ, {{fields.status}} AS Status, dateformat(file.ctime, "dd.MM.yyyy") AS Erstellt, dateformat(file.mtime, "dd.MM.yyyy") AS Geändert
FROM "{{paths.projects}}"
WHERE {{fields.area}} = this.{{fields.area}} AND file.name != this.file.name AND file.name != "README"
SORT file.mtime DESC
LIMIT 10
```

## 🧭 Reflexion

- Welches Projekt braucht als Nächstes eine klare Entscheidung?
- Was ist abgeschlossen, aber noch nicht sauber archiviert?
- Wo blockiert ein offener Punkt den nächsten sinnvollen Schritt?
