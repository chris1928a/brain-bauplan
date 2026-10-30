# 05 Einlesen und Index

Aus Büchern wird ein durchsuchbarer Index in acht Schritten, und fast jeder Schritt hat bei mir schon einmal still etwas kaputt gemacht. Dieses Kapitel beschreibt die Schritte mit allen Parametern und die Fehler, die ich dabei gemacht habe. Davor steht die [Quellenarbeit](04-quellen-beschaffen.md), danach die [Suche](06-suche.md).

Vorab drei Begriffe. Ein **Chunk** ist ein Textstück von rund einer Seite, in das ich jedes Buch zerlege. Ein **Embedding** ist eine Liste aus 1.024 Zahlen, die die Bedeutung eines Chunks beschreibt. Ein **Index** ist die fertige Sammlung aus Chunks, Embeddings und Wortlisten, in der gesucht wird.

## Schritt 1: Text aus der Quelle holen

Aus jeder Quelle muss reiner Text mit **Seitenmarkern** werden. Ohne Marker kennt die Suche später die Seitenzahl nicht, und die Seitenzahl ist der Beleg.

- **PDF:** Das Programm PyMuPDF liest je Seite den Text. Trennstriche am Zeilenende vor einem Kleinbuchstaben werden zusammengezogen ("Verfah-" und "ren" wird "Verfahren"). Vor jede Seite kommt eine Zeile `--- PAGE n ---`.
- **EPUB:** Calibre (`ebook-convert`) macht daraus erst Text, dann gilt dasselbe. Ein EPUB hat keine festen Seiten. Die Marker folgen dann der Aufteilung der Datei, und die Seitenzahl im Treffer entspricht nicht der Druckausgabe.
- **Scan ohne Textebene:** Das ist ein Bild vom Buch, und der Text muss per OCR (Texterkennung) herausgelesen werden. Ich nehme Tesseract. Jede Seite wird auf 300 dpi gerendert, deutsche Bücher brauchen das Sprachpaket `deu`, Fraktur das Modell `deu_latf`. Fehlt das deutsche Paket, erkennt Tesseract mit `eng`, und ich markiere die Quelle als unsicher.
- **Wann komplett OCR:** Hat ein Buch gar keine Textebene oder liegen mehr als 10 Prozent der Hauptteil-Seiten unter 20 Wörtern, lese ich das ganze Buch per OCR. Einzelne leere Seiten lese ich nach. Drei Stichproben aus der Kapitelmitte gehören in den Bericht, denn OCR-Fehler fallen sonst nicht auf.

Was schiefgehen kann: PDF-Schriften liefern manchmal Sonderzeichen aus einem Unicode-Bereich (U+F720 bis F77E und F7A0 bis F7FF) statt normaler Ziffern. Bei mir verloren 1.915 von 179.709 Chunks dadurch alle Jahreszahlen. Mein Korpus-Skript ersetzt diese Zeichen jetzt. Ähnlich: Ein Trennstrich kam als unsichtbares Ersatzzeichen mitten im Wort an, an über 1.100 Stellen, und die Wortsuche kannte "Napoleon" nicht mehr. Prüft den Text vor dem Bau auf Zeichen oberhalb von U+2000.

Regel dazu: Nichts aussortieren. Jede gelieferte Quelle kommt rein, notfalls per OCR. Gefiltert wird später bei der Suche, nicht beim Einlesen.

## Schritt 2: Register und Korpus

Das **Register** ist die Datei `registry.jsonl`, eine Zeile je Quelle mit `id`, Titel, Autor, Typ, Thema und Herkunft. Sie ist die Wahrheit über euren Bestand. Aufbau und Typ-Regeln stehen in [Kapitel 03](03-quellen-finden.md).

Ein Skript (`build_corpus`) macht aus Register und Textdateien den **Korpus**, eine Markdown-Datei je Quelle mit Kopfzeilen für Titel, Epoche, Thema, Autor und Typ. Die Seitenmarker werden dabei zu `@@S<n>@@`, damit der Chunker sie später sicher findet. Quellen unter 50 Wörtern werden übersprungen.

