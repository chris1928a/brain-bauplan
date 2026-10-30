# 1. Warum ein Brain

Eine KI wird nicht klüger, wenn sie eine Bibliothek bekommt, sie wird belesener, und jede ihrer Antworten nennt Buch und Seite, an denen ihr nachprüfen könnt.

## Die KI klingt sicher, auch wenn sie rät

Ihr habt ChatGPT oder Claude sicher schon etwas gefragt, bei dem ein Fehler Geld kostet. Die Antwort kam sofort, klar und ohne Zögern, und genau das ist die Gefahr.

Eine Studie (Dahl u. a. 2024, zitiert in Jurafsky und Martin, Speech and Language Processing) hat Sprachmodelle zu konkreten Urteilen befragt. In 69 bis 88 Prozent der Fälle war die Antwort erfunden. Grob gesagt: drei von vier. Schlimmer als die Zahl ist, dass ihr es nicht seht: Es gibt keine Quelle und keinen Paragrafen, und Treffer und Fehler klingen gleich.
## Muster statt Text

Warum erfindet die KI? Nicht, weil sie zu wenig gelesen hat, denn Llama 3 wurde mit 15 Billionen Token trainiert (ein Token ist ein Wortteil), das sind rund 200 Millionen Bücher. Aber das Modell speichert keinen dieser Texte, sondern Muster: welches Wort nach welchem kommt (Mollick, Co-Intelligence). In diesem Topf liegen das Urteil und der Forenpost darüber übereinander, und das Modell hat kein Gefühl dafür, wann es weiß und wann es rät. Es antwortet in beiden Fällen gleich.

Dazu kommt ein Effekt, den die Forschung Schneeball-Halluzination nennt (Zhang u. a. 2023, zitiert bei Huyen, AI Engineering). Das Modell schreibt Wort für Wort, und jedes neue Wort baut auf den vorherigen auf, auch auf den eigenen. Biegt es im ersten Satz falsch ab, behandelt es diesen Satz als gegeben und baut darauf weiter. Von allein kommt es innerhalb derselben Antwort nicht zurück.

Deshalb entscheidet sich fast alles, bevor das erste Wort fällt: Was liegt auf dem Tisch, wenn die KI anfängt?

## Beleg statt Meinung

Ich habe mich gefragt, wie ich selbst lerne, und bei mir ist es wie bei den Besten in jedem Fach: erst Theorie aus Büchern, dann Praxis in Firmen und Fällen, dann die eigene Erfahrung, vor allem die eigenen Fehler. Jede Schicht hat eine Quelle, und ich weiß, aus welchem Buch ein Satz kommt.

Ein Beispiel. Ich frage zweimal dasselbe: Was bringt Coaching im Vertrieb? Die erste Antwort kommt von der KI allein und beruft sich auf unbenannte Studien, die Coaching für wichtig halten. Das klingt gut, aber welche Studien sind gemeint? Die zweite Antwort kommt mit meiner Bibliothek: Training teilt Wissen, Coaching bringt es in die Anwendung, laufend und je Person. Dahinter steht, wer das sagt und wo: Dixon und Adamson, The Challenger Sale, Stelle 7094. Beide Antworten sagen fast dasselbe, aber nur bei der zweiten kann ich nachschlagen.

Ohne Quelle ist eine Antwort eine Meinung.

## Was ein Brain tut

Stellt euch einen Bibliothekar vor. Ihr kommt mit einer Frage, er geht an die Regale und holt genau acht Stellen, nicht das ganze Regal. Die legt er der KI hin, bevor sie den ersten Satz schreibt, und sie soll nur daraus antworten, mit Quelle. Das Fachwort dafür ist RAG: nachschlagen, mitgeben, antworten.

Die Bücher liegen als Textausschnitte vor, jeder etwa eine Buchseite groß, mit Buch, Autor und Seite. Wie ein Buch hineinkommt, steht in [Kapitel 5](05-einlesen-und-index.md), wie die Suche arbeitet in [Kapitel 6](06-suche.md).

Eine Garantie ist das nicht. Die KI ist nicht gezwungen, den Stellen zu folgen, und unpassende Stellen können die Antwort verschlechtern (Self-RAG, Asai u. a.). Deshalb gehört die Messung zum System, siehe unten und [Kapitel 7](07-messen-und-verbessern.md).

## Acht Brains statt ein Topf

Ich habe nicht eine Bibliothek gebaut, sondern acht, eine je Lebensbereich: Geschichte, Business, Technik, Geld und Steuern, Psychologie, Musik, Recht, Familie. Wenn ihr nach Steuerrecht fragt, soll die Antwort nicht von einem Buch über Schamanismus verwässert werden. Claude fragt immer das Regal, das gerade passt.

