# Stil-Regeln für Shorts (Vorbild: ClipErklärt)

Analysiert aus dem Referenzvideo „Das Letzte schockiert alle Deutschen“ (24,9 s).

## Aufbau
- Länge **18–25 Sekunden**, nie über 30
- **Hook in Satz 1**: Zahl + Schock-Wort („Dutzende Polizisten…“, „3 Dinge aus Japan, die Deutsche komplett schockieren“)
- Erstes Bild = das krasseste Bild des ganzen Videos
- **Falsche Fährte** oder Frage nach 2–4 s („Was hat dieser Junge getan?“ – „Nichts.“)
- Bei Listen: Halteformel in der Mitte („Aber das Beste kommt noch.“)
- Harter Schluss, kein Outro → Video läuft in Schleife

## Schnitt
- **Neuer Shot alle 1–1,5 s** (Referenz: 24 Schnitte in 25 s)
- Jeder Satz = eigenes Bild, das genau zeigt, was gesagt wird
- Logos/Wasserzeichen wegschneiden oder verwischen
- Original-Ton stumm

## Text
- **Ein Wort pro Einblendung**, Font **Bangers**, groß (~195), weiß mit dickem schwarzem Rand, Bildmitte
- Kurzer Pop-Effekt beim Einblenden
- Schlüsselwörter gelb

## Grafik
- **Viele animierte Kreise und Pfeile** (ca. alle 1–2 s eins), Stile aus `tools/fx.py`:
  circle_red (wird gezeichnet, pulsiert), circle_yellow (handgemalt, wackelt), circle_glow (Leuchtring, ploppt),
  arrow_red (fliegt rein, federt), arrow_yellow (gebogen, wird gezeichnet), arrow_white (handgemalt, wackelt)
- **Nie zweimal derselbe Stil hintereinander**; Kreise können mitwandern (x_end/y_end)
- **Automatische Platzierung** (`tools/track.py`, Gesichtserkennung): Overlay bekommt `target: "face"` + grobe `hint`-Position
  - Kreis wird so groß gerechnet, dass er das Gesicht **UMSCHLIESST** (nie draufliegt)
  - Pfeilspitze endet **VOR** dem Gesicht und zeigt auf die Mitte; bleibt immer im Bild
  - Gesicht füllt fast das Bild (r > 200 px) → **kein Pfeil** (würde verdecken), wird automatisch entfernt
  - Keine Overlays während Zooms
- **Gesichtserkennung nur als Hilfe:** klappt bei frontalen, großen Gesichtern (Polizei-Video), versagt bei kleinen
  oder seitlichen Personen (Marathon: Kreis auf Publikum, Pfeil auf Logo). Dann Position **von Hand** aus Standbild messen.
- Nach jedem Render: Standbild aus der Mitte **jedes** Overlays prüfen – falsch platziert = neu setzen, nie so abgeben
- Pfeil/Kreis muss zum **gesprochenen Text** passen (wer gerade gemeint ist: „ein Mädchen greift ein“ → Pfeil auf die Helferin)
- Kurze Punch-Zooms auf Schlüsselsätze

## Sound
- Eigene Sound-Bibliothek: `sfx_lib/` (27 Sounds, ElevenLabs, Namen = Inhalt), Lautstärken in `library.json`
- **Sounds passend zum Skript** (`themes` in library.json): Polizei → Sirene/Funk, Schule → Schulglocke,
  Tod/Trauer → Totenglocke/Herzschlag/Piano, Gehen → Schritte, Ehre → Applaus, Schock → Boom/Bass-Drop/Raunen,
  Foto → Blitz/Auslöser, Happy End → Shimmer/Swell/Piano
- Jedes Video: mindestens 5 Themen-Sounds + Übergänge + Akzente
- **Gruppen statt Einzelsounds** (`@transition`, `@accent`, `@impact` …) → Script wechselt automatisch, **nie zweimal derselbe hintereinander**
- Whoosh startet kurz vor dem Schnitt (Vorlauf), damit er genau auf dem Schnitt peakt
- Lautstärke immer unter der Stimme; Spannung (Tick) besonders leise
- Nicht jeder Schnitt braucht einen Sound – ca. jeder zweite
- **Whoosh bei Schnitten**
- Klick, wenn Kreis/Pfeil erscheint
- Boom bei der Wendung („Nichts.“, „starb“)
- Ding/Chime bei Highlight und Schluss
- Durchgehend Musik darunter (Referenz hat keine einzige Stille)
  - Eingebaut über `music` in der Config: ca. **15 dB unter der Stimme** (gain_db −14), **Ducking** unter der Stimme
  - Nur Instrumental-Stellen nehmen (kein Gesang, der mit der Stimme kollidiert)
  - Gesamtlautheit ~ −14 LUFS (YouTube-Norm)

