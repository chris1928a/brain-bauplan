# 10. Betrieb, Kosten, Datenschutz

Meine Bücher bleiben auf meiner Platte, je Frage gehen nur die Frage und acht Textstellen an Claude, und die Fixkosten für alle acht Brains lagen bei 2.700 Euro ohne meine eigene Zeit.

## Kosten

| Posten | Betrag | Anmerkung |
|---|---|---|
| Grafikkarte | 2.000 EUR | einmalig, nur Stufe 3 aus [Kapitel 2](02-hardware.md) |
| Claude-Abo | 600 EUR | drei Monate, also 200 EUR im Monat. Tarif nicht benannt |
| Cloud-Rechenzeit | 100 EUR | Aufschlüsselung nicht dokumentiert |
| Summe | 2.700 EUR | eigene Zeit nicht eingerechnet |

Nicht in den 2.700 Euro stecken die Bücher und der übrige PC. Bücher kosten bei mir rund 30 Euro je Titel (Rechnung aus einer Kaufliste mit 35 Titeln für rund 1.090 Euro). Die Spanne in den Listen liegt bei 15 bis 55 Euro je Titel, für 20 Titel also 300 bis 1.100 Euro. Freie Quellen kosten nichts ([Kapitel 4](04-quellen-beschaffen.md)).

Dazu die laufenden Posten beim Einlesen:

- Kontextsätze in der Cloud: rund 8 USD je 10.000 Chunks mit Haiku 4.5. Ein Buch hat bei mir rund 360 Chunks (gerechnet), 20 Bücher kosten also rund 5,80 USD. Im Vortrag nenne ich "rund 7 Dollar pro Einlesen".
- Kontextsätze lokal: 0 USD, dafür Zeit ([Kapitel 2](02-hardware.md)).
- Alle 277.000 Chunks eines großen Brains neu zu kontextualisieren, kostet rund 220 USD auf Abruf, rund 110 USD im Stapelbetrieb.
- Suche und Index zur Laufzeit: kostet kein Geld. Die Modelle laufen lokal.
- Strom: im Normalbetrieb nicht gemessen.

## Die Benchmark-Rechnung

Im Vortrag habe ich gerechnet, was dieselbe Arbeit bei Profis gekostet hätte. Pro Fachgebiet ein Fall der letzten drei Monate, bewertet mit dem Stundensatz des Profis, den ich sonst angerufen hätte:

| Profi | Fall | Satz EUR | Std. | Honorar EUR |
|---|---|---|---|---|
| Fachanwalt Bankrecht | Nachforderung der Bank | 300 | 8 | 2.400 |
| Fachanwalt Familienrecht | Erstberatung, Urteilslage | 250 | 4 | 1.000 |
| Steuerberater | Jahresabschluss, Gehalt, Liquidität | 200 | 10 | 2.000 |
| Vertriebsberater | Kundenarbeit gegen Literatur | 200 | 16 | 3.200 |
| Historiker | Faktencheck Podcast, 1.584 Aussagen | 80 | 100 | 8.000 |
| Psychologe, Recherche | Dossier, 250 Quellen | 100 | 40 | 4.000 |
| KI-Entwickler | Die Suche bauen und messen | 150 | 80 | 12.000 |
| Musikproduzent | Mix-Coaching, Reaper | 100 | 10 | 1.000 |
| Summe | | | 268 | 33.600 |

Das sind 268 Stunden, gut sieben Arbeitswochen, und 33.600 Euro, im Vortrag gerundet auf 34.000. Gegen 2.700 Euro Kosten ergibt das den Faktor 12 (33.600 geteilt durch 2.700 sind 12,4). Der Durchschnitt liegt bei 125 Euro je Stunde.

### Die Schwächen der Rechnung

Ich rechne euch das nicht schön. Fünf Punkte:

1. **Zwei Posten machen 60 Prozent aus.** Historiker (8.000) und KI-Entwickler (12.000) ergeben 20.000 von 33.600 Euro.
2. **Der KI-Entwickler ist Bauarbeit.** Die 12.000 Euro bewerten, was es kostete, das System zu bauen und zu messen. Das ist kein Nutzen aus Fachfragen. Ohne diesen Posten bleiben 21.600 Euro, der Faktor sinkt gerechnet auf rund 8.
3. **Die Stundensätze sind Schätzungen**, marktüblich in Deutschland, und die Stunden sind meine Annahme, was ein Profi für dasselbe Ergebnis braucht. Einen Beleg außerhalb von mir und dem Modell gibt es nicht.
4. **Die Qualität ist nicht gleichgesetzt.** Die Rechnung nimmt an, dass die Arbeit mit dem Brain das Ergebnis des Profis ersetzt. Ein Anwalt haftet für seine Auskunft, die KI nicht. Besser ist die Lesart, dass ich Arbeit vorbereitet habe, die ein Profi dann prüft.
5. **Der Bankfall ist ein Einzelfall** mit laufender Verhandlung. Der Ausgang ist offen.

