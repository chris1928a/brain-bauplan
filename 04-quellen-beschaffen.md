# Quellen beschaffen

Zwanzig Bücher kosten rund 600 bis 1.100 Euro, das Einlesen kostet daneben fast nichts, und alles, was ihr kauft, bleibt auf eurer Platte.

## Kanäle, Formate, Preise

Der Einlesevorgang braucht eine Datei ohne Kopierschutz (DRM, ein Schloss, das den Text für fremde Programme sperrt). Das entscheidet über den Shop, nicht der Preis. Die Preise sind Schätzungen aus einer Kaufliste, nicht im Shop geprüft.

| Kanal | Format | Richtpreis je Titel | Hinweis |
|---|---|---|---|
| InformIT (Addison-Wesley, Pearson) | EPUB und PDF | rund 25 bis 45 Euro, Schätzung | ohne DRM, mit Wasserzeichen |
| Pragmatic Bookshelf | EPUB, PDF | rund 40 Euro, Schätzung | ohne DRM |
| No Starch Press | EPUB und PDF | rund 45 Euro, Schätzung | ohne DRM |
| Manning | EPUB und PDF | nicht beziffert | ohne DRM |
| O'Reilly über ebooks.com | EPUB und PDF | rund 45 bis 55 Euro, Schätzung | Wasserzeichen, keine DRM-Sperre; das Lernportal im Abo bietet keinen Download und hilft dem Brain nicht |
| Amazon Kindle, Eigenverlage | EPUB | rund 15 Euro, Schätzung | meist mit DRM. Seit 20.01.2026 dürfen Verlage bei Amazon DRM-frei anbieten, dann steht es im Shop dabei |
| Wiley, IT Revolution | EPUB | nicht beziffert | meist mit DRM, dann nicht verwendbar |
| Akademische Verlage direkt | PDF oder EPUB | nicht beziffert | oft ohne DRM, vor dem Kauf nachfragen |
| Humble Bundle (Buchpakete) | oft PDF, EPUB | rund 15 US-Dollar je Paket, Schätzung | Pakete mit mehreren Büchern, DRM-Freiheit je Paket prüfen |
| Print plus Scan | eigener Scan | Buchpreis, bei Rechtsliteratur etwa 75 bis 190 Euro je Kommentar | siehe unten |
| Freie Quellen (Gesetze, Urteile, Papers) | PDF, HTML | 0 | Lizenz ins Register, siehe [Quellen finden](03-quellen-finden.md) |

Zur Spalte "Print plus Scan": Juristische Kommentare gibt es digital oft nur im Abo einer Datenbank, und die lässt sich nicht in ein Brain übernehmen. Dann bleibt das gedruckte Buch. Ob ein Scan des eigenen Exemplars erlaubt ist, hängt vom Fall ab. Das klärt ihr vorher mit eurem Anwalt (siehe unten).

## Was 20 Bücher kosten

Ein Technik-Brain mit 35 Titeln stand auf der Kaufliste mit rund 1.090 Euro, das sind rund 31 Euro je Titel. Eine kürzere Liste von 28 Titeln lag bei 600 bis 900 Euro, ein Musik-Brain bei 350 bis 450 Euro. Daraus folgt für euch: 20 Bücher kosten rund 600 bis 1.100 Euro. Die Streuung kommt vom Fachgebiet. Rechtsliteratur liegt am oberen Rand.

Das Einlesen daneben: Ein Buch ergibt rund 360 Textstellen (Chunks). Mit einem Cloud-Modell für die Kontextsätze (dazu mehr in [Einlesen und Index](05-einlesen-und-index.md)) kostet ein Buch rund 0,29 US-Dollar, 20 Bücher rund 5,80 US-Dollar. Auf eigener Grafikkarte kostet es nichts. Das ist gegenüber den Buchpreisen vernachlässigbar. Rechnet bei der Hardware-Frage in [Hardware](02-hardware.md) trotzdem mit, dass die Käufe nicht in der Zahl für Grafikkarte und Abo stecken.

## Was nach dem Kauf passiert

Aus der gekauften Datei muss reiner Text werden, und zwar mit Seitenzahlen. Das ist keine Kür: Ohne Seitenmarker kann das Brain später keine Seite nennen, und eine Antwort ohne Seite lässt sich nicht gegenprüfen.