Die Zahlen: Das Register zählt am 30.10.2026 insgesamt 13.888 Zeilen. Darin stecken 1.534 Zusammenfassungen, die eine KI erzeugt hat. Im Vortrag nenne ich gut 12.000 Quellen, das ist der Stand vom 16.10. ohne Zusammenfassungen. Dazu kommen 1.028.148 Textstellen, ebenfalls Stand 16.10. Technisch ist es ein Programm für alle acht.

## Messen statt hoffen

Wie oft liegt das System daneben? Ich habe 60 Testfragen, deren richtige Fundstelle ich kenne. Gemessen am 03.09.2026, vorher und nachher, nach drei Korrekturen am Suchverfahren:

- Richtige Stelle auf Platz 1: von 43 auf 53 Prozent.
- Richtige Stelle unter den acht Treffern: von 70 auf 82 Prozent.

Bei vier von fünf Fragen liegt die richtige Stelle also auf dem Tisch. Bei den übrigen 18 Prozent fehlt sie, und die KI antwortet aus den falschen Seiten, schreibt aber dazu, aus welchem Buch und von welcher Seite. Ich schlage auf und sehe in einer Minute, ob es stimmt. Bei ChatGPT prüfe ich alles, beim Brain eine Stelle.

Nicht null Fehler. Sichtbare Fehler.

Gelernt habe ich das im August 2026. Das System meldete: fertig. Ich zählte nach, und der Index kannte nur 171 von 454 Registerzeilen, fast zwei Drittel fehlten. Seitdem gilt: Eine Erfolgsmeldung ist kein Beweis. Nach jedem Einlesen läuft eine Inventur, und jede Antwort nennt den Stand des Katalogs.

## Der Bankfall

Im Oktober kam ein Brief meiner Bank: 40.700 Euro Rückstand, nachzuzahlen in vier Raten, die letzte im Mai. Dahinter standen ein Vertrag und rund sechzig Mails. Meine Frage: Stimmt das, und was kann ich tun?

Ich fragte zuerst die KI allein. Sie antwortete, Bürgen haften erst, wenn die Bank das Darlehen kündigt. Das klang vernünftig, nannte aber keine Quelle, und ich hätte meine Verhandlung darauf gebaut.

Dann stellte ich dieselbe Frage dem Brain. Die Antwort kam aus dem Kommentar: Erman, BGB, § 765, Randnummer 38. Wer selbstschuldnerisch bürgt, haftet, sobald die Bank ihr Geld fordert. Eine Kündigung braucht es nicht. Die erste Antwort war nicht ungenau, sie war falsch, und ich habe den Fehler nur gesehen, weil zwei Antworten nebeneinander lagen.

Der Rest ist Verhandlung. Die Bank schlug eine Monatsrate von 9.600 Euro vor, mein Angebot liegt bei 3.245 Euro. Die Antwort an die Bank liegt im Entwurf, entschieden ist nichts. Das Brain hat den Anwalt nicht ersetzt, sondern das erste Gespräch mit ihm: Ich komme mit einer fertigen Akte. Das ist kein Rechtsrat.

## Was ein Brain nicht kann

- Es garantiert nicht, dass die Antwort stimmt, sondern eine Fundstelle, die ihr prüfen könnt.
- Es kennt nur, was eingelesen ist. Eine Nullmeldung heißt nicht, dass die Antwort im Fachgebiet nicht existiert (mehr dazu in [Kapitel 8](08-anschluss-claude-mcp.md)).
- Es ersetzt keine Fachleute. Es ist ein zweiter Blick, der nie müde wird.

## Was hier offen ist

- Die 82 Prozent stammen aus dem Geschichts-Brain. Für das Rechts-Brain habe ich nur 20 Prüffragen: richtige Stelle in 16 von 20 unter den ersten acht, in 10 von 20 auf Platz 1.
- Die 82 Prozent messen, ob die richtige Stelle auf dem Tisch liegt. Ob die KI daraus richtig antwortet, habe ich nicht getrennt gemessen. Die 69 bis 88 Prozent messen etwas anderes, nämlich den Anteil erfundener Antworten. Beide Zahlen sind nicht direkt vergleichbar.
- Die Testfragen stammen zum Teil aus Treffern des damals laufenden Systems. Ein getrenntes Prüfset gibt es nicht ([Kapitel 7](07-messen-und-verbessern.md)).
- Für den August nennen meine Dokumente 283 und 286 fehlende Quellen, darum "fast zwei Drittel".
- Die Studie von Dahl u. a. kenne ich nur aus einem Lehrbuch.
- Der Bankfall läuft noch. Wie er ausgeht, weiß ich nicht.
