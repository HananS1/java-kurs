# Video-Engine „Weg der Dinge“

Programm für die TikTok-Karten-Videos (3D-Globus, Satellitenkarte, Route, Infoleiste, Foto-Blasen, Wort-Untertitel). Gebaut mit three.js, gerendert Bild für Bild mit Playwright/Chromium, geschnitten mit ffmpeg. Alles kostenlos, nur die Stimme kommt von ElevenLabs.

## Inhalt

| Ordner | Was |
|---|---|
| `prompt/` | Master-Prompt V6 (PDF + HTML-Quelle), Quellen-Texte der fertigen Videos |
| `scenes/` | Fertige Szenen: `banane.html`, `redbull.html` mit Untertitel-Timings. Vorlage für neue Videos |
| `tools/` | Rendern, Testbilder, Ton-Mix, Satellitenbilder, Wikimedia-Fotos, Erd-Textur |
| `setup.sh` | Baut die Arbeitsumgebung auf |

## Neues Video in einer neuen Sitzung

1. `bash video-engine/setup.sh <arbeitsordner>` (braucht node, python3 mit Pillow/numpy, ffmpeg).
2. Netzfreigaben: `tiles.maps.eox.at`, `commons.wikimedia.org`, `upload.wikimedia.org`, `elevenlabsusercontent.com`.
3. Eine Szene aus `scenes/` kopieren und anpassen: Stationen, Route, Kamera-Keyframes (`CK`), Infoleiste, Chips, Foto-Blasen (`CARDS`), Ortsnamen (`GEO`).
4. Satellitenbilder: `tools/patches_*.py` als Vorlage (Stationen in `P` eintragen), Ergebnis nach `build/patches/` bzw. den Ordner, den die Szene lädt. Dunkle Löcher danach mit `tools/fill_holes.py <ordner>` füllen.
5. Stimme mit ElevenLabs erzeugen (1 Aufnahme), Wort-Timings über die kostenlose Transkription holen, als `*_words.json` speichern (`w`, `s`, `e`, `g` = Untertitel-Gruppe, `hot`).
6. In `build/` einen Webserver starten: `python3 -m http.server 8765`.
7. Testbilder: `S=<arbeitsordner> node tools/snap.js <ausgabe> <sekunden…>` (Dateinamen der Szene im Skript anpassen).
8. Rendern in 3 parallelen Prozessen: `node tools/render.js <frames> <dauer> 30 <words.json> <von> <bis>`.
9. Ton und Video: `tools/mix_*.py` als Vorlage (Zeitpunkte der Soundeffekte anpassen).
10. Vor dem Versand: Kontaktbogen alle 0,5 s prüfen, Stimme auf Lücken über 0,35 s prüfen.

## Feste Regeln (Kurzfassung, vollständig im Master-Prompt)

- Kein Spoiler im Hook, keine vorgezeichnete Route.
- Nur belegte Zahlen, Normalpreise statt Aktionspreise.
- Echte Fotos mit freier Lizenz, keine KI-Bilder. Bevorzugt gemeinfrei oder CC0, kein Quellen-Text.
- Schluss: Zusammenfassung mindestens 3 s, dann komplette Route mit START und ZIEL (`overview()` in `redbull.html`).
- Keine fremde Musik ins Repository legen.

## Bekannte Stolpersteine

- Der lokale Webserver stirbt gelegentlich: vor jedem Rendern prüfen.
- Wikimedia bremst stark: höchstens eine Anfrage alle 30–60 s, eigene User-Agent-Kennung.
- Kamera senkrecht nach unten: Der Up-Vektor muss wie in `camAt()` berechnet werden, sonst dreht sich das Bild.
- Schwarze Rauten in der Karte entstehen bei zu grobem Patch-Gitter: `seg=160` beibehalten.