Der Korpus ist ein Zwischenprodukt. Er gehört nicht in Git und lässt sich jederzeit neu erzeugen.

Was schiefgehen kann:

1. **Quellen fehlen unbemerkt.** Am 12.08.2026 liefen 286 von 454 Registerquellen nicht in den Index, und niemand sah es. Mein Skript bricht deshalb hart ab, wenn eine Registerquelle keine Datei hat. Nur mit `KORPUS_TOLERANT=1` läuft es trotzdem.
2. **Zwei Titel, ein Dateiname.** Dateinamen werden bei 80 Zeichen gekürzt. Zwei Titel mit gleichem Anfang überschrieben sich, 110 Titel und rund 36.000 Chunks gingen verloren. Seitdem zählt das Skript einen Suffix hoch.
3. **Frischer Rechner, leerer Korpus.** Ohne neu erzeugten Korpusordner meldet die Volltextsuche "kein Treffer", obwohl die Quelle im Register steht.

Drei Zustände einer Quelle sind verschieden: im Register, als Datei vorhanden, im Index. Keiner folgt aus dem anderen.

## Schritt 3: In Chunks zerschneiden

Der Chunker schneidet an Absätzen (Leerzeilen). Er packt Absätze zusammen, bis **480 Token** erreicht sind. Ein **Token** ist die Einheit, in der das Embedding-Modell Text zählt, im Mittel 1,853 Token je Wort bei meinem Bestand. 480 Token sind also rund 260 Wörter. Mein älteres Handbuch nennt "rund 270 Wörter", beide Angaben meinen dasselbe. Die 480 lassen Platz unter der Grenze von 512 Token, die das Modell verarbeiten kann.

Warum nach Token und nicht nach Wörtern: Mit einem festen Schnitt bei 350 Wörtern lagen 40,7 Prozent aller Chunks über dem Limit, bei deutschen Texten 75,3 Prozent. Was über dem Limit liegt, schneidet das Modell stumm ab.

Weitere Parameter:

- Absätze über 480 Token werden an der Stelle des 480. Tokens geteilt. In 65,4 Prozent meiner Korpusdateien liegt mehr als die Hälfte des Textes in Blöcken über 350 Wörtern, ohne diese Regel wäre das ein Massenproblem.
- **Kein Overlap.** Nur als Sicherheitsnetz teilt der Chunker einen zu großen Chunk mit 100 Token Überlapp. Ein generelles Überlappen von 15 Prozent habe ich nicht gebaut: Es heilt zwar 79,0 Prozent der 32.907 zerschnittenen Sätze, aber ob das echte Fragen verbessert, habe ich nicht gemessen. Stattdessen holt das Werkzeug `stelle` zur Suchzeit die Nachbarstücke (siehe [Kapitel 06](06-suche.md)).
- Chunks unter 20 Wörtern fallen weg.
- Je Chunk speichere ich `seite_von`, `seite_bis`, `position`, die erkannte Sprache und die Quelle. `seite_bis` war anfangs bei 49,5 Prozent von 5.934 Chunks um eins zu hoch, nach dem Fix bei 0,1 Prozent.

**Der Tokenizer-Rückfall:** Der Chunker braucht den Tokenizer des Embedding-Modells, also das Programm, das Text in Token zerlegt. Wird er nicht geladen, fällt der Chunker still auf 350 Wörter zurück. Am 12.08.2026 zeigte ein Probelauf deshalb 128.182 statt 145.261 Chunks. Wenn die Chunkzahl im Probelauf auffällig niedrig ist, liegt es meistens daran.

## Schritt 4: Kontextsatz je Chunk

Ein Chunk, der mitten aus einem Kapitel stammt, weiß nicht, aus welchem Buch er kommt. Ein **Kontextsatz** löst das: ein bis zwei Sätze, die der Chunk vorangestellt bekommt, etwa "This passage from "Titel" by Autor discusses ...". Die Methode heißt Contextual Retrieval und stammt von Anthropic (2024).

