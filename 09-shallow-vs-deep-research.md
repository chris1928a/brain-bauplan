# 09 Shallow und Deep Research

Der Unterschied zwischen einer einfachen und einer tiefen Recherche liegt nicht in der Antwort, sondern darin, dass bei der tiefen jeder einzelne Fehler nachschlagbar ist. Eine Antwort kann in beiden Fällen falsch sein. Bei Deep Research steht an jeder Aussage, woher sie kommt und wie sicher sie ist, und ihr könnt genau diese Stelle prüfen.

## Shallow gegen Deep

| | Shallow | Deep |
|---|---|---|
| Schritte | Eine Suche, acht Treffer, Antwort | Frage in vier bis sieben Teilfragen zerlegen, je Teilfrage suchen, Lücken nachholen, Widersprüche prüfen, Befund mit Sicherheitsstufen |
| Suchläufe | 1 | eine je Teilfrage, dazu Nachholen (im Beispiel unten 7 Schritte, 58 Treffer) |
| Brains | eines | bei Bedarf mehrere |
| Rechenzeit der Suche | rund 1 Sekunde ohne Reranker | Summe der einzelnen Suchen, bei sieben also rund sieben Sekunden |
| Dauer insgesamt | Sekunden | nicht gemessen, den Hauptteil macht Claude beim Lesen und Schreiben |
| Ergebnis | Antwort mit Quelle | Befund mit Quelle, Chunk-Nummer und Sicherheitsstufe je Aussage, dazu sichtbar aussortiertes Rauschen |
| Reicht für | Nachschlagen: "Was steht in § 765 BGB?", "Was schreibt Autor X zu Y?" | Fragen mit mehreren Rechtsgebieten, Fristen, Rechnung, Entscheidung |
| Reicht nicht für | Fragen, deren Antwort aus mehreren Stellen zusammengesetzt wird | Alles, was ein Nachschlagen löst. Es wäre Verschwendung |

Meine Faustregel: Wenn die Antwort an einer Stelle stehen kann, shallow. Wenn ihr sie aus mehreren Stellen zusammenbauen müsst, deep.

## Das Deep-Verfahren in Schritten

1. **Zerlegen.** Die Frage wird in Teilfragen geteilt, jede Teilfrage hat einen eigenen Suchauftrag. Im Beispiel unten sieben.
2. **Je Teilfrage zwei Suchen parallel.** Eine nach Bedeutung (deutsch und englisch), eine nach Wortlaut (Paragrafen, Zitierlabel wie "§ 6 AStG Abs. 2"). Das ist die hybride Suche aus [Suche](06-suche.md).
3. **Filter gezielt setzen.** Gesetz, Bereich oder Quelle, je nachdem, was die Teilfrage braucht.
4. **Lesen und aussortieren.** Claude liest die acht Treffer jeder Teilfrage. Was zum falschen Gesetz, zum falschen Abkommen oder zum falschen Stichwort gehört, wird aussortiert und im Bericht als Rauschen aufgeführt.
5. **Lücken nachholen.** Meldet das Feld `luecken`, dass ein Nachbar fehlt, holt `stelle(nr)` ihn. Ohne diesen Schritt fehlt manchmal der Satz, der alles dreht.
6. **Widersprüche prüfen.** Stehen zwei Aussagen gegeneinander, wird gesagt, welche gilt und warum.
7. **Befund mit Sicherheitsstufe.** Jede Aussage bekommt eine von drei Stufen. **Sicher**: Wortlaut im Treffer gelesen. **Mittel**: aus Treffern plus Rechnung oder Schluss des Modells. **Unsicher**: Lücke im Brain, das Brain hat die Stelle nicht.
8. **Quellenliste** mit Nummern, damit jede Aussage zurückverfolgt werden kann.

Die Stufen sind die wichtigste Zeile im Bericht. Ein "unsicher" ist für mich wertvoller als zehn Sätze, die alle gleich selbstbewusst klingen.

## Die vier Fragen des Skills "tiefer"

Bevor ich einen großen Auftrag an Claude gebe, lasse ich einen Skill namens "tiefer" darüber laufen. Er baut nichts. Er macht aus dem Auftrag eine tiefere Fassung, keine größere, und ich entscheide, ob ich sie fahre. Er löst nicht bei Routine aus, also nicht bei Mails, Belegen oder kleinen Fragen. Er stellt vier Fragen:

1. **Was würde ein Top-Profi zusätzlich tun?** Eine Schicht tiefer, nicht eine Aufgabe mehr.
2. **Was ist das roheste Material?** Rohdaten und Primärquellen statt Zusammenfassungen. Liegt es bei mir, oder fehlt es?
3. **Welche Methoden und Werkzeuge gibt es wirklich?** Nur Brains und Skills, die es gibt. Passt keiner, steht das da, es wird nichts erfunden.
4. **Welcher Beleg liegt außerhalb von Modell und mir?** Eine Messung, eine Gegenprobe, eine Stichprobe, eine Drittquelle oder ein Testlauf. Oder der ausdrückliche Satz, dass es keinen gibt.

Die vierte Frage ist die wichtigste. Ein Ergebnis, das nur Claude und ich bestätigen, ist noch kein belegtes Ergebnis.

## Beispiel 1: Wegzugsteuer Deutschland nach Österreich

Die Frage im Wortlaut, gestellt am 30.10.2026 an mein Finanz-Brain (1.613 Quellen, 106.062 Textstellen):

> Ich bin Österreicher, lebe seit 21.06.2020 privat in Deutschland, halte 100 Prozent der Erler Ventures UG (Exit 2022) und will mit Familie nach Österreich ziehen. Was passiert steuerlich, wann, und wie mache ich das?

Das Brain kennt, was ich eingelesen habe: Gesetzestexte, Verwaltungsschreiben, Urteile, Kommentare und meine eigenen Jahresabschlüsse. Eigene Unterlagen erscheinen nur, wenn ich mit `type=eigen` gezielt danach frage, sonst stehen sie bewusst hinten. Für dieses Brain ist der Reranker aus.

### Die sieben Schritte

| Nr | Teilfrage | Filter | Treffer | Bester Treffer | cosine | score |
|---|---|---|---|---|---|---|
| 1 | Tatbestand der Wegzugsbesteuerung | type=gesetz, Bereich steuern-de | 8 | AStG § 6 Abs. 2 und 3, Chunk 16548, Rang 1 | 0,7115 | 0,031545 |
| 2 | Nachbarstelle holen | stelle(16547) | 1 | AStG § 6 Abs. 1, Chunk 16547 | nicht in der Spur | nicht in der Spur |
| 3 | Bewertung des fiktiven Gewinns | Bereich steuern-de | 8 | BFH II R 2/24, Chunk 70718, Rang 1 | 0,6571 | 0,031054 |
| 4 | Stundung und Rückkehr | Bereich steuern-de | 8 | Anwendungserlass zum AStG, Rn. 180 f., Chunk 19134, Rang 1 | 0,6929 | 0,03125 |
| 5 | Abkommen Deutschland Österreich | Bereich international, dann quelle=DBA DE-AT | 12 | Schaumburg, Internationales Steuerrecht, S. 375, Chunk 64590, Rang 1 | 0,6554 | 0,03055 |
| 6 | Österreich-Seite | Bereich steuern-at | 8 | EStR 2000 Rz 6158a bis c, Chunk 43170, Rang 1 | 0,6681 | 0,028021 |
| 7 | Eigene Zahlen | type=eigen | 13 | Jahresabschluss 2024, Blatt 17, Chunk 45737, Rang 2 | 0,6916 | 0,031498 |

Zusammen 58 Treffer. Die Zahlen lesen sich so: `cosine` ist die Ähnlichkeit zwischen Frage und Stelle im Vektorraum, bei den besten Treffern zwischen 0,65 und 0,71. `score` ist die Rangzahl aus der Fusion beider Suchen (RRF). Mit der Formel aus [Suche](06-suche.md) kann er höchstens rund 0,033 erreichen, weil zwei Listen je höchstens 1/61 beitragen. Werte um 0,031 heißen also: in beiden Listen ganz oben.

Zwei Anmerkungen. In Schritt 5 steht das Abkommen selbst (Chunk 73147, cosine 0,6437, score 0,031498) auf Rang 2, das Lehrbuch auf Rang 1. In Schritt 7 stand der beste Treffer auf Rang 2, der Treffer auf Rang 1 steht nicht in meiner Aufzeichnung.