## Stimme (nach Stimmung wählen!)
- **IMMER dynamisch, KEINE Pausen** – auch bei traurigen Storys. Pausen auf 0,05 s kürzen, Tempo +12 %
- Prompt-Tags: [fast-paced, intense, dynamic storytelling, no pauses]
- **Emotional / traurig:** „Rob – Warm Bass German Narrator“ (Klangfarbe warm, Tempo trotzdem schnell)
- **Fakten / Listen / lustig (Japan-Stil):** „Christian Plasa – Dynamic and Vibrant“
- Modell eleven_v4
- ~3,8 Wörter pro Sekunde

## Aufbau nach HPC (aus „How to make shorts that go viral“)
- **H**ook (0–5 s): schnell, keine Pause, wirft Fragen auf
- **P**rogression: liefert, was der Hook verspricht
- **C**limax: Auflösung erst am Ende – nie zu früh verraten
- Posten: 1× pro Tag, zur Uhrzeit, wenn die Zuschauer aktiv sind (YouTube Studio → Zielgruppe)

## Mitbewegen (Tracking) – Standard für JEDEN Kreis/Pfeil
- `tools/track.py follow_path`: CSRT-Tracker verfolgt das Ziel Bild für Bild, geglättet; Overlay wandert + skaliert mit
- Kreis: Startpunkt = Mitte des Ziels (x, y), `track_box` = Größe des Ziels
- Pfeil: `track: [Ziel-x, Ziel-y, Ziel-Größe]`, Spitze (x, y) behält ihren Abstand zum Ziel
- **Startpunkt immer aus Raster-Standbild messen** (nicht schätzen) – falscher Start = Kreis folgt dem falschen Objekt
- **Keyframes statt Tracker**, wenn die Kamera schnell schwenkt oder eine Person das Bild füllt (Tracker driftet dann ab):
  `keys: [[t, x, y, scale], ...]` an 3–4 Zeitpunkten aus Raster-Standbildern messen → weich interpoliert
- Overlay nie über einen Schnitt hinweg
- **Prüfen: Anfang, Mitte UND Ende jedes Overlays** – Kreis muss UM das Ziel liegen, Pfeil darf nichts verdecken

## Qualität – nie schlechter als das Original
- Zwischenschnitt fast verlustfrei (CRF 6), Endvideo CRF 16 / preset slow
- Zooms als Punch-in im Schnitt (`punch_at`) aus den **Originalpixeln**, kein zoompan auf das fertige Bild
- Hochskalieren mit Lanczos, bei starker Vergrößerung leicht nachschärfen
- Auflösung kann nicht besser werden als die Quelle → immer die beste verfügbare Version des Clips nehmen

## Clips mit Titel/Rahmen (z. B. „Mr. Bean in real life“)
- Nur den echten Videobereich ausschneiden (`y`/`h` im Shot), Titelbalken und schwarze Ränder weg
- Wasserzeichen mit `delogo` entfernen
- Satzgrenzen der Stimme mit `tools/align.py` finden (Stimme hat keine Pausen mehr)

## Kommentar-Auslöser (im Skript eingebaut, NIE „kommentiere für mehr“)
- Jedes Skript bekommt einen Auslöser, meist als letzter Satz (Video endet hart → Loop)
- **Abwechseln**, nie zweimal dieselbe Art hintereinander:
  1. Steile These („Ehrlich? Er hat alles richtig gemacht.“) → Widerspruch
  2. Offene Lücke („Was sie danach sagte, hat keiner gehört.“) → Vermutungen
  3. Wiedererkennung („Jeder hat so einen Opa.“) → Markieren/„genau so!“
  4. Leichte Frage, selten („Wie hättest du sie genannt?“) → in 2 Sekunden beantwortbar
  5. Mittendrin-Twist („Bis hierhin dachte jeder…“)
- Bei traurigen Storys keine Provokation – Wiedererkennung/Gänsehaut statt These
- Keine absichtlichen Fehler als Köder

## Eingebrannter Text im Clip
- Text verwischen (`blur: [x, y, w, h]` im Shot, Quell-Pixel) und eigene Untertitel genau darauf setzen (`caption_y`)
- Zeitlupe (`speed: 0.5–0.6`) für Pointen/Reveals, wenn die Stimme länger ist als die Szene – Quelle am besten 60 fps
