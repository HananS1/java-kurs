# Regeln für den TikTok-Kanal (@unglaublichwahr, Platzhalter)

## Feste Regel: Mit jedem neuen Video wird die Optik besser
Bei JEDEM neuen Video mindestens 2–3 neue visuelle Dynamik-Upgrades in die Engine
einbauen (z. B. neue Bewegungen, Übergänge, Partikel, Kamera, Text-Animation) und
im Changelog unten festhalten. Nie ein Video mit exakt dem Stand des vorherigen machen.
Effekte dürfen nicht überladen wirken: lieber Bewegung in Figuren und Szenen als
noch mehr Blitze.

## Feste Regel: JEDER Schlag ist im Bild sichtbar (immer, bei jedem Video)
`"beatFx": true` + `"barPhase"` (Taktanfang) im Story-JSON. Auf jedem Beat: Zoom-Punch,
Licht-Puls mit rotem Rand-Glühen, Bewegungsschub (Animationszeit läuft nach dem
Schlag schnell, dann langsam), Text pumpt leicht; Taktanfänge zusätzlich RGB-Split +
Ruckeln. Stärke folgt der Lautstärke des Schlags (`"react"`). Nach dem Rendern mit
`beatcheck` prüfen: Ziel 100 % der Schläge mit sichtbarem Impuls. Max. 3 Lichtpulse/s.

## Format
- Silhouetten-Stil, kein Voiceover, Text auf dem Beat, versteckte Biene (nicht bei
  ernsten Themen wie NS/Holocaust).
- Länge aktuell 61 s (Creator Rewards brauchen > 1 min).
- Hook (2 Zeilen) → Titelkarte → Story → Enthüllung → Zusammenfassung → Endkarte.
- Jede Zahl/Fakt mit 2 Quellen prüfen, Quellen ins Story-JSON.
- Ton: −14 LUFS, keine Peaks über −1 dB (nach dem Rendern messen).

## Changelog Optik
- v1 Ballonflucht: Grundstil, Silhouetten, Labels, Zähler, Dokumente, Stempel, Endkarte.
- v2 Ballonflucht: Wort-für-Wort-Text, Slam-Zeile, Kamera-Shake, Blitze, Schockwellen,
  Pop-up-Tags, Titelkarte, Enthüllungs-Szene, 140-BPM-Musik.
- v3 Ballonflucht: Whip-Übergänge mit Blur, Beat-Puls, Kamerafahrt, Glitch auf Slam,
  Partikel, Open-Loop-Tag, Swell vor Slam.
- v4 Tuffi: animierte Hauptfigur (Elefant läuft, Rüssel/Ohren bewegen sich),
  Physik-Partikel (Wasser, Trümmer, Fontäne), Speed-Lines beim Fall, Parallax bei
  Fahrt, Kamerablitze, Marker-Effekt für *Schlüsselwörter* in Zeile 1,
  austauschbares Endkarten-Emblem. Neue Sounds: Platschen, Splittern, Blitz, Trompeten.

- v5 Juliane: menschliche Hauptfigur (geht/watet, Haare/Arme schwingen), Blitzlicht +
  Regen, Tiefenunschärfe (gecachte Dschungel-Ebenen), Text fliegt am Szenenende raus,
  92-Figuren-Infografik, Körper-Hotspots, Zähler mit Tausenderpunkt.
- v6 Juliane (Kino-Stil wie Referenz @plmadafaka): `"textStyle": "cinematic"` –
  Serifenschrift Cinzel, weiß + karminrot, Text mittig mit Label darüber, Blur-In /
  Blur-Out statt Pop, Unschärfe-Überblendungen mit Abdunklung, ruhigere Kamera,
  entsättigtes Grading, Explosionen aus Kreisen + Rauch + rotem Ring. Schnitte exakt
  auf den Schnittpunkten des Referenzvideos (Taktanfänge, 4/8 Beats).
- v7 Juliane (Beat-Choreografie): jede Textzeile hat eine absolute Zeit auf einem
  Schlag (`"lines"`), Hits/Blitze aus der Referenz (`"hits"`), Explosionen pro Szene
  (`"blastAt"`), Verletzungs-Hotspots auf Hits (`"spots"`), Kamera reagiert auf den
  Musik-Onset (`"react"`). Szenen nach Musik-Intensität verteilt (ruhig ↔ Höhepunkt).
  Prüfung: Ereignisse im fertigen Video messen und mit Referenz vergleichen.
- v8 (Standard ab jetzt, `"v8": true`): Snap-Zoom-Treppe auf jedem Taktanfang,
  Dutch-Tilt im Takt, kinetische Typo (Zeilen fliegen abwechselnd rein, große Wörter
  ziehen Buchstaben zusammen), Speed-Ramp (Zeitlupe vor jedem großen Treffer),
  Impact-Frames (2 invertierte Bilder bei Explosionen), Cinema-Balken bei Treffern,
  Zoom-Through-Übergänge, wandernde Lichtreflexe, Filmkorn im Beat. Explosionen als
  Feuerbälle mit Verlauf + Funken. Grenze: max. 3 Lichtpulse/s, keine Dauerblitze.

## Musik
- Standard für neue Videos: `"musicStyle": "darkEpic"` (eigene Musik im Stil des
  Referenz-Tracks von @plmadafaka): 115,75 BPM, Fis-Moll mit phrygischem G,
  Sub-Bass-Drohne, Staccato-Streicher in Achteln, Schlag auf jedem Beat.
  Basslauf über `"roots"` (Zeit in s → Grundton). Kein fremder Track im Video.
- Nach dem Rendern Klangbalance gegen die Referenz messen (Bänder 20–80, 80–250,
  250–1k, 1–4k, 4–11k Hz), Ziel: ±2 dB.

- Alternative: eigener Track per `"musicFile"` + `"musicStart"` (Datei liegt in
  `music/`, nicht im Repo). BPM per Kick-Band messen, Start so legen, dass der Drop
  auf der Titelkarte landet. Vorher klären, ob der Track lizenzfrei ist.

## Nächste Upgrade-Ideen (für v9+)
- Karten-Szenen mit Punkten, die auf Schlägen aufploppen (wie Referenz)
- Detailliertere Figuren (Kleidung, Gesichtsprofil), mehr Posen
- Figuren mit mehr Posen (Menschen gehen/rennen statt nur stehen)
- Tiefenunschärfe für Hintergrund-Ebenen
- Licht, das auf Figuren reagiert (Rim-Light vom Feuer, Blaulicht)
- Text-Übergänge, bei denen alte Zeilen rausfliegen statt hart zu wechseln
