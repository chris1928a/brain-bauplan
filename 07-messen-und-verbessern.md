# 07 Messen und verbessern

Es wird kein Modell trainiert. Trainiert wird die Konfiguration, und zwar gegen ein Goldset: eine Liste von Fragen, bei denen ihr die richtige Fundstelle vorher kennt. Jede Änderung am Brain läuft gegen dieselbe Liste. Wird das Ergebnis schlechter, fliegt die Änderung raus. Das ist der ganze Trick, und er hat bei mir mehr bewirkt als jedes neue Werkzeug.

Die Sprachmodelle im Brain (Embedding und Reranker, siehe [Einlesen](05-einlesen-und-index.md) und [Suche](06-suche.md)) werden fertig geladen, ihre Gewichte fasse ich nie an. Verändert werden Schwellen, Filter, Reihenfolgen und die Daten selbst.

## Das Goldset

Ein Goldset ist eine Datei mit einer Frage je Zeile. Zu jeder Frage steht, welche Quelle und, wenn möglich, welche Textstelle unter den acht Treffern liegen muss. Die Datei prüft nicht, ob die Antwort der KI stimmt. Sie prüft, ob die richtige Stelle auf dem Tisch liegt, bevor die KI zu schreiben anfängt. Das ist die Hälfte des Problems, die sich zählen lässt.

So sieht eine Zeile bei mir aus (Beispieleintrag zur Erklärung, nicht aus meinem echten Goldset):

```json
{
  "id": "B01",
  "kategorie": "primaertext",
  "frage": "Wann haftet ein selbstschuldnerischer Bürge?",
  "frage_en": "When is a guarantor with waiver of defences liable?",
  "erwartet_quelle_substring": "Erman",
  "erwartet_text_substring": "Ausschnitt aus der Fundstelle, wörtlich",
  "abnahme_rang_max": 3,
  "params": {"type": "kommentar"}
}
```

Die Felder:

- `id` und `kategorie`: eindeutige Nummer und Gruppe (primaertext, zahl, deutsch, kontrolle, beiwerk).
- `frage` und `frage_en`: die Frage deutsch und englisch, so wie Claude sie später an die Suche gibt.
- `erwartet_quelle_substring`: ein Stück des Quellentitels. Eine Liste ist erlaubt, dann gilt "eines davon".
- `erwartet_text_substring` (optional): ein wörtlicher Ausschnitt der Fundstelle. Das ist schärfer als der Titel, denn ein Buch hat Hunderte Stellen.
- `abnahme_rang_max` (optional): harte Obergrenze. Liegt der Treffer tiefer, gilt der Fall als nicht bestanden.
- `params`: Filter, die unverändert an die Suche gehen.

Mein Geschichts-Brain hat heute 106 solcher Zeilen.

### Das Prüfskript

Bevor ein Goldset benutzt wird, läuft ein Prüfskript darüber. Mein Skript prüft: gültiges JSON, Pflichtfelder, eindeutige ids, ob der Titelausschnitt im Index vorkommt (Warnung, wenn er mehr als drei Titel trifft, dann ist er zu unscharf), ob der Textausschnitt ein- bis dreimal vorkommt, und Leakage.

Leakage heißt: Die Frage verrät die Antwort. Steht der Wortlaut der Erwartung schon in der Frage, findet die Suche die Stelle über die Wörter und nicht über die Bedeutung. Dann sieht das Brain besser aus, als es ist. Ab drei gemeinsamen Wörtern schlägt mein Skript Alarm.

Eine Minimalfassung für den Einstieg, nur mit Python-Standardbibliothek, ohne Abgleich gegen den Index. Leere Zeilen im Goldset darf es nicht geben.

