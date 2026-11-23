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
| Analyse | Story-Videos zu hektisch geschnitten, zu viele Grafiken | Listen-Regel auf Storys übertragen | Tempo nach Format (STIL.md) |
| Analyse | Immer dieselbe Musik | bequem | Musik nach Stimmung, Swell am Höhepunkt |
| 7 (Selbst-Review) | Pfeil zeigte auf Kopf der Fotografin statt auf den Strauß | Position nur an einem Zeitpunkt gemessen | Pfeil-Keys an Anfang/Mitte/Ende messen, Pfeil von der freien Seite |
| 7 (Selbst-Review) | Braut im ersten Bild halb am Rand | Quelle zu früh gestartet | erstes Bild: Hauptperson ganz im Bild, sonst Quelle später starten |
| 7 | Like-Satz am Ende („gab diesem Video ein Like“) | aus Analyse übernommen | Nutzer will das NICHT → kein Like-Satz, nie |
| 7 | Eigene KI-Musik | Musik nach Stimmung probiert | **Standard: Golden Brown**, bis der Nutzer andere Musik schickt |
| 8 (Remakes) | **Stimme hackt** – nicht flüssig | tighten.py schneidet zwischen JEDEM Wort, kappt Wortenden | **Stimme am Stück lassen** (`smooth.py`: nur atempo 1.1, kein Schneiden). tighten.py nicht mehr benutzen |
| 8 (Remakes) | Dünne Ringe + Namensschilder + Farbblitze = „nicht clean“ | eigenes neues Design ohne Rückfrage | Bewährte animierte Kreise (fx.py) behalten, nur Bewegung per Tracking verbessern. Kein Design-Wechsel ohne Nutzer |
| 8 (Remakes) | Mehrere Kreise gleichzeitig | zu viel | max. EIN Kreis gleichzeitig |
| 8 (Remakes) | Nur Kreise, 3× hintereinander auf dieselbe Frau | Pfeile weggelassen | Kreis/Pfeil strikt abwechseln, Pfeilspitze an der Kopfkante (0.95·r) |
| 8 Zwillinge | Gelber gebogener Pfeil sieht schlecht aus | Stil | neue Block-Pfeile (arrow_block/arrow_green), gelben nicht mehr nutzen |
| 8 Zwillinge | Nur 1 Baby markiert, Papa ohne Pfeil | nicht alle genannten Personen markiert | JEDE im Satz genannte Person bekommt Kreis/Pfeil genau beim Wort (bei „Zwillinge“ beide) |
| 11 | Originalton lauter als Stimme, Musik unhörbar, Untertitel anders als Konkurrenz, Unschärfe-Ränder | Kompressor zu schwach, Musik −17, eigene Schrift, Fit-Modus | Lautstärke-Kurve, Pegel messen, Montserrat wie Konkurrent, Vollbild |
| 11 v2 | „Lehrer dreht sich um“ – tut er nicht | Handlung nicht Bild für Bild geprüft | Skript nur Sichtbares |
| 11 v2 | Zu viele Kreise, Untertitel 3 Wörter, SFX zu brav | Konkurrent nicht genau umgesetzt | max 2 Wörter, 1–2 Pfeile, krasse SFX je Aktion |
| 12 | Man sah nicht, wie es dazu kam; Hook schwach | Setup weggelassen, direkt Tanz | Setup→Switch: erst Erwartung (ernster Security), dann Wendung |
| 7 (Selbst-Review) | `@transition` wählte „glitch“ bei rührender Story | Gruppe kennt keine Stimmung | bei emotionalen Storys Übergänge einzeln wählen (whoosh/swoosh), kein glitch |

## Skript-Checkliste
- [ ] Clip-Check zuerst: hat das Material selbst eine Mini-Geschichte mit Wendung + universelles Gefühl? Sonst anderen Clip
- [ ] Hook nach einer der 5 Formeln (ANALYSE.md), Hook-Satz = Titel
- [ ] Erstes Bild BEWEIST den Hook (+ Kreis/Pfeil drauf) – Versprechen ohne Bild = Flop
- [ ] Falsche Fährte/Mini-Twist eingebaut, wenn das Material es hergibt
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

## Ausprobiert
- Video 7: eigene Musik pro Video (ElevenLabs Music, ~900 Credits, Swell um 15 s = Höhepunkt), genau EINE Mini-Pause vor dem Twist
  (`PAUSE_AFTER="an:0.3"` in tighten.py), ~~Like-Satz~~ (abgelehnt), ~~eigene Musik~~ (abgelehnt), Story-Schnitt (9 Shots statt 20), Zeitlupe 0,5–0,6 bei Gefühl

## Nächste Stufe – Verbesserungen, die ich nach und nach einbaue
- [ ] **Hook-Bild zuerst:** das krasseste Bild 0,5 s als erstes Bild (Neugier), dann Story von vorne
- [ ] **Hook-Text oben im Bild** in den ersten 2 s (zweite Ebene neben dem Untertitel)
- [ ] **Loop-Ende:** letztes Bild/letzter Satz führt nahtlos in den Anfang → Video läuft automatisch nochmal
- [ ] **Pattern-Interrupts** alle 2–3 s (Mini-Zoom, Flash, Shake bei Pointen)
- [ ] **Schnitte auf den Musik-Beat** legen
- [ ] **3 Hook-Varianten** schreiben und die stärkste nehmen (Titel/Hook mit vidIQ bewerten, kostet Credits)
- [ ] **Emoji-Pops** an Schlüsselwörtern
- [ ] **Nach dem Upload:** Kanal-Zahlen mit vidIQ prüfen → was lief, was nicht → hier eintragen
| 12 Security v5 | Satz „Dann kommt dieser Typ…“ + Pfeil kamen erst, als er längst da war; Umschwung/„Security-Modus: aus“ kam erst nach Tanzbeginn | Timing | Erzähl-Block + Pfeil **auf das Bild-Ereignis legen** (Person tritt ins Bild = Satzstart ±0,2 s); Switch-Flash + Text genau auf das erste Tanz-Frame; vorher Frame-Sheet prüfen |
| 12 Security v5 | Gleicher Sound auf mehreren Pfeilen | Sound | Jeder Pfeil/Kreis/Sticker eigener kurzer Sound (iphone_ping, bloop, blub, sparkle, ding_bright, knock), Übergänge eigener Swoosh |
| 12 Security v6 | „fordert ihn heraus“ war falsch – im Bild bittet der Typ ihn zu gehen | Inhalt | Handlung im Clip genau ansehen (Gesten, wer schiebt wen), nicht raten; Satz nur schreiben, was eindeutig zu sehen ist |
| 12 Security v8 | Nach „Bewegung“ hörte man „Da…“ (Anfang vom nächsten Satz) | Stimme | Transkript-Zeiten sind oft zu spät → place_voice.py schneidet jetzt in die echte Stille (quiet_cut), danach Stimmspur auf Wortreste prüfen |
