# Glossar

Die Fachwörter dieses Bauplans in alphabetischer Reihenfolge. Jede Erklärung gilt für den Bauplan, nicht für das Fach als Ganzes.

**Beiwerk-Filter.** Ein Programmteil, der Literaturverzeichnisse, Register und Zahlenkolonnen aus den Treffern blendet. Er irrt sich bei einem kleinen Teil der Chunks, deshalb lässt man ihn bei Unterlagen mit vielen Tabellen aus ([Kapitel 6](06-suche.md)).

**BM25.** Ein Verfahren der Wortsuche. Es bewertet, wie oft und wie selten ein Suchwort in einem Chunk vorkommt. Es findet genaue Wörter wie Namen und Paragrafen.

**Brain.** Mein Wort für eine durchsuchbare Bibliothek zu einem Fachgebiet: Quellen, Register, Index und der Server, über den Claude sie fragt.

**Chunk.** Ein Textausschnitt von rund 270 Wörtern, etwa eine Buchseite. Der Index durchsucht Chunks, keine ganzen Bücher.

**Cross-Encoder.** Ein Modell, das Frage und Chunk gemeinsam liest und eine Passung bewertet. Es ist genauer und langsamer als die Vorauswahl. Der Reranker ist ein Cross-Encoder.

**Deckung.** Das Maß, wie viel vom Register tatsächlich im Index steht. Ich prüfe sie nach jedem Einlesen und lasse den Wert nur steigen ([Kapitel 5](05-einlesen-und-index.md)).

**DRM.** Kopierschutz bei E-Books. Ein DRM-freies E-Book könnt ihr als Datei einlesen. Den Schutz zu entfernen, empfehle ich nicht ([Kapitel 4](04-quellen-beschaffen.md)).

**Embedding.** Die Übersetzung eines Textes in eine Zahlenreihe, die seine Bedeutung abbildet. Ähnliche Texte erhalten ähnliche Zahlen, auch wenn sie andere Wörter benutzen.

**fp16.** Eine Zahlenform mit halber Genauigkeit. Sie macht das Embedding auf der Grafikkarte deutlich schneller bei kaum messbarem Unterschied.

**Goldset.** Eine Liste von Testfragen mit bekannter richtiger Fundstelle. Jede Änderung am System läuft dagegen ([Kapitel 7](07-messen-und-verbessern.md)).

**Halluzination.** Eine erfundene Antwort, die so klingt wie eine richtige. Die KI merkt nicht, dass sie rät.

**hit@k.** Der Anteil der Testfragen, bei denen die richtige Stelle unter den ersten k Treffern liegt. Ich nutze k gleich 8: hit@8 von 0,82 heißt, bei 82 von 100 Fragen liegt sie unter den acht.

**Index.** Die durchsuchbare Ablage: Vektoren, Chunk-Texte und der Wortindex für BM25. Der Index ist aus Quellen, Register und Kontextsätzen neu baubar.

**Kontextsatz.** Ein Satz, den eine KI jedem Chunk voranstellt: aus welchem Buch, welchem Kapitel, zu welchem Thema. Er hilft, den Chunk zuzuordnen ([Kapitel 5](05-einlesen-und-index.md)).

**MCP.** Model Context Protocol, ein Standard, mit dem Claude externe Programme aufruft. Das Brain ist für Claude ein MCP-Server mit vier Werkzeugen ([Kapitel 8](08-anschluss-claude-mcp.md)).

**MRR.** Mean Reciprocal Rank. Der Mittelwert von 1 geteilt durch den Rang der richtigen Stelle. Platz 1 zählt 1, Platz 2 zählt 0,5. Je näher an 1, desto weiter vorn.

**OCR.** Texterkennung für Scans. Sie wandelt ein Bild einer Seite in Text. Ich nutze Tesseract.

**Primärquelle.** Die Originalquelle: Gesetz, Urteil, das Werk selbst. Das Gegenstück ist Sekundärliteratur, die darüber schreibt. Die Suche bevorzugt Primärquellen leicht.

**RAG.** Retrieval Augmented Generation. Erst nachschlagen, dann die Treffer der KI mitgeben, dann antworten lassen ([Kapitel 1](01-warum-ein-brain.md)).

**Ratsche.** Eine Prüfregel, die den besten erreichten Messwert als Untergrenze speichert. Ein Lauf darf ihn heben, nicht senken.

**Register.** Eine Datei mit einer Zeile je Quelle: Titel, Autor, Typ, Herkunft, Lizenz. Sie ist die Wahrheit für die Kuratierung ([Kapitel 3](03-quellen-finden.md)).

**Reranker.** Ein Cross-Encoder, der die Kandidaten der Vorauswahl neu sortiert. Bei mir bge-reranker-v2-m3. Auf der CPU ist er sehr langsam, in manchen Brains verschlechtert er das Ergebnis ([Kapitel 6](06-suche.md)).

**RRF.** Reciprocal Rank Fusion. Ein Verfahren, das die Trefferlisten von Bedeutungssuche und Wortsuche zu einer Liste mischt. Jeder Rang zählt 1 geteilt durch 60 plus Rang.

**Seitenmarker.** Eine Zeile `--- PAGE n ---` im Volltext. Ohne sie nennt ein Treffer keine Seitenzahl.

**Token.** Ein Wortteil, die Zähleinheit von Sprachmodellen. In meinem überwiegend englischen Bestand kamen 1,853 Token auf ein Wort. Die Chunk-Grenze liegt bei mir bei 480 Token.

**Vektor.** Eine Reihe von Zahlen. Mein Embedding-Modell liefert 1.024 Zahlen je Chunk.

**VRAM.** Der Speicher der Grafikkarte. Er entscheidet, welche Modelle auf die Karte passen ([Kapitel 2](02-hardware.md)).
