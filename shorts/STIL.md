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
- Nach jedem Render: Standbild aus der Mitte **jedes** Overlays prüfen
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
- Durchgehend Musik darunter (Referenz hat keine einzige Stille) → in der YouTube-App hinzufügen

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
