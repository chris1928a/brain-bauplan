# 06 Suche

Eine Frage durchläuft acht Stufen, und die meisten davon dienen dazu, dass das richtige Buch nicht von einem falschen verdrängt wird. Dieses Kapitel folgt dem Weg einer Frage durch meine Suchfunktion. Die Vorarbeit steht in [Kapitel 05](05-einlesen-und-index.md), die Messung der Wirkung in [Kapitel 07](07-messen-und-verbessern.md), den Anschluss an Claude in [Kapitel 08](08-anschluss-claude-mcp.md).

Alle acht Brains laufen mit demselben Code. Ein Brain unterscheidet sich nur durch Index-Ordner, Register und die Frage, ob der Reranker an ist.

## Stufe 1: Die Frage in zwei Sprachen

Claude übergibt dem Suchwerkzeug zwei Fassungen derselben Frage: `frage` in der Sprache des Nutzers und `frage_en` auf Englisch. Das ist keine Spielerei. Mein größter Bestand ist zu 92,7 Prozent englisch (nach Wörtern gezählt, nach Texten 79,5 Prozent). Eine deutsche Frage findet englische Texte über die Bedeutungssuche nur mäßig und über die Wortsuche gar nicht.

Die Messung dazu: Die Wortsuche (BM25, siehe Kapitel 05) traf mit deutscher Frage **0 von 15** erwarteten Fundstellen in den ersten zehn Treffern. Mit englischen Stichwörtern waren es **94 Prozent**.

Beide Fassungen werden eingebettet (mit dem Präfix `query: `), und je Chunk zählt die bessere der beiden Ähnlichkeiten. Fehlt `frage_en`, antwortet der Server mit einem `sprachhinweis`, damit Claude es nachholt.

## Stufe 2: Bedeutungssuche und Wortsuche

Zwei Verfahren laufen parallel.

- **Bedeutungssuche:** Die Frage wird in 1.024 Zahlen verwandelt (ein **Vektor**) und mit den Vektoren aller Chunks verglichen. Maß ist die Kosinus-Ähnlichkeit, ein Wert zwischen 0 und 1, der sagt, wie ähnlich zwei Bedeutungen sind. Das ist ein einfacher Vergleich gegen alle Chunks, kein Spezialindex. Bei 251.147 Chunks dauert das unter einer Sekunde. Bei geschätzt 2,5 Millionen Chunks wären es rund 5 Sekunden, dort lohnt ein Spezialindex.
- **Wortsuche:** BM25 über den Text mit Kontextsatz, wieder das Maximum über beide Sprachfassungen.

Die Bedeutungssuche versteht "Seeräuber" und "Piraten" als nah beieinander. Die Wortsuche findet dafür den seltenen Eigennamen, den die Bedeutungssuche verwischt. Keins von beiden reicht allein.

Ein dokumentierter Fehlerfall: Bei einer deutschen Frage an eine englische Quelle verschlechtert die Verbindung beider Verfahren den Rang. Im Beispiel lag der gesuchte Chunk bei der Bedeutungssuche allein auf Rang 873, nach der Verbindung auf Rang 1.693, weil 20.666 Chunks irgendeinen Wortbezug zur deutschen Frage hatten. Im Server gibt es dafür keinen Schalter, die englische Fassung ist die Abhilfe.

## Stufe 3: Verbinden mit RRF

Beide Ranglisten werden mit **Reciprocal Rank Fusion** (RRF) zusammengeführt. Die Formel ist einfach: Jeder Chunk bekommt von jeder Liste Punkte nach seinem Rang, und die Punkte werden addiert.

```
score = 1 / (60 + Rang_Bedeutung + 1)  +  1 / (60 + Rang_Wort + 1)    (zweiter Summand nur, wenn der BM25-Wert größer 0 ist)
```

Die 60 (`k0`) dämpft den Abstand zwischen den vorderen Rängen. Es gibt keine Gewichte und keine Normalisierung der Werte, deshalb muss man nichts einstellen.

