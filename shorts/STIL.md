# Stil-Regeln für Shorts (Vorbild: ClipErklärt)

> **Vor jedem Video zuerst `LERNEN.md` und `ANALYSE.md` lesen** (Fehler-Log, Checklisten, Konkurrenz-Erkenntnisse).

Analysiert aus dem Referenzvideo „Das Letzte schockiert alle Deutschen“ (24,9 s).

## Aufbau
- Länge **18–25 Sekunden**, nie über 30
- **Hook in Satz 1**: Zahl + Schock-Wort („Dutzende Polizisten…“, „3 Dinge aus Japan, die Deutsche komplett schockieren“)
- Erstes Bild = das krasseste Bild des ganzen Videos
- **Falsche Fährte** oder Frage nach 2–4 s („Was hat dieser Junge getan?“ – „Nichts.“)
- Bei Listen: Halteformel in der Mitte („Aber das Beste kommt noch.“)
- Harter Schluss, kein Outro → Video läuft in Schleife

## Schnitt (Tempo nach Format – aus ANALYSE.md)
- **Listen/Fakten (Japan-Stil):** neuer Shot alle 1–1,5 s (Referenz: 24 Schnitte in 25 s)
- **Storys (ein Clip mit Handlung):** 5–10 Schnitte, Clip läuft, nur Langweiliges rausschneiden
  (Brad-Nolan-Hits mit 100+ Mio haben 4–9 Schnitte) – Tempo kommt dann von Stimme, Punch-ins und Sounds
- Jeder Satz = eigenes Bild, das genau zeigt, was gesagt wird
- Logos/Wasserzeichen wegschneiden oder verwischen
- Original-Ton stumm

## Text
- **Ein Wort pro Einblendung**, Font **Bangers**, groß (~195), weiß mit dickem schwarzem Rand, Bildmitte
- Kurzer Pop-Effekt beim Einblenden
- Schlüsselwörter gelb

## Grafik
- **Pflicht: Kreis/Pfeil im allerersten Bild** auf das Wichtigste (alle Top-Hits machen das)
- Listen: viele Kreise/Pfeile (ca. alle 1–2 s). Storys: 3–6 gezielt, nur wo es etwas zu zeigen gibt
- **Immer Kreise UND Pfeile abwechselnd** (K, P, K, P …): 3 verschiedene Kreise (rot/gelb/Glow) + verschiedene Pfeile: **arrow_block (cyan Sticker), arrow_green (grün Sticker), arrow_red, arrow_white** – arrow_yellow (gebogen) NICHT mehr benutzen (Nutzer mag ihn nicht) pro Video. Nie zweimal dasselbe hintereinander, nie 3× dieselbe Art auf dieselbe Person
- Stile aus `tools/fx.py`:
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
- **Nutzer-Standard: `sfx_gain: 0.45`** (Stimme soll klar heraustechen) (alle Sounds leiser), dafür MEHR Sounds: leiser Swoosh auf fast jedem Schnitt (gain 0.45), JEDER Kreis/Pfeil bekommt einen hörbaren, dezenten Sound (gain 1.6): Gruppen `circle_in` (blub, sparkle, scribble, bloop, pop, knock) und `arrow_in` (swish_soft, zip, arrow_thunk, swipe, slide_in, swoosh_air) – rotieren, pro Video anderer Startpunkt; andere leise Sounds ±0,3 s davon weg
- Nicht jeder Schnitt braucht einen Sound – ca. jeder zweite
- **Whoosh bei Schnitten**
- Klick, wenn Kreis/Pfeil erscheint
- Boom bei der Wendung („Nichts.“, „starb“)
- Ding/Chime bei Highlight und Schluss
- Durchgehend Musik darunter (Referenz hat keine einzige Stille)
  - **Musik-Lautstärke messen statt raten:** RMS des Musikausschnitts mit Golden Brown vergleichen (GB −16 dB RMS bei gain −10) und gain_db so setzen, dass der Pegel gleich ist (Headlights-Drop ist ~8 dB lauter → gain −18,5)
  - **Drop/Höhepunkt der Musik auf den Story-Höhepunkt legen** (music.start = Drop-Zeit − Höhepunkt im Video)
  - **Standard-Musik: Golden Brown** (`video2/music.mp3` im Arbeitsordner), bis der Nutzer andere Musik schickt – keine eigene KI-Musik
  - Eingebaut über `music` in der Config: ca. **15 dB unter der Stimme** (gain_db −14), **Ducking** unter der Stimme
  - Nur Instrumental-Stellen nehmen (kein Gesang, der mit der Stimme kollidiert)
  - Gesamtlautheit ~ −14 LUFS (YouTube-Norm)