Ein Sprachmodell schreibt diese Sätze. Eingabe sind Titel, Autor, Themen, Typ und die ersten 2.000 Zeichen des Chunks. Kapitelüberschriften oder Nachbartext gebe ich nicht mit, das ist der größte offene Hebel.

Der Systemprompt, wörtlich aus dem Skript (im Code stehen bewusst ae, oe, ue statt Umlaute, ich habe es nicht geändert):

```
Du erzeugst kurze Kontextsaetze fuer Textausschnitte (Chunks) aus einem Archiv wissenschaftlicher und historischer Quellen (Contextual Retrieval). Du bekommst mehrere nummerierte Chunks in einer Anfrage. Antworte NUR mit einer nummerierten Liste, eine Zeile je Chunk, exakt im Format 'N) <Kontextsatz>' (N = die Nummer aus der Anfrage), keine Einleitung, kein Nachwort, keine Leerzeilen dazwischen.

Jeder Kontextsatz: ein bis zwei Saetze, die den Chunk in seiner Quelle einordnen, was fuer ein Werk, ggf. Autor, welches Thema/Kapitel der Ausschnitt behandelt. Stil wie: "This passage from \"<Titel>\" by <Autor> discusses/describes ...". Schreib in der Sprache des jeweiligen Chunk-Texts (meist Deutsch oder Englisch).
```

Für ein rein deutsches Brain hängt eine Variable (`KONTEXT_SPRACHE=de`) diese Anweisung an: "Antworte ausschliesslich auf Deutsch, unabhaengig von der Sprache des Chunk-Texts. Ein Satz, keine Einleitung." Bei meinem Rechts-Brain war das nötig, weil englische Kontextsätze zu deutschen Gesetzestexten die Suche auseinanderzogen. Gemessen am Goldset (siehe [Kapitel 07](07-messen-und-verbessern.md)) änderte sich dadurch bei keiner der 20 Fragen ein Rang.

**Welches Modell:** Standard ist Qwen 2.5 14B (4-Bit-Variante `q4_K_M`), lokal über das Programm Ollama. Alternative in der Cloud: Claude Haiku 4.5 über AWS Bedrock (Region us-east-1). Ich habe beide an 300 Chunks verglichen, bewertet mit einer Regel-Heuristik, nicht von Menschen: Qwen kam auf 106,6 Prozent von Haikus Punktzahl und erfand seltener Buchtitel. Die Suchqualität habe ich dabei nicht verglichen.

**Parameter:** 24 Chunks je Aufruf (`KONTEXT_BATCH`), 4 Worker, Temperatur 0, Kontextfenster 16.384 Token, bis zu 12 Versuche je Aufruf. `OLLAMA_NUM_PARALLEL=4`, nie 8. Das Ergebnis landet in `kontexte_map.jsonl`, Zeilen der Form `{"hash": ..., "kontext": ...}`. Der Hash ist die SHA-256-Prüfsumme des Chunk-Textes. Die Zuordnung läuft über den Hash und nicht über die Position, damit ein Umsortieren nichts zerstört. Das Skript arbeitet im Delta-Modus: Es erzeugt nur Sätze für Chunks ohne Eintrag.

**Cloud oder lokal:** In der Cloud verlässt der Chunk-Text den Rechner. Bei vertraulichem Material daher lokal.

Ehrlich zum Nutzen: In meinen Messungen bei drei Brains lagen die Unterschiede mit und ohne Kontextsätze im Bereich weniger Tausendstel bis Hundertstel. Für das Geschichts-Brain steht eine Verbesserung in der Doku, aber zusammen mit einem Modellwechsel, sie lässt sich nicht einzeln zurechnen. Ob ihr den Schritt wollt, ist offen (siehe unten).

## Schritt 5: Embedding

Das Embedding-Modell ist `Snowflake/snowflake-arctic-embed-l-v2.0`, 1.024 Dimensionen, bei allen meinen acht Brains gleich. Es läuft über die Bibliothek sentence-transformers.