```python
import json, re, sys

PFLICHT = ["id", "kategorie", "frage", "frage_en", "erwartet_quelle_substring"]
woerter = lambda s: {w for w in re.findall(r"\w+", s.lower()) if len(w) >= 5}

ids, probleme = set(), []
for nr, zeile in enumerate(open(sys.argv[1], encoding="utf-8"), 1):
    e = json.loads(zeile)
    fehlt = [f for f in PFLICHT if not e.get(f)]
    if fehlt:
        probleme.append(f"Zeile {nr}: fehlt {fehlt}")
    if e.get("id") in ids:
        probleme.append(f"Zeile {nr}: id doppelt")
    ids.add(e.get("id"))
    frage = e.get("frage", "") + " " + e.get("frage_en", "")
    if len(woerter(str(e.get("erwartet_text_substring", ""))) & woerter(frage)) >= 3:
        probleme.append(f"Zeile {nr}: Leakage")
print(chr(10).join(probleme) or "ok")
sys.exit(1 if probleme else 0)
```



### Woher die Fragen kommen

Meine Fragen stammen aus drei Quellen. Erstens aus bekannten Fehlfällen: eine Stelle, die ich im Buch kenne und die das System nicht fand. Zweitens aus Textausschnitten der Primärpassage, die ich selbst aufgeschlagen habe. Drittens aus Beschaffungsprüfungen: Ich lese ein Buch ein und frage nach etwas, das nur darin steht. Dazu kommen Kontrollfragen. Sie prüfen, dass ein Mechanismus nicht auslöst, wo er nicht auslösen soll.

Das ist auch die Schwäche, dazu unten mehr. Für euch heißt es: Schreibt die Fragen aus eurer Berufspraxis. Ihr wisst, wonach Mandanten fragen und in welchem Kommentar die Antwort steht. Die Frage kommt von euch, die Stelle schlagt ihr im Buch auf, nicht über das Brain.

## Die Metriken

Alle Metriken rechnen mit den Top 8 (k = 8), denn so viele Stellen bekommt Claude.

- hit@k: Anteil der Fragen, bei denen die erwartete Stelle unter den ersten k Treffern liegt. hit@8 ist die Zahl, auf die es ankommt.
- hit@1: Anteil der Fragen, bei denen die erwartete Stelle ganz oben steht.
- MRR (Mean Reciprocal Rank): Mittelwert aus 1 geteilt durch den Rang des Treffers. Rang 1 gibt 1, Rang 2 gibt 0,5, kein Treffer gibt 0.
- Abnahme-Rang: die harte Obergrenze je Fall. Ein Fall ist bestanden, wenn der Treffer mindestens so weit oben liegt.

Gemessen wird über denselben Aufruf, den auch Claude benutzt, damit Filter, Reranker und Deckel wie im Betrieb wirken. Mein erstes Messwerkzeug ging daran vorbei und hat ein System gemessen, das es im Betrieb nie gab.

## Gate und Ratsche

Zwei Regeln halten die Qualität oben.

**Das Gate.** Eine Änderung wird nur übernommen, wenn hit@8 auf den alten Fällen nicht um mehr als 0,02 fällt. Die Reihenfolge der Kriterien lege ich vor der Messung fest: erst hit@8, dann MRR, dann Einfachheit. Ausgeschieden wird auch, wenn ein Pflichtfall nicht mehr besteht oder eine Kontrollfrage plötzlich auslöst. Die Regel vorher festzulegen verhindert, dass ich mir das Ergebnis nachträglich schönrede.

**Die Ratsche.** Der beste erreichte Stand steht in einer Datei. Ein Lauf darf diesen Stand nur heben. Fällt er darunter, beendet sich das Prüfprogramm mit Fehlercode, und ich sehe es. Dasselbe Prinzip gilt für die Abdeckung der Quellen (siehe Inventur unten).

Ein Beispiel: Ein Abzug auf Impressum und Inhaltsverzeichnis sollte Ballast aus den Treffern drücken. Gemessen: MRR 0,6098 mit Abzug, 0,6417 ohne, 0,6466 als Ausgangswert. Der Abzug bleibt aus.

## Fallstudie: die drei Defekte vom 03.09.2026

Am 3. September 2026 lagen drei konkrete Fehler offen. Jeder war ein Fall im Goldset, den ich von Hand nachgestellt hatte.