### Das Rauschen

In Schritt 1 kamen unter den acht Treffern vier, die nicht passten: eine Vorschrift zu Fondsanteilen, eine Grunderwerbsteuer-Vorschrift, die "sieben Jahre" in anderem Zusammenhang verwendet, eine Norm aus dem Umwandlungssteuerrecht und eine aus dem Erbschaftsteuerrecht. In Schritt 5 kamen zwei Treffer zum Abkommen mit Südafrika, also zum falschen Abkommen, dazu ein Schreiben zum Arbeitslohn.

Aussortiert hat sie das Lesen: Welche cosine und welchen score sie hatten, steht nicht in meiner Aufzeichnung. Sie sind sichtbar im Bericht aufgeführt, damit ich sehe, was Claude verworfen hat und warum. Ein Bericht, der nur das Passende zeigt, verschweigt, wie viel Zufall in der Auswahl steckte.

### Die zwei Lücken und die Nachbarstelle

Bei Schritt 4 meldete das Lücken-Feld zwei fehlende Nachbarn. Der erste, Chunk 16549, die Fortsetzung des Gesetzes mit der Verlängerung der Rückkehrfrist, stand bereits in Schritt 1 auf Rang 2 und war gelesen. Der zweite, Chunk 8794 aus dem Urteil I R 55/19, wurde mit `stelle(8794)` geholt. Er enthält die Begründung, warum die Ausnahme erfüllt war: Der Kläger kehrte fristgerecht zurück, veräußerte nicht und war bei der Rückkehr nicht im Ausland ansässig.

Die Nachbarstelle ist Schritt 2: `stelle(16547)` lieferte § 6 Abs. 1 mit den drei Auslösern der Wegzugsbesteuerung. Ohne diese Stelle hätte die Aussage gefehlt, dass der Absatz 2 für alle drei Auslöser gilt.

### Der Befund

Die Aussagen aus dem Bericht, ohne Beträge und ohne Namen von Beratern:

| Aussage | Fundstelle | Stufe |
|---|---|---|
| Entscheidend ist das Datum der Beendigung der deutschen Steuerpflicht. Erfasst sind Personen, die in den letzten zwölf Jahren insgesamt mindestens sieben Jahre unbeschränkt steuerpflichtig waren. Wer vor dieser Grenze geht, löst die Wegzugsbesteuerung nach dem Wortlaut nicht aus. Das gilt für alle drei Auslöser | AStG § 6 Abs. 1 und 2, Chunk 16547 und 16548 | sicher |
| Frühere deutsche Wohnsitzzeiten zählen mit ("insgesamt"). Ob und wie lange es sie vor 2020 gab, steht nicht im Brain | Chunk 16548 | unsicher, Lücke |
| Nach der Grenze: Besteuert wird der gemeine Wert der Anteile abzüglich der Anschaffungskosten. Der Wert zum Stichtag ist nicht im Brain | EStG § 17 Abs. 2, Chunk 62438; BFH II R 2/24, Chunk 70718 | mittel |
| Der Steuersatz von rund 28,5 Prozent des gemeinen Werts ist eine Rechnung des Modells. Der 60-Prozent-Anteil des Teileinkünfteverfahrens stand in keinem Treffer, er ist Standardwissen des Modells | Rechnung aus Gesetzeswerten | unsicher |
| Zahlung auf Antrag in sieben Jahresraten, in der Regel nur gegen Sicherheit. Sofort fällig bei Veräußerung oder bei Ausschüttung über einem Viertel des Werts | AStG § 6 Abs. 4, Chunk 16550; Anwendungserlass, Chunk 19126 | sicher |
| Rückkehr innerhalb von sieben Jahren: Der Anspruch entfällt. Das Finanzamt kann um höchstens fünf Jahre verlängern. Die Rückkehrabsicht muss beim Wegzug nicht nachgewiesen werden | Chunk 16548 und 16549; BFH I R 55/19, Chunk 8793 und 8794 | sicher |
| Die alte Wegzugsklausel im Abkommen (Art. 13 Abs. 6) ist aufgehoben. Deutschland besteuert deshalb über das nationale Gesetz, nicht über das Abkommen | Abkommen DE-AT, Fassung 2026-09-21, Chunk 73147 | sicher |
| Österreich wertet die Anteile beim Zuzug auf den gemeinen Wert auf und besteuert danach mit 27,5 Prozent. Dieselbe Wertsteigerung wird nicht doppelt besteuert | EStG 1988 § 27 Abs. 6, Chunk 68723; EStR Rz 6158a bis c und Rz 6230, Chunk 43170 und 43347 | mittel, Schluss aus drei Stellen |
| Beteiligungen an Personengesellschaften, Immobilien, Wert der Holding zum Stichtag | nicht im Brain | unsicher, offen |

