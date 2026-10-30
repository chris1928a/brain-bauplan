# 08 Anschluss an Claude über MCP

MCP ist ein offener Standard, mit dem Claude ein Programm auf eurem Rechner wie ein Werkzeug aufrufen kann. Euer Brain ist dann kein Webdienst, sondern ein kleines Programm, das Claude Fragen stellt und Stellen zurückgibt. Wann nachgeschlagen wird, entscheidet Claude selbst.

Der Server ist ein einziges Python-Programm. Er spricht über Standardeingabe und Standardausgabe mit Claude, ohne offenen Netzwerkport. Er lädt Index und Modell erst beim ersten Werkzeugaufruf, nicht beim Start. Merkt euch das, es wird bei der Fehlersuche wichtig.

## Die vier Werkzeuge

**`suchen`** ist die eigentliche Suche: hybride Suche über Bedeutung und Wortlaut, liefert standardmäßig acht Treffer mit Quelle, Seite, Nummer und Ähnlichkeitswert (siehe [Suche](06-suche.md)). Die wichtigsten Parameter sind `frage`, `frage_en`, `k`, `type`, `quelle`, `author`, `epoche` und `beiwerk`.

```json
{
  "name": "suchen",
  "arguments": {
    "frage": "Wann tritt die Wegzugsbesteuerung bei Anteilen an Kapitalgesellschaften ein?",
    "frage_en": "When does exit taxation apply to shares in a corporation?",
    "type": "gesetz"
  }
}
```

**`stelle`** holt die Nachbarn eines Treffers aus derselben Quelle. Damit schließt Claude Lücken, wenn ein Satz an der Grenze zwischen zwei Textstücken zerschnitten wurde.

```json
{"name": "stelle", "arguments": {"nr": 16547, "umgebung": 1}}
```

**`bruecken`** liefert einen zuletzt erzeugten Bericht über Querverweise zwischen Bereichen. Für ein erstes Brain könnt ihr das ignorieren.

```json
{"name": "bruecken", "arguments": {"achse": "epoche", "anzahl": 10}}
```

**`deckung`** sagt, was der Index vom Register überhaupt kennt: Quellen, Textstellen, Bereiche. Es braucht keine Parameter.

```json
{"name": "deckung", "arguments": {}}
```

In jeder Antwort von `suchen` steht außerdem ein Feld `konfiguration` mit Index-Stand und allen aktiven Schaltern. Ich habe es eingebaut, nachdem ein Eintrag in einer Konfigurationsdatei vier Wochen lang auf einen alten Index zeigte und niemand es merkte. Auch das Feld `luecken` und der `sprachhinweis` (wenn `frage_en` fehlt) stehen dort.

Das Feld `epoche` heißt so, weil mein erstes Brain Geschichte war. Bei euch enthält es, was ihr beim Einlesen als Bereich vergeben habt, etwa Steuerrecht oder Bewertung.

## Konfiguration

Es gibt keine Installation im üblichen Sinn. Ihr tragt in die Konfiguration ein, welches Programm Claude starten soll. Alle Pfade unten sind Platzhalter. `<PYTHON_EXE>` ist das Python der Umgebung, in der ihr Torch installiert habt (siehe [Hardware](02-hardware.md)), nicht irgendein Python.

Derselbe Eintrag gilt für beide Programme, nur der Ort der Datei unterscheidet sich:

```json
{
  "mcpServers": {
    "mein-brain": {
      "command": "<PYTHON_EXE>",
      "args": ["<ORDNER_MIT_CODE>/mcp_server.py"],
      "env": {
        "BRAIN_INDEX": "<ORDNER_MIT_INDEX>/current"
      }
    }
  }
}
```

- **Claude Desktop:** in der Konfigurationsdatei, zu erreichen über Einstellungen, Entwickler, Konfiguration bearbeiten.
- **Claude Code:** im Projektordner als Datei `.mcp.json`.

`BRAIN_INDEX` ist die entscheidende Variable, so heißt sie im Referenzcode in `code/`. Sie trennt den Ort des Index vom Ort des Codes. Der Code kann aktualisiert werden, ohne den Index anzufassen, und umgekehrt. Modellname und Präfixe stehen im Manifest des Index, der Server liest sie von dort. In meinem eigenen System heißt dieselbe Variable `CCG_INDEX`, der Präfix stammt aus meinem ersten Brain.

Windows-Hinweise: In JSON schreibt ihr Pfade mit Schrägstrich (`C:/...`) oder doppeltem Rückwärtsschrägstrich. Ein einzelner Rückwärtsschrägstrich macht die Datei ungültig.

### Prüfen, dass es läuft

1. Claude Desktop vollständig beenden und neu starten. Die Konfiguration wird nur beim Start gelesen. Bei Claude Code ebenso eine neue Sitzung beginnen.
2. Fragt Claude: "Rufe das Werkzeug deckung auf." Kommt eine Zahl zurück, läuft der Server.
3. Fragt dann eine Testfrage, deren Fundstelle ihr kennt.

Wenn der erste Aufruf lange dauert, ist das normal. Das Laden braucht auf der CPU rund 164 Sekunden, auf einer RTX 3080 rund 40 Sekunden. Danach läuft eine Suche ohne Reranker in unter einer Sekunde. Rechnet beim ersten Aufruf mit dieser Wartezeit.

