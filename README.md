# Eigenes Brain bauen

Nach einem Wochenende habt ihr eine eigene, durchsuchbare Bibliothek aus rund 20 Fachbüchern zu einem Thema, die Claude vor jeder Antwort nachschlagen muss und bei der jede Fundstelle mit Buch und Seite belegt ist.

Das Verfahren heißt RAG (Retrieval Augmented Generation): Eine Suche holt die passenden Textstellen aus euren Büchern, legt sie der KI hin, und die KI antwortet nur daraus. Ich nenne so eine Bibliothek ein Brain.

## Wer schreibt

Ich bin Chris Erler, Erler Ventures, Berlin. Seit August 2026 baue ich acht Brains zu acht Lebensbereichen. Dazu gehören Geschichte und Musik, daneben Business, Technik, Geld und Steuern, Psychologie, Recht und Familie. Zusammen sind das gut 12.000 Quellen und rund eine Million Textstellen. Ich habe das System am 30.10.2026 bei der BCD-Gruppe vorgestellt. Dieser Bauplan ist die Anleitung dazu, geschrieben für Leute ohne Entwicklerwissen, die einer Anleitung folgen.

## Das Bild dahinter

Stellt euch eine Bibliothek vor, in der eure Bücher in Karteikarten zerlegt sind. Jede Karte ist ein Textausschnitt von etwa einer Buchseite (Fachwort: Chunk). Zwei Bibliothekare suchen gleichzeitig, der eine nach genauen Wörtern, der andere nach Bedeutung. Ein dritter Prüfer liest die besten Kandidaten noch einmal und gibt acht Stellen an Claude weiter. Am Tresen, einem Programm namens MCP-Server, fragt Claude dieses Regal. Das Bild stammt aus meiner ersten Anleitung für das Geschichts-Brain und kommt in allen Kapiteln wieder vor.

## Für wen

- Vermögensberater, Unternehmer und Berater, die in einem Fachgebiet heute googeln und zweifeln, weil das Wissen verstreut liegt.
- Leute, die einen PC kaufen oder vorhandene Hardware nutzen, ein Programm installieren und eine Anleitung Schritt für Schritt befolgen können.
- Wer bereit ist, rund 30 Euro je Fachbuch auszugeben und ein Wochenende zu investieren.

## Für wen nicht

- Wer eine KI sucht, die keine Fehler macht. Ein Brain macht Fehler sichtbar, es macht sie nicht unmöglich. Siehe [Kapitel 1](01-warum-ein-brain.md).
- Wer Bücher aus unklaren Quellen einlesen will, denn das Kapitel zur Beschaffung nennt nur saubere Wege.
- Wer tagesaktuelle Daten braucht, denn ein Brain kennt nur, was ihr eingelesen habt.
- Wer vertrauliche Mandantendaten in die Cloud schicken möchte, ohne den Datenweg zu prüfen. Siehe [Kapitel 10](10-betrieb-kosten-datenschutz.md).

## Reihenfolge der Kapitel

1. [Warum ein Brain](01-warum-ein-brain.md): Warum eine KI mit eigener Bibliothek weniger erfindet und wie ich das gemessen habe.
2. [Hardware](02-hardware.md): Drei Stufen von ohne Grafikkarte bis 24 GB Grafikspeicher, mit gemessenen Zeiten.
3. [Quellen finden](03-quellen-finden.md): Wie ihr ein Fachgebiet in 20 Standardwerke übersetzt und das Register führt.
4. [Quellen beschaffen](04-quellen-beschaffen.md): Kanäle, Preise und die Regeln, was ihr legal einlesen dürft.
5. [Einlesen und Index](05-einlesen-und-index.md): Von der PDF-Datei zum durchsuchbaren Index, Schritt für Schritt.
6. [Suche](06-suche.md): Was zwischen eurer Frage und den acht Stellen passiert.
7. [Messen und verbessern](07-messen-und-verbessern.md): Wie ihr mit Testfragen prüft, ob jede Änderung etwas bringt.
8. [Anschluss an Claude](08-anschluss-claude-mcp.md): Das Brain als Erweiterung in Claude Desktop und Claude Code.
9. [Shallow und Deep Research](09-shallow-vs-deep-research.md): Wann eine Suche reicht und wann ihr eine Frage in Teilfragen zerlegt.
10. [Betrieb, Kosten, Datenschutz](10-betrieb-kosten-datenschutz.md): Was es kostet, was den Rechner verlässt und wie ihr den Index pflegt.
11. [Wochenende-Plan](11-wochenende-plan.md): Die Checkliste mit Uhrzeiten und Abbruchkriterien.

Dazu gibt es ein [Glossar](glossar.md) mit allen Fachwörtern, einen Ordner `code` mit minimalem Referenzcode und einen Ordner `slides` mit den Folien.

## Wie ihr lest

Wollt ihr sofort loslegen, lest Kapitel 2 und dann 11. Wollt ihr verstehen, was ihr baut, lest von vorn. Jeder Fachbegriff wird beim ersten Auftreten in einem Satz erklärt, und das Glossar hilft beim Nachschlagen.

Jedes Kapitel endet mit dem Abschnitt "Was hier offen ist". Dort steht, was ich nicht gemessen oder nicht geprüft habe, denn die Zahlen stammen von meinen Rechnern und meinen Büchern, und einige Messungen haben Schwächen, die ich benenne.

## Wichtiger Hinweis

Das hier ist kein Rechts- und kein Steuerrat. Der Bauplan beschreibt ein privates System, so wie ich es betreibe, Stand 30.10.2026. Beispiele aus Recht und Steuern zeigen die Technik, sie ersetzen weder Anwalt noch Steuerberater. Vor der Nutzung für Mandanten oder Kunden klärt ihr Berufsrecht, Datenschutz und Urheberrecht selbst.