- **EPUB:** Mit Calibre (`ebook-convert`) nach Textdatei umwandeln. EPUB hat keine festen Seiten. Setzt Marker nach Kapiteln.
- **PDF mit Textlayer:** Text mit PyMuPDF auslesen, pro Seite ein Marker `--- PAGE n ---`.
- **Scan ohne Textlayer:** OCR (Texterkennung) mit Tesseract, Sprache deu, 300 dpi. Für Fraktur gibt es ein eigenes Sprachpaket. Bei sauberen Scans lagen die Raten bei 787 von 788 und 2.397 von 2.398 erkannten Seiten.
- **Stichprobe:** Schaut euch Anfang, Mitte und Ende der Textdatei an, bevor ihr weitermacht. Kaputte Umlaute und verrutschte Spalten fallen sofort auf.

Danach folgt die Registerzeile. Der Vermerk "gekauft" im Register ist weder Datei noch Index: Sechs Titel galten in einem Bestand als gekauft und lagen noch ungelesen im Download-Ordner. Prüft nach dem Einlesen, ob die Datei im Index angekommen ist.

## Die Regeln

Diese Regeln gelten für jede Quelle, die nicht frei lizenziert ist.

1. **Nur die eigene Kopie.** Ihr nutzt eine Datei, die ihr selbst erworben habt, für euch.
2. **Lokal.** Datei, Textfassung und Index liegen auf eurer Platte oder einem Speicher, den nur ihr kontrolliert.
3. **Keine Weitergabe.** Weder die Datei noch ein Index, aus dem sich der Text rekonstruieren lässt, geht an Dritte.
4. **Vermerk im Register.** Schreibt in `provenienz` und `lizenz`, wie die Datei zu euch kam. Beispiel: "Buch, privat beschafft, nur lokaler Index, keine Weitergabe".
5. **Kein geschützter Volltext in einem Repo oder auf einem geteilten Laufwerk.** Das gilt für Git, für Cloud-Ordner mit Freigabe und für Team-Laufwerke. Setzt den Ordner mit den Textdateien und den Index in die Ausschlussliste (`.gitignore`).
6. **CC-NC und CC-ND heißt: lokal bleiben.** Die Lizenz erlaubt das Lesen, nicht das Weiterreichen. Der Index bleibt bei euch.
7. **Amtliche Werke und gemeinfreie Texte** (Gesetze, Urteile, Gutenberg) dürft ihr weitergeben, vermerkt aber die Lizenz.

## Was nicht geht

Schattenbibliotheken scheiden aus. Der Download von Kopien Dritter scheidet aus, auch wenn die Datei im Netz liegt. Scraping gegen die Nutzungsbedingungen einer Seite scheidet aus, auch wenn die Seite frei lesbar ist. Und DRM-Entfernung scheidet aus: Wer einen Titel mit Kopierschutz braucht, kauft die Ausgabe ohne. Gibt es sie nicht, bleibt der Titel außerhalb des Brains. Es gibt immer einen Ersatz, ein anderes Standardwerk, einen Aufsatz, ein Gesetz. Eine Lücke kostet weniger als ein Rechtsstreit.

Keine dieser Regeln ersetzt die rechtliche Prüfung. Ob eine Privatkopie in eurem Fall zulässig ist, ob das Auslesen für ein privates Suchsystem unter die Regeln zum Text- und Data-Mining fällt und wie die Lage bei Scans eigener Printbücher aussieht, ist Sache von euch und eurem Anwalt. Der Bauplan ist keine Rechtsberatung.

## Was hier offen ist

- Alle Buchpreise sind Schätzungen aus Kauflisten, nicht im Shop geprüft. Bei Rechtsliteratur sind es Ladenpreise der Printausgaben.
- Für Manning, wissenschaftliche Verlage, Wiley und IT Revolution gibt es keine Preisangabe.
- Die Rechnung "20 Bücher rund 600 bis 1.100 Euro" ist aus drei Kauflisten gemittelt, nicht aus einer Erhebung.
- Die rechtliche Zulässigkeit von Scans und von Text- und Data-Mining ist nicht geprüft.
- Die Stromkosten im Normalbetrieb sind nicht gemessen.