## HYBRID-STIL (Standard ab Video 11, wenn der Clip echten Originalton hat)
- Video UND Story gleich wichtig: Stimme nur in 3–4 kurzen Blöcken (`tools/place_voice.py`, atempo 1.1), dazwischen spielt das Video
- **Originalton immer an** (`audio_out` in shots.json + `orig_audio` in config): voll in Pausen, unter der Stimme geduckt
- Spricht jemand im Video → KI schweigt, Übersetzung als \*Aktions-Text\* (Box im Original verwischen, Text genau drauf)
- Untertitel 1:1 wie @shortsrender (gemessen): `chunk`, Font **MontserratXB** (fonts/), Größe 78, y 1210, weiß + dünner Rand + Schatten, 1 Wort pink/gelb/cyan/grün; Aktions-Texte ganz cyan mit gelben Sternchen + Leucht-Rand
- Pop/Klick-Sound nur bei Aktions-Texten/Stickern, gesprochene Untertitel ohne Sound
- Stimme passend zum Konkurrenz-Stil: Laura (weiblich, amüsiert), atempo 1.12
- **Lautstärke (gemessen):** Stimme ≈ −20 dB RMS; Originalton unter Stimme −18 dB (Kurve `under_db`, nicht Kompressor), in Pausen `gain_db −4`; Musik `gain −9` (hörbar, ~10 dB unter Stimme)
- Vollbild 9:16 (kein Unschärfe-Rand); weiße TikTok-Textboxen mit `tools/debox.py` wegrechnen
- Übergänge (rings.py flash): Zoom-Punch + Licht-Glow – weiß bei Schnitten, pink bei Akt-Wechsel (strength 0.45), rot bei Wut
- Flashes via `rings.py` (nur flash/shake): weiß bei Szenen-/Akt-Wechsel, rot bei Wut/Pointe + Vine-Boom
- 2–4 Kreise/Pfeile (abwechselnd, getrackt) + 2–3 Emoji-Sticker
- Musik nur vom Nutzer (Golden Brown / Headlights), leise (gain −17), Kommentar-Auslöser in einem Stimmblock
- Clip-Check vorher: echter Originalton? sonst alter Stil

## Comedy-Videos 1:1 Stil @shortsrender (Nutzer-Wunsch: genau so, nicht mischen)
- Weibliche Stimme Laura `LB5G0Z4EP98YaEgL654m`, amüsiert, normales Tempo (atempo 1.0), Erzählung in 4 Blöcken mit Lücken für die Action
- `caption_mode: "chunk"`, Font Inter Black 92, y 1260: 1–3 Wörter, EIN Wort farbig (pink/gelb/cyan/grün rotierend)
- \*Aktions-Texte\* in den Lücken, groß, Wörter abwechselnd cyan/gelb/rot
- Kaum Grafik: 1 roter Pfeil im Hook, 2–3 Meme-Sticker, roter Flash + Vine-Boom bei Wut – KEINE Kreis/Pfeil-Serie
- Comedy-Pizzicato-Musik (gain −12,5), SFX laut (sfx_gain 0.75), Länge wie Original (~40 s)

## Comedy-Videos (alt, gemischt)
- `multicolor: true`, `actions` mit \*Aktions-Text\*, 3–6 Emoji-Sticker (style emoji, nie auf Gesichter), Comedy-Sounds bei Pointen (vine_boom, laugh, boing, slide_whistle, rubber_pull)
- Regel der Drei im Skript; Pointe = Autoritätsperson scheitert
- Eingebrannte Untertitel mit `tools/detext.py` entfernen

## Stimme (nach Kategorie wählen – feste Zuordnung)
- **Flüssig vor allem:** Stimme am Stück (`tools/smooth.py`, atempo 1.1). NIE zwischen Wörtern schneiden (hackt). Dynamik kommt über Tags „fast-paced, no pauses“
- Einzige Ausnahme: **eine** Mini-Pause (~0,3 s) direkt vor dem Twist (`PAUSE_AFTER`)
- Modell eleven_v4, Tags vorne im Text (Spalte „Tags“), ~3,8 Wörter pro Sekunde
- Hörproben aller Stimmen: `stimmen_hoerproben.mp4` – Nutzer-Feedback zu Stimmen hier eintragen

