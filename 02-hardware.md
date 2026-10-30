# 2. Hardware

Für ein Wochenend-Brain mit 20 Büchern reicht ein Laptop mit 8 GB Grafikspeicher. Ohne Grafikkarte geht es auch, dann fällt der Reranker weg und ihr verliert Treffer. Alle Zeiten unten sind auf meinen Rechnern gemessen, wo nicht "gerechnet" dabeisteht.

## Was die Grafikkarte wofür braucht

Ein Brain braucht Rechenleistung an drei Stellen. Nur beim Einlesen ist sie groß, die Suche selbst ist leicht.

1. **Embedding.** Jeder Textausschnitt wird in einen Zahlencode übersetzt (1.024 Zahlen, Fachwort Vektor), damit sich später nach Bedeutung suchen lässt. Ich nutze dafür das Modell Snowflake arctic-embed-l-v2.0. Auf einer RTX 3080 liefen mit halber Genauigkeit (fp16) 1.136 Chunks pro Minute statt 219 ohne.
2. **Reranker.** Ein zweites Modell (bge-reranker-v2-m3) liest die besten Kandidaten noch einmal und sortiert sie neu. Es braucht rund 1,7 GB Grafikspeicher. Auf der RTX 3080 kostet es 0,54 Sekunden je Frage, auf vier CPU-Kernen 127 Sekunden.
3. **Sprachmodell für Kontextsätze.** Zu jedem Ausschnitt schreibt ein Sprachmodell einen Satz, aus welchem Buch und Kapitel er stammt ([Kapitel 5](05-einlesen-und-index.md)). Lokal nutze ich Qwen 2.5 in 14B-Größe (Modell 9,0 GB, Spitze 13,5 GB Grafikspeicher). Alternativ läuft das in der Cloud.

Die Suche zur Laufzeit braucht unter 3 GB Grafikspeicher. Ein MCP-Server-Prozess belegt nach dem ersten Aufruf rund 3,5 GB, zwei Brains rund 7 GB.

## Die drei Stufen

| Stufe | Was geht | Was nicht | Richtpreis | Gemessene Zeiten |
|---|---|---|---|---|
| 1. Ohne Grafikkarte (Messrechner: 4 CPU-Kerne, 15 GB RAM) | Einlesen mit kleinem Embedding-Modell, Suche ohne Reranker, Kontextsätze aus der Cloud | Reranker (127 s je Frage), lokale Kontextsätze, Arctic-Bau in brauchbarer Zeit | Kein Zusatzgerät. Kontextsätze in der Cloud für 20 Bücher rund 6 USD (gerechnet) | Frage ohne Reranker 0,94 s, mit Reranker 127 s (Median). Kaltstart 59 bis 164 s. Embedding mit e5-small 641 Chunks/min |
| 2. Laptop, 8 GB Grafikspeicher (RTX 3080, 31,9 GB RAM) | Arctic-Embedding mit fp16, Reranker, MCP-Server, Kontextsätze mit dem 7B-Modell | Kontextsätze mit dem 14B-Modell (9 GB Modell passt nicht), lokale Antwortmodelle | Nicht ermittelt | Embedding 1.136 Chunks/min, Frage 0,54 s, Kaltstart rund 40 s, Kontextsätze 25 bis 35/min |
| 3. Stand-PC, 24 GB Grafikspeicher (RTX 4090, 63,7 GB RAM) | Alles: Vollbau, 14B-Kontextsätze, lokales Antwortmodell mit 27B | Antwortmodell 27B und MCP-Server gleichzeitig (19,6 GB plus 3 GB) | Grafikkarte 2.000 EUR, übriger PC nicht beziffert | Embedding 20.000 bis 21.000 Chunks/min, Vollbau von 402.871 Chunks rund 20 Min, Kontextsätze 74 bis 80/min |

Was das für 20 Bücher heißt (gerechnet): Ein Buch ergibt bei mir rund 360 Chunks, 20 Bücher also rund 7.200. Das Embedding dauert auf der RTX 3080 rund 6 Minuten. Die Kontextsätze mit dem 7B-Modell brauchen dort 206 bis 288 Minuten, auf der RTX 4090 rund 93 Minuten. Auf Stufe 1 habe ich Arctic nicht gemessen. Die Modelle bge-m3 und e5-large schafften auf vier CPU-Kernen 28,5 und 71,2 Chunks pro Minute. Für 7.200 Chunks sind das gerechnet rund 100 Minuten (e5-large) beziehungsweise rund vier Stunden (bge-m3).

Meine Empfehlung als Meinung, nicht als Messung: Kauft keine Grafikkarte, bevor ihr ein Thema eingelesen und die Prüffragen beantwortet habt. Die Karte war mein größter Einzelposten, und für ein erstes Brain braucht ihr sie nicht.

## Was ohne Grafikkarte verloren geht

Auf Stufe 1 läuft alles außer dem Reranker in unter einer Sekunde. Den Reranker schaltet ihr ab. Der Preis, gemessen an 60 Testfragen im Geschichts-Brain:

- Richtige Stelle auf Platz 1: unverändert bei 0,533.
- Richtige Stelle unter den ersten acht (hit@8): von 0,817 auf 0,700. Sieben von 60 Fragen fallen aus den Top 8.
- MRR (mittlerer Kehrwert des Rangs): von 0,6268 auf 0,5924.

