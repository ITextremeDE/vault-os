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

| **Topic** | |
| --- | --- |
| **Location** | `= default(this.{{moduleFields.location}}, "–")` |
| **Date** | `= choice(this.{{moduleFields.date}}, dateformat(this.{{moduleFields.date}}, "yyyy-MM-dd"), "–")` |
| **Time** | `= default(this.{{moduleFields.time}}, "–")` |
| **Author** | `= default(this.{{moduleFields.author}}, "–")` |
| **Participants** | `= default(this.{{moduleFields.participants}}, [])` |

## 🎯 Occasion

## 💬 Content

## 💡 Key points

## 🧾 Processing

- **State:** raw / evaluated / transferred

# 🧩 Context and actions

## 📚 Sources

## 🔗 References

## ✅ Tasks

- [ ]