## Stufe 4: Filter

Danach greifen die Filter des Aufrufers: Epoche (oder bei anderen Brains: Bereich), Typ, Autor, Quelle, Thema, optional nur Primärquellen. Der Vergleich läuft an **Wortgrenzen**. Ein Filter "Caesar" findet nicht mehr "Prokopios von Caesarea".

Reihenfolge ist wichtig: erst filtern, dann auf k abschneiden. Bis zum 13.08.2026 füllten ausgefilterte Chunks die Liste still wieder auf, ein Fehler, der nie gemeldet wurde. Wer nur den Filter prüft und nicht die Länge der Liste, übersieht so etwas.

Der **Beiwerk-Filter** (Literaturverzeichnisse, Register, Kapitel 05) ist standardmäßig an und blendet diese Chunks aus. Mit `beiwerk=false` ist er aus.

## Stufe 5: Reranker

Die Verbindung liefert eine gute, aber grobe Vorauswahl. Der **Reranker** sortiert sie genauer. Technisch ist er ein Cross-Encoder, das ist ein Modell, das Frage und Chunk gemeinsam liest und eine Passung bewertet, statt beide getrennt in Vektoren zu verwandeln. Das ist genauer und viel langsamer.

- **Modell:** `BAAI/bge-reranker-v2-m3`, Eingabelänge 512 Token.
- **Kandidaten:** die besten 100 aus der Verbindung (im Kommandozeilenwerkzeug 50).
- **Welche Frage:** Standard ist der Modus `en`, der Reranker bewertet nur gegen die englische Fassung. Den Modus `beide` habe ich getestet: 36 Prozent mehr Zeit (1,109 gegen 0,813 Sekunden je Frage) und drei Fälle fielen aus den ersten acht.
- **Kosten:** Das Modell braucht 2,4 GB Arbeitsspeicher und 1,7 GB Grafikspeicher. Auf einer RTX 3080 kostet es 0,54 Sekunden je Frage, auf vier CPU-Kernen **127 Sekunden** (Spanne 105 bis 271). Ohne Grafikkarte ist er unbrauchbar.
- **Ausfall:** Fällt der Reranker aus, bleibt die Reihenfolge der Verbindung. Die Suche liefert dann etwas schlechtere, aber gültige Treffer.

Nicht jedes Brain profitiert. Ich habe es pro Brain entschieden, wo ich messen konnte:

| Brain | Reranker | Messung | Fragen |
|---|---|---|---|
| Geschichte (CCG) | an | hit@8 0,700 ohne, 0,817 mit; MRR 0,5924 ohne, 0,6268 mit; hit@1 unverändert 0,533 | 60 |
| Finanzen (CFO) | aus | MRR 0,814 ohne, 0,736 mit (79 statt 80 Treffer) | 80 (21.09.2026) |
| Psychologie | aus | MRR 0,945 ohne, 0,857 mit (hit@8 mit Reranker 0,984) | 61 |
| Franz-Brain | aus | keine Messung gelesen, Begründung steht nur in der Konfiguration | 20 |
| Business, Technik, Recht, Familienrecht | an (Standard) | keine Messung an gegen aus gefunden | |

**hit@8** heißt: Die erwartete Quelle steht unter den ersten acht Treffern. **MRR** ist der Mittelwert aus 1 geteilt durch den Rang des ersten richtigen Treffers; ein Wert nahe 1 bedeutet, dass der richtige Treffer meist ganz oben steht.

Warum der Reranker bei Finanzen und Psychologie schadet und bei Geschichte hilft, weiß ich nicht. Gemessen ist nur das Ergebnis. Das CFO-Goldset ist inzwischen auf 95 Fragen gewachsen, die Zahlen gelten für den Stand mit 80.

## Stufe 6: Maluse, Boost und Deckel

Nach dem Reranker sortiert die Suche die Treffer nach Typ der Quelle um.

