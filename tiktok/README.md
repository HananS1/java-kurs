# TikTok-Pipeline: Unglaubliche wahre Geschichten

Rendert Silhouetten-Storyvideos (1080×1920, 30 fps) mit synthetisch erzeugter Musik
und Soundeffekten, die exakt auf den Beats liegen.

```
node render.js stories/ballonflucht.json            # fertiges MP4 -> out/ballonflucht.mp4
node render.js stories/ballonflucht.json --preview  # Kontaktabzug aller Szenen
```

- `stories/*.json` – Skript: Szenen, Texte, Timing in Beats, Soundeffekte, Quellen
- `engine.js` – zeichnet die Szenen (Canvas)
- `audio.py` – Musik + SFX aus der Timeline
- `render.js` – Playwright rendert Frames, ffmpeg baut das MP4

Schriften: Anton, Oswald, Special Elite, Black Ops One (SIL Open Font License).