Das Ergebnis in einem Satz: Das Datum entscheidet, nicht der Umzug selbst.

Der Bericht widerspricht auch einem früheren Stand. Frühere Notizen von mir stützten sich auf Web-Beiträge und hielten die alte Wegzugsklausel im Abkommen noch für geltend. Das Brain hat den Wortlaut des Abkommens in der Fassung vom 21.09.2026 und die Anmerkung zur Aufhebung. Zwischen "ein Blogbeitrag sagt" und "der Gesetzestext sagt, Chunk 73147" liegt der Unterschied, um den es geht.

Der Befund ist eine Vorlage für Steuerberater, kein Rat. Er sagt auch, was fehlt: den Wert der Gesellschaft zum Stichtag, frühere Wohnsitzzeiten, die Behandlung der Personengesellschaften.

## Beispiel 2: Der Bankfall, kurz

Dieselbe Technik am Fall aus dem Vortrag: Meine Bank forderte 40.700 Euro Rückstand. Ich fragte erst die KI allein, ob ein Bürge schon vor der Kündigung des Darlehens haftet. Antwort: nein, erst nach der Kündigung. Klang vernünftig, ohne Quelle.

Dann dieselbe Frage an das Rechts-Brain. Antwort aus dem Kommentar von Erman zum BGB, § 765, Randnummer 38: Wer selbstschuldnerisch bürgt, haftet, sobald die Bank ihr Geld fordert. Eine Kündigung braucht es nicht. Die erste Antwort war nicht ungenau, sie war falsch. Gesehen habe ich es nur, weil zwei Antworten nebeneinander lagen, und ich die Stelle aufschlagen konnte.

Das Brain sagte noch mehr: Verjährung ist kein Hebel, das Zögern der Bank zieht nicht. Bleibt ein Argument, der Aufschub der Bank. Ein gutes System sagt auch, was nichts bringt.

## Der Unterschied

Die KI allein hätte mir die falsche Antwort mit voller Sicherheit gegeben, und ich hätte meine Verhandlung darauf gebaut. Das Brain hat die Antwort nicht besser formuliert. Es hat eine Stelle genannt: Buch, Paragraf, Randnummer, Chunk-Nummer. Bei der Wegzugsfrage ist es dasselbe, nur mit 58 Treffern statt einem. Jede Aussage hat eine Nummer, jede Nummer lässt sich aufschlagen.

Der Unterschied ist nicht die Antwort, sondern dass jeder Fehler nachschlagbar ist.

## Was hier offen ist

- Ein Vergleichslauf derselben Wegzugsfrage als Shallow-Suche (eine Suche, acht Treffer) wurde nicht gemacht. Wie viel eine einzelne Suche gefunden hätte, ist nicht gemessen.
- Die Gesamtdauer eines Deep-Laufs ist nicht gemessen.
- Das steuerliche Ergebnis ist Vorlage, nicht geprüft von einem Berater. Der 60-Prozent-Anteil im Steuersatz stammt nicht aus dem Brain.
- Für den Bankfall gibt es keine eigene Messung. Die 82 Prozent aus [Messen und verbessern](07-messen-und-verbessern.md) gelten für das Geschichts-Brain, das Recht-Brain trifft bei 16 von 20 Fragen die Stelle in den Top 8.
- Die Zahlen cosine und score zu Schritt 2 und zum Treffer auf Rang 1 in Schritt 7 stehen nicht in meiner Aufzeichnung.