| Defekt | Was passierte | Ursache | Fix | Messung |
|---|---|---|---|---|
| Zitate werden ausgeblendet | Eine Quelle mit Aktenzeichen in Klammern fiel aus den Top 8, ebenso griechische Urtexte | Der Filter für Beiwerk (Literaturverzeichnisse, Register) hielt zitatdichte Prosa für ein Verzeichnis | Neuer Klassifikator, 600 Textstücke blind gelabelt, 10.800 Schwellen-Kombinationen durchsucht | Präzision 60,3 auf 91,0 Prozent, Recall 90,5 auf 91,0 Prozent, kein Fall schlechter |
| Falsche Reihenfolge nach dem Reranker | Der deutsche Primärtext mit der höchsten Ähnlichkeit (0,6356) rutschte auf Rang 3 hinter zwei englische Schreibratgeber, Zusammenfassungen belegten die Top 3 | Reranker zog Sekundärliteratur vor, der Deckel zählte Werk und Zusammenfassung doppelt | Abzug für Zusammenfassungen, normalisierter Deckel, Lücken-Feld | hit@8 0,700 auf 0,733, MRR 0,530 auf 0,569 |
| Passage nicht in den Kandidaten | Das Werk wurde gefunden, die gesuchte Passage nicht | Die Stelle stand nicht in den ersten 100 der Fusion | Zweiter, gefilterter Suchlauf, sobald Autor oder Werk in der Frage vorkommt | 7 Fragen besser, 5 um genau einen Rang schlechter, keine fällt aus den Top 8, alle 8 Kontrollfragen lösen nicht aus |

Die Gesamtzahlen auf den 60 Fragen von damals:

| Metrik | Vorher | Nachher |
|---|---|---|
| hit@1 | 0,433 | 0,533 |
| hit@3 | 0,617 | 0,683 |
| hit@8 | 0,700 | 0,817 |
| MRR | 0,530 | 0,627 |
| Zeit je Frage | 0,81 s | 1,04 s |

Bei Fragen nach Zahlen stieg hit@8 von 0,500 auf 0,875. Insgesamt sind das 42 auf 49 von 60 Fragen, also sieben Fragen. Ein echter Fortschritt, aber eine kleine Stichprobe.

Zwei Dinge gehören dazu. Erstens: Der Fall, der den dritten Defekt ausgelöst hat, ist bis heute nicht gelöst. Der Symptomkatalog der Pest bei Thukydides bleibt offen, drei andere Abnahmefälle bestehen jetzt. Zweitens: Ich habe 28 Konfigurationen gemessen, R0 bis R27. Verworfen wurden unter anderem eine Mischung der Ranglisten (ein Fall fiel in jeder Variante heraus) und ein Reranker-Modus, der beide Sprachen auswertet (36 Prozent mehr Zeit, drei Fälle verloren).

### Die Endstände der anderen Brains

| Brain | Fragen | hit@8 | MRR |
|---|---|---|---|
| Finanzen | 95 | 0,989 | 0,818 |
| Technik | 56 | 0,946 | 0,850 |
| Beratung | 32 | 1,0 | 0,906 |
| Psychologie | 61 | 1,0 | 0,945 |
| Musik | 20 | 1,0 | 0,879 |
| Recht | 20 | 0,80 | 0,61 |

Beim Recht-Brain liegt der Treffer nur bei 10 von 20 Fragen auf Rang 1, es ist das schwächste. Eine Stelle auf Rang 9 ist für Claude unsichtbar, auch wenn sie im Index steht.

## Reranker: an oder aus, je Brain

Der Reranker ist der Prüfer, der die Kandidaten einzeln liest (siehe [Suche](06-suche.md)). Er hilft nicht überall.

| Brain | Fragen | Reranker aus | Reranker an |
|---|---|---|---|
| Geschichte | 60 | hit@8 0,700, MRR 0,5924 | hit@8 0,817, MRR 0,6268 |
| Finanzen | 80 | 80 von 80, MRR 0,814 | 79 von 80, MRR 0,736 |
| Psychologie | 61 | MRR 0,945 | MRR 0,857 |

Bei Geschichte hilft er, bei Finanzen und Psychologie schadet er. Warum, habe ich nicht untersucht. Für Beratung, Technik und Recht läuft er, ohne dass ich ihn dort gegen "aus" gemessen habe.

