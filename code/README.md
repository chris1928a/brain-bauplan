# Brain in klein: eine lauffähige Referenz

Dieser Ordner baut die Suche eines Brains im Kleinformat nach: Texte einlesen, in Textstellen (Chunks) schneiden, einbetten, Stichwortindex (BM25) rechnen, mit Vektor plus BM25 suchen und das Ganze Claude als Werkzeug (MCP) anbieten. Der Code ist kurz und auf Deutsch kommentiert. Lest ihn, bevor ihr ihn ändert.

## Installation in fünf Befehlen

Voraussetzung: Python 3.11 oder 3.12. Im Ordner `code/`:

```
python -m venv .venv && .venv\Scriptsctivate          # macOS und Linux: source .venv/bin/activate
pip install torch && pip install -r requirements.txt     # Torch zuerst, GPU-Variante siehe unten
python build_index.py beispiel                           # Beispielindex bauen
python suche.py "Was versteht Kant unter Unmündigkeit?" --en "What does Kant mean by immaturity?"
claude mcp add brain -- ...                              # als MCP anschließen, siehe nächster Abschnitt
```

Beim ersten Bauen lädt `sentence-transformers` das Embedding-Modell (Snowflake arctic-embed-l-v2.0, rund 2 GB) in den Modell-Cache. Das dauert einmal. Der Beispielindex hat 22 Chunks und ist auf einer CPU in unter einer Minute gebaut.

Messen könnt ihr mit `python goldset.py`: fünf Fragen gegen den Beispielindex, Ausgabe hit@1, hit@8 und MRR. Das Beispiel hat nur zwei Quellen und taugt als Funktionstest, nicht als Qualitätsnachweis.

## Als MCP-Server an Claude anschließen

Claude Code (Pfade anpassen, absolut):

```
claude mcp add brain --env BRAIN_INDEX=/PFAD/ZU/code/index/current -- /PFAD/ZU/code/.venv/bin/python /PFAD/ZU/code/mcp_server.py
```

Unter Windows zeigt der Python-Pfad auf `.venv\Scripts\python.exe`. Für Claude Desktop trägt ihr denselben Aufruf in der `claude_desktop_config.json` unter `mcpServers` ein:

```
{ "mcpServers": { "brain": {
    "command": "/PFAD/ZU/code/.venv/bin/python",
    "args": ["/PFAD/ZU/code/mcp_server.py"],
    "env": { "BRAIN_INDEX": "/PFAD/ZU/code/index/current" } } } }
```

Claude bekommt drei Werkzeuge: `suchen`, `stelle` (Nachbarstellen lesen), `deckung` (was ist im Index). Pro Frage verlassen Frage und Treffertext den Rechner, nicht das Buch.

## Was die Dateien tun

| Datei | Aufgabe |
|---|---|
| `build_index.py` | liest `.txt` und `.pdf` aus einem Ordner, schreibt Register, Chunks, Vektoren, BM25 und `manifest.json` in einen Ordner `build-<Zeitstempel>` und benennt ihn am Ende in `current` um |
| `suche.py` | Kommandozeile und Funktionen `suchen`, `stelle`, `deckung` |
| `mcp_server.py` | MCP-Server mit denselben drei Werkzeugen |
| `goldset.py` | misst hit@1, hit@8 und MRR gegen `beispiel/fragen.jsonl` |
| `beispiel/` | zwei gemeinfreie Texte (Kant, Kleist) und fünf Prüffragen |

Eigene Quellen: `.txt` oder `.pdf` in einen Ordner legen und `python build_index.py MEIN-ORDNER` aufrufen. Eine `.txt` darf oben einen Kopf haben (`Titel:`, `Autor:`, `Jahr:`, `Typ:`, `Lizenz:`, `Quelle:`), sonst werden Dateiname und `unbekannt` eingetragen. Bei eigenen Texten gehören Seitenmarker `--- PAGE n ---` hinein, bei PDFs setzt sie das Skript. Ohne Marker gibt es keine Seitenzahl im Treffer.

Der Bau ist inkrementell: Chunks mit unverändertem Text übernehmen ihren Vektor aus dem bisherigen `current`. Geschrieben wird nie direkt in `current`, sondern in `build-...`. Der alte Stand bleibt als `build-vorher-...` liegen, ihr könnt ihn löschen.

Eine Datei `kontexte.jsonl` im Quellordner (eine Zeile `{"hash": "<sha256 des Chunk-Textes>", "kontext": "..."}`) stellt den Kontextsatz vor den Text. Beim Beispiel gibt es keine.

## Was der Code kann und was nicht

Er kann: Chunking absatzweise bis 480 Token ohne Overlap, Embedding (fp16 auf GPU, fp32 auf CPU), eigenes BM25, Suche mit Frage in zwei Sprachen, RRF-Fusion, Filter an Wortgrenzen vor dem Abschneiden, optionalen Reranker über die besten 100, Quellen-Deckel, Lücken-Feld.

Er kann nicht, und das steht in den Kapiteln:

- **Kontextsätze erzeugen.** Es gibt keinen Generator, nur das Einlesen einer fertigen `kontexte.jsonl`.
- **Beiwerk erkennen** (Literaturverzeichnisse, Register, Zahlenkolonnen ausblenden). Es gibt keinen Klassifikator.
- **Werk-Durchgang** (zweiter Suchlauf, wenn die Frage ein Werk oder einen Autor nennt).
- **Zusammenfassungen, Typ-Maluse, Primärquellen-Boost, Scherben** für sehr große Bestände, OCR für Scans.

Der Index liegt in einer Datei je Art (`vectors.npy`, `chunks.jsonl`, `bm25.npz`). Das reicht für einige zehntausend Chunks. Die Suche rechnet linear über alle Vektoren.

## GPU (CUDA-Torch)

`pip install torch` ohne weitere Angabe liefert je nach System die CPU-Variante. Mit CPU läuft alles, aber das Einbetten großer Bestände dauert Stunden, und der Reranker ist auf der CPU unbrauchbar langsam. Für eine NVIDIA-Karte installiert ihr Torch vor den anderen Paketen mit dem CUDA-Index, zum Beispiel:

```
pip install torch --index-url https://download.pytorch.org/whl/cu128
```

Welche Zahl (`cu128`) passt, steht auf pytorch.org unter "Get Started". Prüfen: `python -c "import torch; print(torch.cuda.is_available())"` muss `True` ausgeben. Meldet es `False`, ist der häufigste Grund eine CPU-Variante von Torch.

## Lizenzen der Beispieltexte

Kant, "Beantwortung der Frage: Was ist Aufklärung?" (1784) und Kleist, "Über die allmähliche Verfertigung der Gedanken beim Reden" sind gemeinfrei. Die Textfassungen stammen von Projekt Gutenberg. Die Quelle steht im Kopf jeder Datei.