Bei meinem Geld-und-Steuern-Brain und beim Psychologie-Brain ist es anders: Dort läuft der Reranker aus, weil die Messung ohne ihn besser war (MRR 0,814 gegen 0,736 und 0,945 gegen 0,857). Der Reranker ist also nicht immer ein Gewinn. Ihr messt es für euer Thema ([Kapitel 7](07-messen-und-verbessern.md)).

## Index-Größen

So groß sind meine acht Indizes (Ordner auf der Platte, gemessen am 30.10.2026):

| Brain | Chunks | Index auf der Platte |
|---|---|---|
| Geschichte | 402.871 | 1,7 GB |
| Psychologie | 203.744 | 904 MB |
| Geld und Steuern | 106.062 | 473 MB |
| Recht | 98.711 | 441 MB |
| Technik | 78.064 | 346 MB |
| Musik | 53.669 | 235 MB |
| Business | 45.252 | 206 MB |
| Familie | 43.341 | 200 MB |

Als Faustwert ergeben sich 4 bis 5 KB je Chunk (gerechnet). Euer 20-Bücher-Brain mit rund 7.200 Chunks wäre danach rund 30 MB groß.

## Arbeitsspeicher und Platte

Der Index liegt im Arbeitsspeicher, als float32 und ohne mmap. Gemessen am Geschichts-Brain mit 251.147 Chunks: 4,60 GB RAM nach der ersten Suche ohne Reranker, 7,00 GB mit. Davon sind rund 2,2 GB das Embedding-Modell, 1,03 GB die Vektoren, rund 1,2 GB Texte und Metadaten, rund 0,2 GB die Wortsuche. Bei einem kleinen Brain macht das Modell den Hauptteil aus. Für mein Business-Brain rechne ich rund 2,5 GB (gerechnet, nicht gemessen). 16 GB RAM genügen also für ein Brain, mein Messrechner mit 15 GB hat 7 GB mit Reranker geschafft.

Auf der Platte liegen Quellen, Index und Modelle. Dazu kommen Sicherungskopien des Index: Ich baue jeden neuen Index in einen eigenen Ordner und behalte den alten ([Kapitel 10](10-betrieb-kosten-datenschutz.md)). Bei mir liegen neun alte Stände des Geschichts-Index herum. Plant also mindestens das Doppelte des Index ein (Schätzung). Die Größe der Modelle im Cache habe ich nicht gemessen.

## Software

Aus meinem Rechner, Stand 30.10.2026:

- Python 3.13.13 am Stand-PC, Python 3.11 auf dem Laptop. Für Python 3.14 gab es zum Zeitpunkt meiner Anleitung keine Torch-Pakete.
- PyTorch 2.11.0 mit CUDA-12.8-Build (`+cu128`), sentence-transformers 6.0.0, transformers 5.16.1.
- Tesseract für Scans, Ollama für lokale Modelle.

Der häufigste Fehler ist ein Torch ohne CUDA. Pip zieht dann stillschweigend die CPU-Version, alles läuft, nur sehr viel langsamer. Prüft vor dem Einlesen:

```
python -c "import torch; print(torch.cuda.is_available())"
```

Kommt `False` und ihr habt eine NVIDIA-Karte, installiert Torch neu aus dem CUDA-Index.

## Cloud-Alternative

Statt eines eigenen Rechners lässt sich ein Brain auf einen gemieteten Server legen. Ich habe Lightsail-Preise von AWS notiert (Stand 09.2026): 4 GB RAM für 24 USD, 8 GB für 40 USD, 16 GB für 80 USD im Monat. Das sind CPU-Server, also Stufe 1 ohne Reranker. Mein Plan sah vor, den Reranker später als API zu mieten. Das ist ein Entwurf, ungemessen, und dabei gehen die Frage und 100 Passagen an den Anbieter.

Ein Haken gilt für jede Cloud: AWS unterliegt dem US CLOUD Act, auch in Frankfurt. Für ein Recht-Brain mit Mandantenunterlagen ist das ein Risiko. Bei vertraulichem Material lasst ihr den Server bei euch. Mehr dazu in [Kapitel 10](10-betrieb-kosten-datenschutz.md).

## Was hier offen ist

- Der Preis für Stufe 2 und der Preis für den übrigen PC der Stufe 3 sind nicht ermittelt. Beziffert habe ich nur die Grafikkarte (2.000 EUR).
- Embedding-Tempo widerspricht sich in meinen Unterlagen: 1.136 Chunks/min auf der RTX 3080 (Arctic, fp16), dagegen 5.200 in einer älteren Standmeldung, deren Modell unklar ist. Ich nutze den belegten Wert.
- Die Vollbau-Zeit auf dem Laptop steht mit 50 bis 70 Minuten (geschätzt) und mit 12 bis 17 Stunden in zwei Dokumenten. Ich habe sie nicht selbst gestoppt.
- Arctic auf CPU habe ich nicht gemessen, nur andere Modelle.
- Strom im Normalbetrieb habe ich nicht gemessen.
- Ob der Laptop eine mobile oder eine Desktop-3080 hat, weiß ich nicht.
