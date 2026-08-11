<!-- SPDX-License-Identifier: MPL-2.0 -->

---
{{fields.kind}}: "{{values.kind.conversation-note}}"
{{fields.type}}:
{{fields.status}}: "{{values.status.open}}"
{{fields.area}}:
aliases: []
tags: []
cssclasses: []
created:
{{moduleFields.location}}:
{{moduleFields.date}}:
{{moduleFields.time}}:
{{moduleFields.author}}:
{{moduleFields.participants}}: []
---

# {{title}}

| **Stichwort** | |
| --- | --- |
| **Ort** | `= default(this.{{moduleFields.location}}, "–")` |
| **Datum** | `= choice(this.{{moduleFields.date}}, dateformat(this.{{moduleFields.date}}, "dd.MM.yyyy"), "–")` |
| **Zeit** | `= default(this.{{moduleFields.time}}, "–")` |
| **Autor** | `= default(this.{{moduleFields.author}}, "–")` |
| **Teilnehmer** | `= default(this.{{moduleFields.participants}}, [])` |

## 🎯 Anlass

## 💬 Inhalt

## 💡 Wichtige Punkte

## 🧾 Verarbeitung

- **Stand:** roh / ausgewertet / überführt

# 🧩 Kontext und Aktionen

## 📚 Quellen

## 🔗 Referenzen

## ✅ Aufgaben

- [ ]
