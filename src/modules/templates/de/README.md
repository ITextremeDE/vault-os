<!-- SPDX-License-Identifier: MPL-2.0 -->

# Vorlagenmodul

Vorlagen sind zentral verwaltete, strukturierte Ausgangspunkte. Sie wenden die
installierten Schema-, Register- und Workflow-Regeln an, ohne sie neu zu
definieren. Eine Vorlage gehört nur in das System, wenn ihre Inhaltsform
wiederkehrend ist. Für jeden Zweck gibt es genau eine kanonische Vorlage.

Portable Quellen verwenden reservierte Materialisierungsvariablen für
semantische Felder, Werte, Modulfelder und konfigurierte Pfade. Installation und
Aktualisierung lösen diese Variablen auf, bevor die verwalteten Vorlagen
Obsidian erreichen. Native Obsidian-Platzhalter wie `{{title}}` und
Datumsausdrücke bleiben erhalten.

Die kanonischen Quellen sind englisch. Verwaltete Einträge können vollständige
Übersetzungen bereitstellen. Vault-OS wählt zuerst die exakt konfigurierte
Sprache, dann deren primäres Sprachkürzel und verwendet schließlich Englisch als
Fallback. Die Übersetzung verändert Darstellung und Hinweise, aber niemals
semantische Kennungen, Feldzuordnungen, Pfade oder Eigentumsgrenzen.

Vorlagen sind bewusst nützliche Strukturen statt leerer Gerippe. Sie dürfen
Leitfragen, Dataview-Abfragen und wiederkehrende Kontextabschnitte enthalten,
müssen aber unabhängig von einem bestimmten Vault, einer Person, Organisation
oder einem externen Dienst bleiben.
