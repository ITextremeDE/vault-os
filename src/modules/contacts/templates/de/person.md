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

## 🧾 Basisdaten

- **Vorname:**
- **Nachname:**
- **Job:** `= default(this.{{moduleFields.job}}, "–")`

## 🤝 Beziehung

- **Beziehungstyp:** `= default(this.{{moduleFields.relationship}}, "–")`
- **Relevanz:** `= default(this.{{moduleFields.relevance}}, "–")`
- **Letzter Kontakt:** `= choice(this.{{moduleFields.last_contact}}, dateformat(this.{{moduleFields.last_contact}}, "dd.MM.yyyy"), "–")`

## 🗓️ Interaktionen

## 🧠 Kontext und Notizen

# 🧩 Kontext und Aktionen

## 📚 Quellen

## 🔗 Referenzen

## ✅ Aufgaben

- [ ]
