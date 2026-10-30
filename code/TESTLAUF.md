# Testlauf

Datum: 30.10.2026. Rechner: Windows 11, nur CPU (kein CUDA im Test). Frische Umgebung unter `code/.venv`.

## Umgebung

Python 3.11.9. Pakete (aus `pip list`): torch 2.15.0+cpu, sentence-transformers 6.0.0, transformers 5.22.1, tokenizers 0.23.3, numpy 2.4.6, pymupdf 1.28.2, mcp 1.30.0. Torch ließ sich als CPU-Variante installieren. Die Installation von `requirements.txt` brach beim ersten Versuch mit einer Dateisperre ab (WinError 32, wohl ein Virenscanner oder ein paralleler pip-Lauf) und lief beim zweiten Versuch durch.

Das Embedding-Modell (Snowflake arctic-embed-l-v2.0) lag schon im Modell-Cache des Rechners. Die Downloadzeit ist deshalb nicht gemessen.

## 1. Beispielindex bauen

```
python build_index.py beispiel
kant-aufklaerung: 12 Chunks
kleist-verfertigung: 10 Chunks
22 Chunks, davon 22 neu einzubetten, 0 wiederverwendet.
Fertig in 25 s
```

Index: 22 Chunks, 1024 Dimensionen, token_cap 480. Beispieltexte: Kant 2.625 Wörter, Kleist 2.107 Wörter.

Inkrementeller Zweitlauf ohne Änderung: `0 neu einzubetten, 22 wiederverwendet`, 5 s. Der alte Stand blieb als `build-vorher-...` liegen, der neue Build wurde zu `current`.

PDF-Pfad (Probe-PDF mit zwei Seiten, eigener Zielordner): 1 Chunk, `seite_von` 1, `seite_bis` 2, Registerzeile mit Titel `unbekannt - probe`. Seitenmarker und Register funktionieren.

## 2. Suche

```
python suche.py "Was versteht Kant unter Unmündigkeit?" --en "What does Kant mean by immaturity?" -k 4
[10] Immanuel Kant 1784 - Beantwortung der Frage: Was ist Aufklärung?, S. 4  cosine 0.3784  score 0.032
[20] Heinrich von Kleist 1805/06 ... Verfertigung der Gedanken beim Reden, S. 5  cosine 0.3316  score 0.0315
[1]  Immanuel Kant 1784 ..., S. 1  cosine 0.4725  score 0.0315
[17] Heinrich von Kleist ..., S. 3  cosine 0.3233  score 0.0284  Lücken: [18, 19]
```

Dauer 14 s je Aufruf als Kommandozeile (davon der größte Teil Import und Modell laden). Zwei Dinge fallen auf:

- Die Rangfolge ist nicht sauber. Chunk 10 (nebensächlich) steht vor Chunk 1 (die Definition), und ein Kleist-Chunk steht auf Rang 2. Grund: Bei 22 Chunks und ohne Stoppwortliste punkten Füllwörter der Frage ("was", "unter") im BM25, und die RRF-Werte liegen mit 0,032 gegen 0,0315 dicht beieinander. In einem großen Bestand mittelt sich das aus, in diesem Beispiel nicht.
- Das Lücken-Feld funktioniert: Treffer 17 nennt die ungesehenen Nachbarn 18 und 19.

Filter `--quelle Kleist`: nur Kleist-Treffer, Lücken-Feld gesetzt (Treffer 14 nennt 15, 16, 17). `--deckung`: 2 Quellen im Register, 2 im Index, 22 Chunks, keine Quelle ohne Chunks.

Mit `--rerank` (BAAI/bge-reranker-v2-m3, CPU): 26 s für eine Frage, die Reihenfolge wurde schlechter (ein Kleist-Chunk auf Rang 1 für eine Kant-Frage). Mit 22 Chunks ist das kein Urteil über den Reranker, nur der Nachweis, dass der Pfad läuft.

## 3. Goldset

```
python goldset.py
G1 bis G5: Rang 1 jeweils
Fragen: 5  hit@1: 1.000  hit@8: 1.000  MRR: 1.000  (14.5 s)

python goldset.py --rerank
G1: Rang 2, G2 bis G5: Rang 1
Fragen: 5  hit@1: 0.800  hit@8: 1.000  MRR: 0.900  (62.1 s)
```

Ohne Reranker: **hit@8 1,000, MRR 1,000**. Mit Reranker: hit@8 1,000, MRR 0,900.

Einordnung: Das Goldset prüft nur, ob die richtige von zwei Quellen vorn liegt. Mit zwei Quellen ist das eine leichte Aufgabe. Die Zahlen zeigen, dass die Kette läuft, nicht dass die Suche gut ist. Die Fragen wurden außerdem vom Autor des Beispiels geschrieben, der die Texte kannte (kein getrenntes Prüfset). Der Goldset-Lauf schaltet den Quellen-Deckel ab (`quellen_deckel=0`), damit der Rang die reine Ordnung zeigt.

## 4. MCP-Server

Prüfung mit dem Python-Client des Pakets `mcp` über stdio (Handshake, Werkzeugliste, je ein Aufruf):

```
Werkzeuge: ['suchen', 'stelle', 'deckung']
suchen: [(3, '2'), (8, '4')] isError: False
stelle isError: False
deckung isError: False  {"quellen_im_register": 2, "quellen_im_index": 2, "chunks": 22, ...
```

Gesamtdauer des Clientlaufs rund 16 s (Start, Import, Modell laden, drei Aufrufe).

Gefundener und behobener Fehler: In der ersten Fassung importierte der Server `sentence-transformers` erst in der ersten Suche. Unter Windows blieb der Aufruf dabei im DLL-Laden von scipy hängen (Server antwortet nicht, Client meldet nach dem Timeout "Connection closed"). Die Handshake-Tests mit rohen JSON-Zeilen liefen davor durch, weil die Eingabe sofort geschlossen wurde. Fix: Torch und sentence-transformers werden beim Serverstart im Hauptthread importiert, die Werkzeuge laufen als `async` mit `asyncio.to_thread`. Danach lief der Client-Test sauber durch. Der Fehler ist auf Windows beobachtet, auf macOS und Linux nicht getestet.

## Nicht getestet

- GPU-Pfad (fp16, CUDA): kein CUDA im Test, Code vorhanden, nie gelaufen.
- Kontextsätze: das Einlesen einer `kontexte.jsonl` wurde nicht ausgeführt, es gab keine Datei zum Testen.
- Großer Bestand: getestet wurde mit 22 Chunks. Laufzeit und Speicher bei Zehntausenden Chunks sind nicht gemessen.
- Anbindung an Claude Code oder Claude Desktop selbst (nur der Server und ein Python-Client).
- EPUB und Scans: der Code liest nur `.txt` und `.pdf`.