| Kategorie | Beispiele | Stimme (voice_id) | Tags |
|---|---|---|---|
| Rührend / Liebe / Wholesome | Hochzeit, Wiedersehen, gute Tat, Tier gerettet | **Rob** `5euSC8RarC3AHrZ242sr` (Alternative: Ekrem `RY3dTe57R8HXp7kzijeB`) | warm, emotional, fast-paced storytelling, no pauses |
| Traurig / Abschied / Tod | Hund stirbt, letzter Wunsch | **Ekrem** `RY3dTe57R8HXp7kzijeB` (tief, kinoreif) | emotional, soft but fast-paced, no pauses |
| Lustig / Fail / Prank | Mr. Bean, Katze, Missgeschick | **Christian Plasa** `nsFsExJHz4xV1sOX6Kdn` | funny, energetic, fast-paced, no pauses |
| Spannung / Schock / Mystery | „geriet in Panik“, Fund, Rätsel | **Axel** `ZPI4bKVkeIVdAkOA73qX` | suspenseful, intense, fast-paced, no pauses |
| Düster / Krimi / Gefahr | Polizei-Einsatz, Verbrechen, Unfall | **Anton** `Ay1WwRHxUsu3hEeAp8JZ` | suspenseful, dark, fast-paced, no pauses |
| Krass / Held / Rekord / Sport | Rettung, Mutprobe, „alle scheiterten“ | **Jan** `keqaIOtp0ePlmN5jgQfy` | hyped, energetic, fast-paced, no pauses |
| Gaming / Jugend / Hype | GTA, Schule, Teenager | **Timon** `0i5UT3fATBWphA0jBZug` | excited, energetic, fast-paced, no pauses |
| Frauen-/Mädchen-Perspektive | Mutter, Braut, Tochter, „Sie …“-Storys mit viel Gefühl | **Mila** `dCnu06FiOZma2KVNUoPZ` | emotional, warm, fast-paced, no pauses |
| Fakten / Listen (Japan-Stil) | „3 Dinge …“ | **Christian Plasa** | energetic, crisp, fast-paced, no pauses |

- **Pro Video genau EINE Stimme** – nie zwei Stimmen in einem Video
- Mischt ein Video zwei Stimmungen (lustig → rührend): Stimme nach dem **Ende** wählen (das Gefühl, mit dem man rausgeht)
- Nicht dieselbe Stimme 5× hintereinander, wenn die Kategorie es zulässt (Kanal klingt sonst monoton)

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
- **KEIN Like-Satz** („gab diesem Video ein Like“) – vom Nutzer abgelehnt
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

## Skript-Fakten = was man SIEHT
- Jede beschriebene Handlung vor dem Vertonen im Original Bild für Bild prüfen (0,2-s-Schritte)
  (Fehler bei Video 6: „drückt ihm in die Hand“ – sie stellt sie hin; „reißt die Tüte auf“ – er holt es raus)
- Bei schnellen Bewegungen in der Hand (Spielhülle, Handy …) Keyframes statt Tracker
- Korrekturen: `tools/splice.py` ersetzt einen einzelnen Satz in der Stimme und zieht alle Zeiten nach
- Das Wort, das etwas benennt („GTA!“), muss genau auf dem Bild liegen, wo man es sieht

## Stimme & Timing (neuer Standard ab Video 6)
- Stimme immer KOMPLETT neu erzeugen statt Sätze einzukleben (Kleben kann Wortreste hinterlassen)
- Wortzeiten: ElevenLabs-Transkription (0 Credits) auf den Sprach-Node → `words.json`
- `tools/tighten.py`: Pausen nur ZWISCHEN Wörtern kürzen (Wortenden per Pegel gekürzt), Tempo 1.15 → exakte Wortzeiten
- Untertitel mit exakten Wortzeiten (`words` in den Captions)
- `tools/retime.py`: bei neuer Stimme alle Shots/Overlays/Sounds auf die neuen Satzgrenzen umrechnen
- `cut.py` warnt, wenn ein Shot über einen Schnitt im Original oder dessen Ende läuft; `build.py` kürzt Overlays automatisch auf ihren Shot