Die Konsequenz für euch: Baut den Index, messt mit und ohne Reranker, nehmt die bessere Einstellung. Ohne Grafikkarte ist die Frage ohnehin entschieden: Auf vier CPU-Kernen braucht er 127 Sekunden je Frage, auf einer RTX 3080 0,54 Sekunden (siehe [Hardware](02-hardware.md)).

## Warum k bei 8 bleibt

Das Kostenaudit zeigte: Eine Suche liefert im Median 19.047 Zeichen, rund 5.400 Token. Mit k = 5 statt 8 hätte ich rund 40 Prozent dieses Kontexts gespart. Ich habe nachgemessen, was das kostet. Bei 85 von 106 Prüfungen lag der Treffer in den Top 8. Davon wären bei k = 5 neun weggefallen, 10,6 Prozent.

Entscheidung: k bleibt 8. Jeder zehnte Treffer ist mir mehr wert als 40 Prozent weniger Kontext.

## Kontextsätze: was sie messbar gebracht haben

Ein Kontextsatz ist eine Zeile, die vor jede Textstelle gestellt wird: aus welchem Buch, aus welchem Zusammenhang (siehe [Einlesen](05-einlesen-und-index.md)). Er soll helfen, die Stelle zu finden. Gemessen, jeweils ohne gegen mit Kontextsätzen:

| Brain, Fragen, Metrik | ohne | mit |
|---|---|---|
| Finanzen, 45, MRR | 0,781 | 0,779 |
| Finanzen, 60, MRR | 0,800 | 0,808 |
| Technik, 31, hit@8 | 0,935 | 0,903 |
| Technik, 31, MRR | 0,875 | 0,871 |
| Technik, 56, MRR | 0,841 | 0,850 |

Die Unterschiede liegen bei wenigen Tausendsteln bis Hundertsteln, mal nach oben, mal nach unten. Beim Recht-Brain habe ich die Kontextsätze von Englisch auf Deutsch umgestellt. In 20 Fragen änderte sich kein einziger Rang. Beim Psychologie-Brain stieg die MRR von 0,523 auf 0,557, aber dort hatte sich der Korpus zwischen den Läufen geändert. Eine einzige echte Verbesserung steht im Raum, beim Geschichts-Brain (Detailfragen von 14 von 24 auf 34 von 50 Prozent). Dort kam gleichzeitig ein Modellwechsel dazu, ich kann sie keinem der beiden Schritte zuschreiben.

Mein Fazit: Die Messung belegt den Nutzen nicht, aber auch keinen Schaden. Ich mache sie weiter, weil sie lokal nichts kosten. Wer Zeit sparen will, lässt sie weg und misst selbst.

Ein lokales Modell (Qwen 2.5, 14 Milliarden Parameter) erreichte beim Schreiben der Kontextsätze 106,6 Prozent der Punkte von Haiku 4.5 in der Cloud. Bewertet hat ein Regelwerk aus Mustern, die Suchqualität wurde nicht gemessen.

## Inventur: der Fehler, den kein Test findet

Die schlimmste Panne war keine Rangfrage. Am 12. August 2026 meldete mein System: alles fertig. Ein Audit am selben Tag zeigte, dass der Index nur 171 von 454 Zeilen des Registers kannte (37,7 Prozent der Titel, 32,0 Prozent der Wörter). Fast zwei Drittel der Bücher fehlten. Die Wikingerzeit hatte 32 Titel im Register und null Textstellen im Index.

Das Audit fand acht Fehler, drei davon still: Der Metadatenfilter filterte nicht, die Seitenangabe war um eins zu hoch, und das Abnahme-Gate war Dekoration. Zwei meiner eigenen Zahlen waren falsch.

Daraus wurde eine Regel mit drei Teilen. Erstens: **Erfolgsmeldung ist kein Beweis.** Nach jedem Einlesen läuft eine Inventur, die zählt und nicht zusammenfasst. Zweitens: Eine Quelle hat **drei Zustände**: im Register eingetragen, als Datei vorhanden, im Index. Jeder kann einzeln stimmen oder fehlen. Wer sagt "die Quelle fehlt", prüft alle drei. Am 5. September erklärte eine Analyse ein Werk für nicht eingelesen, obwohl 3.592 Textstellen davon im Index lagen. Drittens: Vor dem Satz "Ranking kaputt" schaut man auf das Feld `type` der Treffer. Bei mir stand `primary-book` bei 505 Einträgen, 390 davon Sekundärliteratur. Der Primärquellen-Bonus war deshalb wirkungslos, bis ich die Typen aufgeräumt hatte.