Die häufigste Fehlermeldung ist ein Größenfehler beim Rechnen ("size 384 is different from 1024"). Sie heißt: Das Modell in der Konfiguration passt nicht zum Index. Der Server prüft das heute vorher gegen die Datei `manifest.json` im Index-Ordner und nennt den Grund. Mir ist es passiert, als der Index noch vom alten Modell stammte und die Konfiguration schon das neue nannte.

### Mehrere Brains

Für jedes Brain ein eigener Eintrag mit demselben Programm und anderen Umgebungsvariablen: anderer Index-Ordner, anderes Register, Reranker an oder aus (im Referenzcode der Parameter `rerank` beim Aufruf, in meinem System die Variable `CCG_RERANK=0`). So laufen bei mir acht Brains aus einer Datei. Ein Brain ist nur eine Konfiguration.

## Der Skill: was Claude über das Suchen wissen muss

Die Werkzeuge allein reichen nicht. Claude sucht mit ihnen schlechter, als es könnte, wenn es die Regeln nicht kennt. Ich gebe sie als Skill mit, eine Textdatei mit Anweisungen. In Claude Code liegt sie als `SKILL.md` im Skill-Ordner. Für Claude Desktop würde ich den Text als Anweisung in ein Projekt kopieren, das habe ich nicht getestet.

Der Text, den Claude bekommt (leicht gekürzt):

```
Du hast ein Brain: eine Bibliothek mit eigenen Quellen. Schlage nach, bevor du antwortest.
Antworte nur aus den Treffern. Nenne zu jeder Aussage Quelle, Seite und Nummer.

1. Zerlege. Eine zusammengesetzte Frage wird in vier bis sieben Teilfragen
   zerlegt, jede Teilfrage bekommt eine eigene Suche.
2. Gib frage_en immer mit. Die Quellen sind überwiegend englisch. Ohne englische
   Variante findet die Wortsuche fast nichts.
3. Willst du einen Wortlaut, such mit type=gesetz (Gesetzestexte).
   Bei Büchern und Kommentaren such zweimal: einmal ohne Filter, einmal mit
   quelle=<Titelfragment>.
4. Nutze quelle, author und epoche als Filter, wenn du weißt, wo die Antwort steht.
   Bei Zahlen und Tabellen setze beiwerk=false.
5. Eine Nullmeldung heißt nicht, dass die Quelle fehlt. Prüfe zuerst: zu enger
   Filter? Falsche Sprache? Rufe deckung auf und wiederhole die Suche ohne Filter.
6. Meldet das Feld luecken fehlende Nummern, hole sie mit stelle(nr).
7. Sage "nicht belegt" erst, wenn deckung zeigt, dass das Fachgebiet im Index
   vorkommt und die Suche ohne Filter nichts liefert.
8. Treffer mit cosine unter 0,30 sind Füllmaterial, kein Beleg.
9. Eigene Texte (type=eigen) sind kein Beleg. Zitiere die Primärquelle.
10. Markiere jede Aussage: sicher (Wortlaut im Treffer gelesen), mittel (aus
    Treffern geschlossen), unsicher (Lücke im Brain).
```

Die Regeln stammen aus Fehlern. Regel 5 zum Beispiel aus einem Fall, in dem eine Analyse ein Buch für nicht eingelesen erklärte, obwohl es im Index lag (siehe [Messen und verbessern](07-messen-und-verbessern.md)). Regel 2 aus der Messung, dass die Wortsuche mit deutscher Frage an englischen Büchern 0 von 15 Treffern fand und mit englischen Stichwörtern 94 Prozent.

## Was je Frage den Rechner verlässt

Das Brain selbst bleibt lokal. Index, Modelle, Reranker und Bücher laufen und liegen auf eurer Platte. Im Suchweg steckt kein Cloud-Dienst.

Verlassen tut den Rechner, was ihr mit Claude besprecht. Pro Suchaufruf sind das:

- die Frage und ihre englische Variante, die Claude als Argument an den Server gibt,
- die acht Treffer, die der Server zurückgibt und die dann Teil des Gesprächs sind. Eine Suche liefert im Median rund 19.000 Zeichen, etwa 5.400 Token.

Dieses Gespräch geht an den Dienst, bei dem euer Claude-Konto liegt. Bei einer Deep-Research-Frage mit sieben Teilfragen sind es entsprechend mehr Stellen, bis rund 56 (siehe [Shallow und Deep Research](09-shallow-vs-deep-research.md)). Was der Anbieter mit Gesprächsdaten tut, regeln die Bedingungen eures Abos. Das habe ich hier nicht geprüft. Bei Mandantendaten gilt: Was ihr in eine Frage schreibt, geht raus. Die Kapitel zu [Kosten und Datenschutz](10-betrieb-kosten-datenschutz.md) vertiefen das.

## Was hier offen ist

- Der Skill-Text ist eine gekürzte Fassung der Regeln, die ich verwende. Der Wortlaut des Originals ist länger.
- Die Variablennamen mit dem Präfix `CCG` stammen aus meinem System. Ob die Referenzimplementierung im Ordner `code/` dieselben Namen benutzt, ist abzugleichen.
- Claude Desktop mit Skill-Text als Projektanweisung: nicht getestet.
- Eine Fehlersuche für andere Betriebssysteme als Windows habe ich nicht geschrieben.
- Datenschutz beim Anbieter: nicht geprüft, hängt vom Abo ab.
- Ob der Server beim ersten Start Modelle aus dem Netz nachlädt, hängt von der Installation ab: nicht geprüft.