- Fragen bekommen den Präfix `query: ` (Umgebungsvariable `QUERY_PREFIX`), Chunks keinen (`PASSAGE_PREFIX` leer). Falsche Präfixe verschlechtern den Index, ohne dass ein Fehler erscheint.
- Der Chunk wird mit vorangestelltem Kontextsatz eingebettet. Gespeichert und angezeigt wird weiter der Originaltext.
- `MODELL_BATCH=64` (Chunks je Rechenschritt, Standard im Code 32). Auf vier CPU-Kernen war 32 der Bestwert mit 641 Chunks/min, 16 brachte 407, 64 brachte 458.
- Auf der Grafikkarte läuft das Modell in halber Genauigkeit (fp16). Auf einer RTX 3080 waren das 1.136 statt 219 Chunks pro Minute bei einer Abweichung von 0,001 in der Ähnlichkeit. Abschalten mit `MODELL_FP16=0`.
- Die Vektoren liegen als float16 auf der Platte und werden beim Laden zu float32 (doppelter Speicher).
- **Inkrementell:** Ein Chunk wird nicht neu berechnet, wenn der SHA-256-Hash über Kontextsatz plus Text derselbe ist wie beim letzten Bau. Eine neue Quelle kostet nur ihre eigenen Chunks. `EMBED_BATCH=8192` steuert nur, wie oft zwischengespeichert wird.
- Ein Modellwechsel erzwingt den Neubau von null.

Zwei Fehler dazu aus meinem Alltag:

1. **Pflichtvariable für die Kontextsatz-Datei.** Beim Bau muss `KONTEXT_DATEI` auf `kontexte_map.jsonl` zeigen. Fehlt sie, ändert sich für jeden Chunk der Hash, der Bau hält alles für neu und rechnet alles ohne Kontextsätze neu. Am 01.09.2026 dauerte so ein Lauf 12 Minuten, statt rund 247.000 Chunks wiederzuverwenden. Kontrolle: Die Zeile "N Chunks total, R wiederverwendet, M zu embedden" muss nach zwei bis drei Minuten zeigen, dass R nahe an der alten Chunkzahl liegt.
2. **Fehlbuild mit falschem Modell.** Am 31.08.2026 lief ein Bau mit einem veralteten Befehl und dem kleinen Modell `multilingual-e5-small` (384 Dimensionen). Ergebnis: ein kompletter Index mit 245.000 Chunks, den der Server wegen der falschen Dimension ablehnte. Der Server prüft seither `manifest.json` und meldet Klartext, wenn Modell oder Dimension nicht passen.

## Schritt 6: Wortsuche (BM25)

Neben der Bedeutungssuche gibt es die Suche nach Wörtern. **BM25** ist ein altes, bewährtes Verfahren, das Chunks nach Häufigkeit und Seltenheit der Suchwörter bewertet. Ich habe es selbst geschrieben, ohne Bibliothek: Wörter per `\w+` in Kleinbuchstaben, keine Stoppwörter, keine Wortstämme, `k1 = 1,5`, `b = 0,75`. Indexiert wird der Text mit Kontextsatz.

Die Wortstatistik wird einmal gebaut und gespeichert (`bm25.npz`, `bm25_meta.npz`). Ein Neuaufbau je Frage hätte 5,2 bis 6,9 Sekunden gekostet, geladen sind es 0,15 Millisekunden.

## Schritt 7: Beiwerk-Flag und Zusammenfassungen

**Beiwerk** sind Literaturverzeichnisse, Register, Inhaltsverzeichnisse und Zahlenkolonnen. Beim Speichern berechnet ein Klassifikator je Chunk ein Ja oder Nein (`beiwerk.npy`), die Suche kann diese Chunks ausblenden. Die erste Version hatte gegen 600 blind gelabelte Chunks 60,3 Prozent Präzision, sie blendete also viel Nutzbares aus. Die zweite Version kommt auf 91,0 Prozent Präzision bei 91,0 Prozent Recall. Gelabelt haben Sprachmodelle. Bei meinem Finanz-Brain schalte ich den Filter ab, weil er dort Summen- und Saldenlisten blendete, 23 Prozent der eigenen Unterlagen.