- **Maluse (Abzüge).** Eigene Texte (`type=eigen`) werden stabil ans Ende geschoben, nicht ausgeblendet. Anlass: Meine eigene Synthese zu einem Thema stand auf Rang 1 vor den Primärquellen. Dasselbe gilt für Zusammenfassungen (`type=zusammenfassung`), die bei einem Test bis zu 3 der ersten 3 Plätze belegten. Beide Abzüge ruhen, wenn ihr gezielt nach diesem Typ filtert. Zwei weitere Abzüge (für Impressum, Inhaltsverzeichnis und die ersten drei Chunks einer Quelle) habe ich gebaut und im Code standardmäßig ausgeschaltet, weil sie im Test den MRR drückten: 0,6098 mit Abzug, 0,6417 ohne, 0,6466 ohne beide Neuerungen. Meine Doku nennt sie noch "an", der Code sagt "aus".
- **Primärquellen-Boost.** Primärquellen und Fachbücher erhalten auf den Reranker-Wert einen Zuschlag (Faktor 1,5, also plus 0,5), aber nur innerhalb der ersten 16 Treffer und nur ohne Typ-Filter. Am 08.09.2026 hob das den Rang-1-Anteil von 54 auf 58 von 106 Prüfungen, Top 3 von 71 auf 76 und Top 8 von 85 auf 87. Über 1,5 fiel Rang 1 wieder. Der Boost wirkt nur, wenn die Typen im Register sauber vergeben sind: Vorher trug `primary-book` bei mir 505 Einträge, 390 davon Sekundärliteratur. Der Boost gilt für mein Geschichts-Brain, der Standard im Server ist 0 (aus).
- **Quellen-Deckel.** Höchstens 2 Treffer je Buch im Modus `fokus`, 1 im Modus `rack`. Das verhindert, dass ein einziges Buch alle acht Plätze füllt. Der Deckel entfällt, wenn ihr gezielt nach einer Quelle oder einem Autor fragt. Eine Ausgabe und ihre Zusammenfassung zählen als ein Buch.

## Stufe 7: Lücken-Feld und Werk-Durchgang

**Lücken-Feld.** Zwei Treffer derselben Quelle mit ein bis drei ungesehenen Chunks dazwischen deuten auf einen zerschnittenen Gedankengang. Die Antwort nennt dann im Feld `luecken` die Nummern der fehlenden Chunks, und Claude holt sie mit dem Werkzeug `stelle(nr)`. Das ist der Ersatz für den Overlap, den ich nicht gebaut habe.

**Werk-Durchgang.** Wer fragt, was ein bestimmter Autor in einem bestimmten Werk sagt, bekommt oft Sekundärliteratur statt der Stelle selbst, weil die Passage nicht unter den ersten 100 der Verbindung landet. Der Werk-Durchgang erkennt Autor oder Werk in der Frage, sucht ein zweites Mal gefiltert auf dieses Werk und flicht die besten Treffer in die Liste.

- Erkennung über eine Liste: 33 von Hand gepflegte Alias-Einträge und 618 aus dem Register abgeleitete Nachnamen, dazu eine Sperrliste mit über 500 Alltags- und Vornamen,damit gewöhnliche Namen nicht jede Frage auslösen.
- Die Frage wird "entkernt": Metawörter wie "beschreibt", "laut" oder "describes" fliegen raus.
- Pro erkanntem Werk kommen 3 Treffer (`CCG_WERK_K`), im Wechsel mit den freien Treffern. Ausgeschlossen sind Zusammenfassungen, eigene Texte, Transkripte und Notizen.
- Schutz vor Fehlauslösern: Liefert der Durchgang weniger als 2 Treffer oder liegt die Ähnlichkeit unter 0,30, wird er verworfen.
- Kosten: rund 4 Prozent mehr Reranker-Zeit. Die Gesamtzeit je Frage stieg über die ganze Umbaukette (Durchgang plus Maluse) von 0,81 auf 1,04 Sekunden.

