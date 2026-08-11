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

## 🧾 Basisdaten

- **Name:**
- **Art der Organisation:**

## 🤝 Beziehung

- **Beziehungstyp:** `= default(this.{{moduleFields.relationship}}, "–")`
- **Relevanz:** `= default(this.{{moduleFields.relevance}}, "–")`
- **Letzter Kontakt:** `= choice(this.{{moduleFields.last_contact}}, dateformat(this.{{moduleFields.last_contact}}, "dd.MM.yyyy"), "–")`

## 👥 Ansprechpartner

```dataview
TABLE file.link AS Ansprechpartner, {{fields.status}} AS Status, choice({{moduleFields.last_contact}}, dateformat({{moduleFields.last_contact}}, "dd.MM.yyyy"), "–") AS "Letzter Kontakt"
FROM "{{paths.contacts}}"
WHERE {{fields.type}} = "{{values.type.representative}}" AND contains({{moduleFields.organizations}}, this.file.link)
SORT default({{moduleFields.last_contact}}, date("1900-01-01")) DESC, file.name ASC
```

## 🗓️ Interaktionen

## 🧠 Kontext und Notizen

# 🧩 Kontext und Aktionen

## 📚 Quellen

## 🔗 Referenzen

## ✅ Aufgaben

- [ ]