**Zusammenfassungen (Ebene 2):** Je Quelle schreibt ein Sprachmodell Zusammenfassungen und legt sie als eigene Registerzeilen mit `type=zusammenfassung` an, Titel mit dem Zusatz "(Ebene-2)". Das Rezept: Abschnitte von rund 5.000 Wörtern entlang der Seitenmarker, je Abschnitt 5 bis 8 Sätze, bei mehreren Abschnitten vorneweg eine Werk-Zusammenfassung mit 6 bis 10 Sätzen. Quellen unter 1.500 Wörtern bekommen keine. Sie helfen bei Überblicksfragen und werden in der Suche bewusst nach hinten sortiert ([Kapitel 06](06-suche.md)).

## Schritt 8: Index-Format, Deckung, Umschalten

### Dateien im Indexordner

- `vectors.NN.npy`: die Embeddings, in Scherben geteilt.
- `chunks.NN.jsonl`: Text und Metadaten der Chunks im Klartext. Der geschützte Volltext liegt also im Index, deshalb gehört der Index nie in Git oder ein geteiltes Laufwerk.
- `bm25.npz` und `bm25_meta.npz`: die fertige Wortstatistik.
- `beiwerk.npy`: das Beiwerk-Flag je Chunk.
- `manifest.json`: Modell, Dimension, Token-Grenze, Chunkzahl, `vollstaendig` (ja oder nein) und Bauzeit.
- `deckung.json`: der Stand der Deckungsprüfung.

Die Zuordnung der Quellen zu den Scherben läuft über `sha1(quelle_id) % 32`, also 32 feste Scherben. Eine Quelle landet immer in derselben Scherbe, deshalb ändert ein Ingest nur wenige Dateien.

### Build-Ordner, dann umschalten

Der laufende Index heißt `current`. **Gebaut wird nie direkt dort, sondern in einem eigenen Build-Ordner, danach wird umgeschaltet.** Begründung: Das Speichern löscht alte Scherben im Zielordner, und alle fünf Minuten steht dort `vollstaendig: false`. Ein Server, der in dieser Zeit lädt, bekäme einen halben Index.

Ablauf:

1. Nur ein Bau gleichzeitig. Prüft vorher, dass kein Bauprozess läuft.
2. Den Ordner `current` in `build-<datum>` kopieren, damit der Hash-Abgleich den alten Stand findet.
3. Bau mit den Pflichtvariablen: `EMBED_MODEL`, `PASSAGE_PREFIX=`, `QUERY_PREFIX='query: '`, `MODELL_BATCH=64`, `EMBED_BATCH=8192`, `KONTEXT_DATEI`.
4. Kontrollzeile nach zwei bis drei Minuten: "wiederverwendet" muss der alten Chunkzahl entsprechen.
5. Kontextsätze für die neuen Chunks erzeugen, danach ein zweiter Bau in denselben Ordner. Zwei Bauläufe je Ingest sind kein Umweg: Kontextsätze lassen sich erst erzeugen, wenn die Chunks existieren, und die Chunks müssen danach mit Satz neu eingebettet werden.
6. Deckung setzen (unten).
7. Prüfen: `vollstaendig: true`, erwartete Chunkzahl, eine Stichprobe gegen den Build-Ordner.
8. `current` in `current-alt-<datum>` umbenennen, den Build nach `current`. Laufende Server halten den alten Index im Arbeitsspeicher, startet sie neu.

### Deckung als Werkzeug

Das Werkzeug `deckung` vergleicht das Register mit dem Index. Es meldet die Titeldeckung (wie viele Registerzeilen mindestens einen Chunk haben), die Wortdeckung (wie viel Textmasse wirklich drin ist, die ehrlichere Zahl, weil ein fehlendes dickes Buch die Titelquote kaum, die Wortquote aber stark senkt) und die Chunks je Bereich. Ein Bereich mit null Chunks ist ein harter Fehler.

Es gibt keine feste Schwelle, sondern eine **Ratsche**: Der erreichte Stand steht in `deckung.json` und ist die Untergrenze. Ein Lauf darf ihn heben, nie senken. Nach jedem Bau mit `--setzen` neu eintragen, sonst zeigt das Werkzeug alte Zahlen.

