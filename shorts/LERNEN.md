# Fehler-Log & Verbesserungen – vor JEDEM Video lesen, nach JEDEM Video ergänzen

## Arbeitsweise (ohne dass der Nutzer es sagen muss)
1. `STIL.md` und diese Datei komplett lesen
2. Video Bild für Bild ansehen (0,2-s-Schritte bei Handlungen) – **erst dann** Skript schreiben
3. Skript gegen Checkliste unten prüfen
4. Bauen → Selbst-Review (unten) → erst dann abgeben
5. Nach Feedback: Fehler hier eintragen + Regel/Tool anpassen, damit er nie wieder passiert
6. Jedes Video mindestens **eine neue Verbesserung** ausprobieren (Liste „Nächste Stufe“) und im Ergebnis nennen

## Fehler, die passiert sind – nie wiederholen
| Video | Fehler | Ursache | Regel/Fix |
|---|---|---|---|
| 2 | Immer derselbe Sound (Peitsche) | Sounds nur nach Spektrum geraten, absichtlich gleich | eigene benannte Bibliothek, `@gruppen` rotieren |
| 2 | Hype-Stimme bei trauriger Story | Stimmung nicht beachtet | Stimme nach Stimmung wählen |
| 2 | Pausen in der Stimme, nicht dynamisch | zu vorsichtig gekürzt | Pausen raus, Tempo +12–15 % |
| 2 | Kreise IN der Person statt drumherum | Position geschätzt | Gesichtserkennung/Messen, Kreis umschließt |
| 3 | Kreis auf Publikum, Pfeil auf Logo | Gesichtserkennung bei kleinen/seitlichen Personen | Hand-Messung aus Raster-Standbild |
| 3 | Fakten („200 Meter“, „17 Jahre“) unbelegt | aus Erinnerung geschrieben | nur Belegtes ins Skript |
| 4 | Kreis folgt falschem Objekt | falscher Startpunkt | Startpunkt messen, Anfang/Mitte/Ende prüfen |
| 5 | Tracker driftet bei Schwenk | CSRT kommt nicht mit | Keyframes |
| 6 | „drückt ihm in die Hand“ – falsch | Handlung nicht geprüft | jede Handlung Bild für Bild prüfen |
| 6 | „reißt die Tüte auf“ – falsch | dito | dito |
| 6 | Satz eingeklebt → Wortreste hörbar | Satzgrenze nur geschätzt, nicht hörbar | Stimme immer komplett neu erzeugen |
| 6 | Pfeil läuft in nächste Szene | neue Stimme verlängert Shot | Overlays automatisch auf Shot gekürzt |
| 6 | Shot läuft über Schnitt im Original | dito | `cut.py` warnt |

## Skript-Checkliste
- [ ] Hook in den ersten 1,5 s: Schock/Zahl/Widerspruch, wirft eine Frage auf
- [ ] Jede beschriebene Handlung ist im Video sichtbar (Zeit notiert)
- [ ] Keine erfundenen Fakten über echte Personen
- [ ] Pointe/Auflösung erst am Ende (HPC)
- [ ] Kommentar-Auslöser, andere Art als im letzten Video
- [ ] Das Wort, das etwas benennt, liegt genau auf dem Bild
- [ ] Stimme passt zur Stimmung

## Selbst-Review vor Abgabe
- [ ] Ganzes Video in 0,5-s-Schritten angesehen: richtige Bilder, keine fremden Szenen, keine Titel/Wasserzeichen
- [ ] Jedes Overlay Anfang/Mitte/Ende: umschließt/zeigt richtig, verdeckt nichts, bleibt im Shot
- [ ] Keine `cut.py`-Warnungen
- [ ] Untertitel mit exakten Wortzeiten
- [ ] Sounds passen zum Inhalt, keine Wiederholung, leiser als Stimme
- [ ] Musik ~11 dB unter Stimme, Gesamt ~ −15 LUFS

## Nächste Stufe – Verbesserungen, die ich nach und nach einbaue
- [ ] **Hook-Bild zuerst:** das krasseste Bild 0,5 s als erstes Bild (Neugier), dann Story von vorne
- [ ] **Hook-Text oben im Bild** in den ersten 2 s (zweite Ebene neben dem Untertitel)
- [ ] **Loop-Ende:** letztes Bild/letzter Satz führt nahtlos in den Anfang → Video läuft automatisch nochmal
- [ ] **Pattern-Interrupts** alle 2–3 s (Mini-Zoom, Flash, Shake bei Pointen)
- [ ] **Schnitte auf den Musik-Beat** legen
- [ ] **3 Hook-Varianten** schreiben und die stärkste nehmen (Titel/Hook mit vidIQ bewerten, kostet Credits)
- [ ] **Emoji-Pops** an Schlüsselwörtern
- [ ] **Nach dem Upload:** Kanal-Zahlen mit vidIQ prüfen → was lief, was nicht → hier eintragen
