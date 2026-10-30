# 11. Wochenende-Plan

Ein Thema, 20 Bücher, 10 Prüffragen: Wer den Plan abarbeitet, hat am Sonntag ein Brain, das ihr ausprobiert habt. Alle Zeiten sind Planwerte für ein Brain mit rund 7.200 Chunks, die Rechenzeiten sind gerechnet (siehe [Kapitel 2](02-hardware.md)). Zu jedem Schritt gehört ein Abbruchkriterium, damit ihr euch nicht festfahrt.

## Freitag, 18:00 bis 20:30

- [ ] **18:00 Thema wählen (30 Minuten).** Nehmt das Thema, bei dem ihr heute am meisten googelt und zweifelt, weil das Wissen verstreut ist. Abbruch: Habt ihr nach 30 Minuten zwei Themen, nehmt das mit mehr offenen Fragen aus der letzten Woche.
- [ ] **18:30 20 Titel auswählen (60 Minuten).** Liste A frei und legal, Liste B Kaufliste ([Kapitel 3](03-quellen-finden.md)). Abbruch: Habt ihr nach 90 Minuten keine 20, startet mit sechs Büchern. Das reicht für den ersten Test.
- [ ] **19:30 Zehn Prüffragen schreiben (30 Minuten).** Frage, erwartete Antwort, erwartetes Buch. Schreibt sie jetzt, bevor ihr das System seht, sonst formt ihr die Fragen nach seinen Treffern. Abbruch: Fallen euch keine zehn ein, ist das Thema zu breit oder zu neu. Engt es ein.
- [ ] **20:00 Rechner prüfen (30 Minuten).** Python, Torch, `torch.cuda.is_available()` ([Kapitel 2](02-hardware.md)). Abbruch: Kommt `False` trotz Grafikkarte, installiert Torch mit CUDA neu. Klappt es nach 30 Minuten nicht, geht auf Stufe 1 und lasst den Reranker aus.

## Samstag, 09:00 bis 17:00

- [ ] **09:00 Beschaffen (2 Stunden, Planwert).** Kauft DRM-freie Ausgaben, ladet freie Quellen ([Kapitel 4](04-quellen-beschaffen.md)). Abbruch: Gibt es einen Titel nur mit Kopierschutz, nehmt eine andere Ausgabe oder lasst ihn weg. Entfernt den Schutz nicht. Liegen um 11:00 weniger als 12 Titel vor, macht mit diesen weiter und holt den Rest am Sonntag nach.
- [ ] **11:00 Text gewinnen und Register anlegen (2 Stunden, Planwert).** Text aus PDF oder EPUB, Seitenmarker `--- PAGE n ---` einsetzen, eine Registerzeile je Quelle ([Kapitel 5](05-einlesen-und-index.md)). Prüft je Buch drei Stichproben: Anfang, Mitte, Ende. Abbruch: Liefert ein Buch fast keinen Text, ist es ein Scan. Lest es per OCR ein, wenn mehr als 10 Prozent der Hauptteil-Seiten unter 20 Wörtern liegen. Bringt auch das nichts, stellt das Buch zurück, werft es nicht weg.
- [ ] **13:00 Pause.**
- [ ] **14:00 Index bauen (1 Stunde, Planwert).** Das Embedding braucht gerechnet rund 6 Minuten auf der RTX 3080. Baut in einen Build-Ordner. Abbruch: Zeigt das Manifest nicht `vollstaendig: true` oder stimmt die Chunkzahl nicht mit dem Erwarteten überein, stoppt, löscht den Build-Ordner und beginnt neu. Schaltet nichts um.
- [ ] **15:30 Kontextsätze erzeugen (optional).** Lokal mit dem 7B-Modell brauchen sie 206 bis 288 Minuten, in der Cloud 25 bis 90 Minuten je nach Drosselung (gerechnet aus 304 und 80 Chunks/min). In meinen Messungen brachten sie nur Tausendstel bis Hundertstel Gewinn. Entscheidet danach, ob ihr sie überhaupt braucht ([Kapitel 7](07-messen-und-verbessern.md)). Abbruch: Läuft es nach 30 Minuten noch nicht stabil, lasst die Kontextsätze weg und startet Sonntag ohne sie.
- [ ] **17:00 Stand sichern.** Quellen, Register, Prüffragen kopieren.

## Sonntag, 09:00 bis 13:00

- [ ] **09:00 An Claude anschließen (90 Minuten).** MCP-Server eintragen, Claude neu starten ([Kapitel 8](08-anschluss-claude-mcp.md)). Abbruch: Antwortet der Server nach 60 Minuten nicht, testet die Suche an der Kommandozeile. Findet sie dort Treffer, liegt der Fehler im Anschluss, nicht im Index.
- [ ] **10:30 Zehn Prüffragen stellen (90 Minuten).** Tragt je Frage ein, ob die erwartete Stelle unter den acht Treffern liegt. Meine Brains liegen zwischen 0,80 und 1,0 bei den acht Treffern. Abbruch: Liegen weniger als 8 von 10 richtig, stellt noch keine echte Frage. Prüft, ob Bücher fehlen ([Kapitel 3](03-quellen-finden.md), Lückenanalyse), und holt sie nach.
- [ ] **12:00 Erste echte Frage (60 Minuten).** Eine Frage aus eurem Alltag. Schlagt jede genannte Stelle auf. Abbruch: Kommt die Antwort ohne Buch und Seite, fehlt die Suchregel im Skill ([Kapitel 8](08-anschluss-claude-mcp.md)). Behebt das, bevor ihr weiterfragt.
- [ ] **13:00 Abschluss.** Notiert Datum, Chunkzahl und Trefferquote. Das ist euer Ausgangswert für alle späteren Änderungen.

## Was hier offen ist

- Die Zeiten für Beschaffen und Textgewinnung sind Planwerte, nicht gemessen. Keiner meiner Brains ist an einem Wochenende entstanden.
- Zehn Prüffragen sind statistisch wenig. Sie zeigen grobe Lücken, keine feinen Unterschiede. Mein größtes Prüfset hat 106 Einträge.
- Die Schwelle von 8 von 10 ist eine Orientierung an meinen Messungen, kein getesteter Grenzwert.
- Die Kontextsätze sind hier optional. Für das Geschichts-Brain sind sie Teil meiner Pipeline, einzeln messbar war ihr Nutzen nicht.