Der Anlass für die Ratsche war das Audit vom 12.08.2026: Der Index kannte 171 von 454 Registerzeilen (37,7 Prozent der Titel, 32,0 Prozent der Wörter). Die Wikingerzeit hatte 32 Titel im Register und null Chunks im Index. Ein verwandter Fehler: Deckung und Kontextsatz-Skript lasen einmal einen alten Index-Ordner und meldeten Fehlalarme ("zu generieren: 0" bei 594 offenen Chunks). Die gemeldete Chunkzahl muss immer zum Manifest passen.

## Durchsatz je Hardware

Die Zahlen stammen aus verschiedenen Tagen, Modellen und Chunklängen. Sie widersprechen sich zum Teil, die Spalte "Hinweis" sagt wo.

| Schritt | Hardware | Wert | Hinweis |
|---|---|---|---|
| Embedding | RTX 4090 (24 GB) | rund 20.000 bis 21.000 Chunks/min, 250.000 Chunks in 12 Minuten | Betriebswert Stand-PC |
| Embedding | RTX 3080 (8 GB), Arctic, fp16 | 1.136 Chunks/min | Messung 20.08.2026 |
| Embedding | RTX 3080 | rund 5.200 Chunks/min | Standmeldung 13.08., Modell unklar, widerspricht der Zeile darüber |
| Embedding | 4 CPU-Kerne, e5-small | 641 Chunks/min bei Batch 32 | kleineres Modell, nicht Arctic |
| Embedding | Cloud-Modell Titan | netto 17 Chunks/min | Altwert, nicht mehr im Einsatz |
| Vollbau 402.871 Chunks | RTX 3080 | 50 bis 70 Minuten | geschätzt aus 40 Prozent der 4090-Rate, passt nicht zu 1.136/min |
| Kontextsätze | 4090, Qwen 2.5 14B | 74 bis 80 Chunks/min, 13,5 GB VRAM | Modell 9,0 GB |
| Kontextsätze | Laptop 3080, Qwen 2.5 7B | 25 bis 35 Sätze/min | 14B passt nicht in 8 GB |
| Kontextsätze | Haiku 4.5, Bedrock, Batch 24 | 304 Chunks/min | rund 7 US-Dollar für 8.418 Sätze |
| Kontextsätze | Haiku, Einzelaufrufe | 12 bis 17 Chunks/min | Drosselung je Anfrage |

Ältere Angaben aus meinem ersten Handbuch: rund 150 Kontextsätze pro Minute, nach rund 500 Chunks gedrosselt auf 80 bis 90 (damals Batch 8). Ein Vollbau dauert laut Bedienungsanleitung rund 25 Minuten, sechs neue Quellen rund drei. Die Kontextsätze für das ganze Geschichts-Brain (402.871 Chunks) kosten rund 130 Stunden Textgenerierung.

Gerechnet aus der Tabelle: 20.000 Chunks sind auf der 4090 in rund einer Minute eingebettet, die Kontextsätze dafür brauchen bei Qwen 14B rund vier Stunden. Teuer sind die Kontextsätze, nicht das Embedding.

## Was hier offen ist

- Die Durchsatzzahlen für die RTX 3080 widersprechen sich (1.136 gegen rund 5.200 Chunks/min). Ich habe sie nicht abgeglichen.
- Ob Kontextsätze die Suche messbar verbessern, ist nicht belegt. Ich führe sie als optionalen Schritt.
- Der Klassifikator für Beiwerk wurde mit Labels von Sprachmodellen getuned, nicht von Menschen. 18 von 600 Labels bleiben falsch.
- Den Embedding-Vergleich vom 20.08.2026 finde ich nicht mehr. Belegt ist nur Arctic gegen Qwen3-Embedding-0.6B auf 25 Fragen: hit@8 0,88 gegen 0,80.
- Wie stark die Seitenzahlen bei EPUB abweichen, habe ich nicht gemessen.