Und die 2.700 Euro enthalten weder Bücher noch den übrigen PC noch meine Zeit. Wer es nachrechnen will, ersetzt meine Sätze durch seine.

## Datenschutz: was den Rechner verlässt

**Bleibt auf der Platte:** die Bücher, der Index, die Kontextsatz-Datei. Es gibt keine Datenbank in der Cloud. Embedding, Reranker und Suche laufen lokal.

**Geht raus, bei jeder Frage:** die Frage und die acht gefundenen Textstellen, an Claude. Das ist keine Kleinigkeit. Wenn in den acht Stellen vertrauliche Inhalte stehen, haben sie den Rechner verlassen. Prüft die Datenschutzeinstellungen eures Claude-Tarifs. Das habe ich hier nicht bewertet.

**Geht raus, beim Einlesen mit Cloud-Kontextsätzen:** der Text jedes Chunks, bei mir an AWS Bedrock in der Region us-east-1. Für Fachbücher ist das mein Weg. Bei vertraulichem Material nutzt ihr das lokale Modell. In meinem Vergleich von 300 Chunks erreichte Qwen 2.5 14B lokal 106,6 Prozent der Haiku-Punkte, bewertet mit einer Regel-Heuristik, nicht von Menschen.

**Für maximale Abschottung** gibt es lokale Antwortmodelle, bei mir Qwen 3.6 mit 27B auf der RTX 4090 mit einer Netzsperre. Ihre Qualität lag in meinem Test bei 4,3 von 5 gegen Opus 4.7 und Sonnet 4.6, und bei Lücken im Treffer erfinden lokale Modelle Zuschreibungen.

**Nie in ein Repo oder auf ein geteiltes Laufwerk:** geschützter Volltext, Index, Kontextsatz-Dateien. Der Index enthält den vollen Text der Bücher. Aus einem früheren Fehler weiß ich außerdem, dass Index-Dateien Git aufblähen: Die Historie meines Repos lag bei 4,2 GB, GitHub lehnt Dateien über 100 MiB ab. Der Index liegt deshalb außerhalb von Git.

## Betrieb

- **Backups.** Sichert Originaldateien, Register und Prüffragen. Den Index könnt ihr neu bauen. Die Kontextsatz-Datei ist teuer: Für mein Geschichts-Brain brauchte sie rund 130 Stunden Textgenerierung. Sie liegt als gepackte Kopie an einem zweiten Ort.
- **Index nie direkt in current bauen.** Baut in einen Build-Ordner, prüft, schaltet erst dann um und behaltet den alten Stand ([Kapitel 5](05-einlesen-und-index.md)). Während eines Baus schreibt das Programm alle fünf Minuten einen unvollständigen Stand.
- **Nur ein Build gleichzeitig.**
- **Neustart nach jedem Umschalten.** Laufende Server halten den alten Index im Arbeitsspeicher. Jede Antwort nennt den Stand des Index. Das habe ich eingebaut, nachdem eine Konfiguration vier Wochen auf einen alten Index zeigte.
- **Ein Modellwechsel heißt Neubau von null.** Der Wiederverwendungs-Hash greift dann nicht. Ein falsches Kommando mit dem alten Modell hat mir einmal 245.000 Chunks in einen unbrauchbaren Index verwandelt.
- **Konfiguration an einer Stelle.** Ein Schalterwert stand nur in der Programm-Konfiguration, nicht in meiner zentralen Datei. Ein Schreibvorgang aus der Zentraldatei hätte ihn gelöscht.
- **Nach jeder Änderung messen.** [Kapitel 7](07-messen-und-verbessern.md).

## Was hier offen ist

- Die Abo-Stufe hinter den 600 Euro ist nicht benannt. Bücher und übriger PC sind in den 2.700 Euro nicht enthalten.
- Strom im Normalbetrieb ist nicht gemessen. Der Plan für Dauerbetrieb nennt 15 bis 25 Euro, ohne Zeitraum, als Entwurf.
- Die Stundensätze der Benchmark sind Schätzungen. Es gibt keinen Beleg von außen.
- Ob mein Vorgehen bei Datenschutz und Berufsrecht für Mandantendaten reicht, habe ich nicht rechtlich geprüft. Das ist kein Rechtsrat.
- Der Qwen-Haiku-Vergleich bewertet mit einer Heuristik. Die Suchqualität habe ich damit nicht verglichen.
- Die lokalen Antwortmodelle habe ich nur an einem Benchmark mit 24 Fragen gemessen.
