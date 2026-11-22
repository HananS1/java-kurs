#!/usr/bin/env python3
"""Stimme FLUESSIG: ElevenLabs-Aufnahme am Stueck, nur schneller (atempo) - KEIN Schneiden zwischen Woertern
(tighten.py hat Wortenden abgehackt). Nur sehr lange Pausen (>0.35 s) werden per silenceremove gekuerzt? Nein: gar nichts.
Aufruf: python3 smooth.py roh.mp3 words.json voice.wav sentences.json script.txt [tempo=1.1]
"""
import json, subprocess, sys

def main(raw, words_json, out_wav, out_sent, script, tempo="1.1"):
    tempo = float(tempo)
    d = json.load(open(words_json)); d = d["words"] if isinstance(d, dict) else d
    ws, intag = [], False
    for w in d:
        t = w["text"]
        if t.startswith("["): intag = True
        if not intag and w.get("type", "word") == "word" and any(c.isalnum() for c in t):
            ws.append(w)
        if t.endswith("]"): intag = False
    t0 = max(0.0, ws[0]["start"] - 0.03)
    t1 = ws[-1]["end"] + 0.15
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", raw, "-af",
                    f"atrim={t0:.3f}:{t1:.3f},asetpts=PTS-STARTPTS,atempo={tempo}", "-ac", "1", "-ar", "44100", out_wav], check=True)
    timed = [[w["text"], round((w["start"] - t0) / tempo, 3), round((w["end"] - t0) / tempo, 3)] for w in ws]
    lines = [l.strip() for l in open(script, encoding="utf-8") if l.strip()]
    out, k = [], 0
    for line in lines:
        n = len(line.split()); s = timed[k:k + n]; k += n
        out.append({"text": line, "start": s[0][1], "end": s[-1][2], "words": s})
    assert k == len(timed), f"Skript {k} Woerter, Stimme {len(timed)}"
    json.dump(out, open(out_sent, "w"), indent=1, ensure_ascii=False)
    print(f"{len(timed)} Woerter, Laenge {timed[-1][2]:.2f}s")

if __name__ == "__main__":
    main(*sys.argv[1:])
