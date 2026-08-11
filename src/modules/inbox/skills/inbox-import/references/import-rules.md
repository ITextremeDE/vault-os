<!-- SPDX-License-Identifier: MPL-2.0 -->

# Import routing rules

Classify imports by semantic role, not file format:

- reusable explanation, model, principle, or guide → knowledge;
- useful material, document, link, or external reference → resource;
- bounded outcome and implementation context → project;
- person, organization, role, or relationship → contact;
- incomplete or ambiguous material → remain in the inbox.

Strip foreign frontmatter unless a field maps unambiguously to the installed
schema. Normalize imported tags according to instance policy. Preserve Markdown
structure and external links. For PDFs, remove obvious headers, footers, or OCR
artifacts only when the intended text is clear.