Das Werkzeug `deckung` vergleicht Register und Index (Titel, Wörter, Textstellen je Bereich) und merkt sich den erreichten Stand als Ratsche. Ein Bereich mit null Textstellen ist ein harter Fehler. Nach jedem Bau setze ich den Stand neu. Abweichungen gibt es trotzdem: Beim Beratungs-Brain nennt das Manifest 45.252 Textstellen, die Deckungsdatei 40.226. Sie ist älter als der Index.

## Schwächen

Das System ist besser gemessen als die meisten, die ich kenne. Es ist trotzdem nicht sauber gemessen.

1. **Das erste Goldset stammt aus Treffern des eigenen Systems.** Die Einträge haben den Kommentar "Verifizierter Treffer, gemessen am 31.08.2026". Ich habe aufgeschrieben, was das System fand, und mir bestätigt, dass es das wieder findet. Fragen, die es nie findet, fehlen. Am 12. August stand noch im Architekturpapier, dass kein von Hand beurteiltes Ergebnis existiert.
2. **Auswahl und Bericht laufen auf denselben Fragen.** Die 28 Konfigurationen habe ich auf denselben 60 Fragen gemessen, aus denen ich die Zahl 0,817 berichte. Wer 28 Varianten am selben Prüfstein ausprobiert, findet die, die am besten zu diesem Prüfstein passt. Ein Teil der 82 Prozent ist Überanpassung. Wie groß der Teil ist, habe ich nicht gemessen.
3. **Es gibt kein getrenntes Prüfset (Holdout).** Nur der Klassifikator für Beiwerk hat eines (200 Textstücke, Präzision 0,933, Recall 0,889). Die Labels dazu hat aber kein Mensch gesetzt, sondern sechs KI-Agenten. Ob es eine Stichprobe von Hand gab, steht nicht in den Berichten.
4. **Treffer in den Top 8 ist nicht Antwort richtig.** Ob Claude aus der richtigen Stelle auch die richtige Antwort macht, ist nicht separat gemessen. Das Titel-Kriterium unterscheidet zudem nicht zwischen einer Primärquelle und ihrer Zusammenfassung.
5. **Die 82 Prozent stammen aus dem Geschichts-Brain**, nicht aus dem Recht-Brain. Dort liegt der Wert niedriger (16 von 20 in den Top 8).

**Meine Empfehlung für euch:** Legt von Anfang an zehn Fragen beiseite. Schreibt sie am ersten Tag, aus eurer Praxis, mit der Fundstelle aus dem Buch. Benutzt sie nie zum Einstellen. Lasst sie genau einmal laufen, wenn ihr mit allen Änderungen fertig seid, und berichtet diese Zahl. Alle weiteren Fragen sind Arbeitsfragen, mit denen ihr probieren dürft. Das kostet einen Nachmittag und erspart euch meinen Fehler. Die Planung dazu steht im [Wochenend-Plan](11-wochenende-plan.md).

## Was hier offen ist

- Ob ein getrenntes Prüfset die Zahl 0,817 bestätigt oder senkt: nicht gemessen.
- Reranker an gegen aus für Beratung, Technik und Recht: nicht gemessen.
- Der Finanz-Vergleich beruht auf dem Fragenstand vom 21.09. mit 80 Fragen. Das Goldset hat heute 95.
- Kontextsätze sind in meinen Läufen weder als Gewinn noch als Schaden belegt. Ob das Kapitel zum Einlesen sie als Standardschritt oder als optional führt, ist abzugleichen.
- Der Abzug auf Impressum und Frontmatter ist in der Dokumentation als "an" beschrieben, im Code aber aus. Gemessen wurde die Variante aus.
- Das Prüfskript liegt hier nur als Skizze vor und ist nicht gegen ein echtes Goldset gelaufen.
