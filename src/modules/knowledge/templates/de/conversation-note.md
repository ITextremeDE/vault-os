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

```base
filters: "file.path == this.file.path"
formulas:
  value_1: "if({{moduleFields.location}}, {{moduleFields.location}}, \"–\")"
  value_2: "if({{moduleFields.date}}, {{moduleFields.date}}.format(\"DD.MM.YYYY\"), \"–\")"
  value_3: "if({{moduleFields.time}}, {{moduleFields.time}}, \"–\")"
  value_4: "if({{moduleFields.author}}, {{moduleFields.author}}, \"–\")"
  value_5: "if(list({{moduleFields.participants}}).isEmpty(), \"–\", {{moduleFields.participants}})"
properties:
  "formula.value_1":
    displayName: "Ort"
  "formula.value_2":
    displayName: "Datum"
  "formula.value_3":
    displayName: "Zeit"
  "formula.value_4":
    displayName: "Autor"
  "formula.value_5":
    displayName: "Teilnehmer"
views:
  - type: table
    name: "Tabelle"
    order:
      - "formula.value_1"
      - "formula.value_2"
      - "formula.value_3"
      - "formula.value_4"
      - "formula.value_5"
```

## 🎯 Anlass

## 💬 Inhalt

## 💡 Wichtige Punkte

## 🧾 Verarbeitung

- **Stand:** roh / ausgewertet / überführt

---

# 🧩 Kontext & Aktionen

## 📚 Quellen

## 🔗 Referenzen

## ✅ Aufgaben

- [ ]