Wirkung am Goldset von 60 Fragen: sieben Fragen besser, fünf um genau einen Rang schlechter, keine fiel aus den ersten acht, und alle acht Kontrollfragen lösten nicht aus. Drei weitere Schalter dieses Durchgangs habe ich gebaut, gemessen und ausgeschaltet gelassen, weil sie nichts brachten.

## Stufe 8: Modus rack und Ausgabe

Der Modus `fokus` ist der Normalfall: eine Frage, die besten acht Treffer. Der Modus `rack` dient Querverweisen über Epochen oder Bereiche hinweg. Er schaltet den Reranker ab, vergibt eine Quote je Epoche und nutzt statt einer festen Ähnlichkeitsgrenze ein Quantil (die besten 2 Prozent). Der Grund: Ähnlichkeitswerte hängen vom Modell ab. Bei einem älteren Modell lag der Mittelwert bei 0,089, bei einem anderen bei 0,805. Eine feste Grenze würde beim Wechsel brechen.

Die Antwort enthält je Treffer Nummer, Quelle, Seite, Ähnlichkeit und Score, dazu `luecken`, den Werk-Durchgang und ein Feld `konfiguration` mit Index-Stand und allen aktiven Schaltern. Das Feld steht seit 19.09.2026 in jeder Antwort, nachdem ein Eintrag in der Benutzerkonfiguration vier Wochen lang auf einen alten Index zeigte.

## Zeiten und was ohne Grafikkarte geht

Alles außer dem Reranker läuft unter einer Sekunde.

| Messung | Wert |
|---|---|
| Kaltstart des Servers, CPU (4 Kerne) | 164 s (andere Läufe 59 s) |
| Kaltstart, RTX 3080 | rund 40 s |
| Frage ohne Reranker, CPU | 0,94 s (0,90 bis 2,79 s) |
| Reranker allein, RTX 3080 | 0,54 s je Frage |
| Frage mit Reranker, 4 CPU-Kerne | 127 s |
| Arbeitsspeicher nach der ersten Suche | 4,60 GB ohne, 7,00 GB mit Reranker |

Der Kaltstart gilt, weil der Server das Modell und den Index erst beim ersten Aufruf lädt und nicht beim Start. Der Index liegt als float32 im Arbeitsspeicher, ohne Memory-Mapping.

**Ohne Grafikkarte** geht alles außer dem Reranker. Der Preis: Auf meinen 60 Geschichtsfragen blieb hit@1 bei 0,533, aber hit@3 fiel um 0,050 und hit@8 um 0,117. Sieben von 60 Fragen fielen aus den ersten acht. Neun Fragen wurden ohne Reranker besser, 15 schlechter, 36 blieben gleich. Für Brains, die ohnehin ohne Reranker laufen (Finanzen, Psychologie), ist eine Grafikkarte für die Suche nicht nötig. Was die Kontextsätze und das Einlesen brauchen, steht in [Kapitel 02](02-hardware.md).

Eine Rechnung, die ich nicht gemessen habe: Mit 8, 16 oder 32 Kernen würde der Reranker rund 70, 40 oder 25 Sekunden je Frage brauchen. Das bleibt zu langsam für den Alltag.

## Was hier offen ist

- Für Business-, Technik-, Recht- und Familienrecht-Brain habe ich keine Messung Reranker an gegen aus gefunden. Dass er dort läuft, ist ein Standardwert, kein Befund.
- Die Messwerte stammen aus Goldsets, die ich teils aus Treffern des eigenen Systems gebaut habe (siehe Kapitel 07). Ein getrenntes Prüfset gibt es nicht.
- Eine Erklärung, warum der Reranker bei Finanzen und Psychologie schadet, habe ich nicht.
- Die Skalierung auf 8 bis 32 CPU-Kerne ist gerechnet, nicht gemessen.
- Ob ein Spezialindex (statt Vergleich gegen alle Vektoren) bei meiner Größe nötig wird, ist offen.
