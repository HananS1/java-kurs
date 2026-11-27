#!/usr/bin/env python3
"""Wort-Zeiten OHNE Transkription (spart Credits): Saetze ueber Sprechpausen finden, Woerter darin nach
Silben/Laenge verteilen. Ausgabe im words.json-Format fuer place_voice.py.
Aufruf: python3 align.py raw.mp3 "Satz 1|Satz 2|..." words.json
Die Saetze muessen in Reihenfolge den hoerbaren Abschnitten entsprechen (Pause >= gap s zwischen Saetzen).
"""
import json, re, subprocess, sys
import numpy as np


def segments(path, sr=16000, hop=0.02, thr=-42, gap=0.22):
    b = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                       capture_output=True).stdout
    a = np.frombuffer(b, np.int16) / 32768.0
    n = int(hop * sr)
    e = np.array([20 * np.log10(np.sqrt(np.mean(a[i:i + n] ** 2)) + 1e-9) for i in range(0, len(a) - n, n)])
    on = e > thr
    segs, s = [], None
    for i, v in enumerate(on):
        if v and s is None: s = i
        if not v and s is not None:
            segs.append([s * hop, i * hop]); s = None
    if s is not None: segs.append([s * hop, len(on) * hop])
    out = []
    for x in segs:
        if out and x[0] - out[-1][1] < gap: out[-1][1] = x[1]
        else: out.append(x)
    return [x for x in out if x[1] - x[0] > 0.08]


def syl(w):
    return max(1, len(re.findall(r"[aeiouäöüy]+", w.lower())))


def main(raw, sents, out, gap="0.22"):
    sents = [s.strip() for s in sents.split("|") if s.strip()]
    segs = segments(raw, gap=float(gap))
    # Abschnitte den Saetzen zuordnen: zu viele Abschnitte -> die kleinsten Pausen zusammenlegen
    while len(segs) > len(sents):
        gaps = [segs[i + 1][0] - segs[i][1] for i in range(len(segs) - 1)]
        i = int(np.argmin(gaps)); segs[i] = [segs[i][0], segs[i + 1][1]]; del segs[i + 1]
    if len(segs) < len(sents):   # tipp: kleineres gap (4. Argument) versuchen
        sys.exit(f"Nur {len(segs)} Abschnitte fuer {len(sents)} Saetze gefunden: {segs}")
    words = []
    for (t0, t1), s in zip(segs, sents):
        ws = s.split(); wt = [syl(w) + 0.15 * len(w) for w in ws]; tot = sum(wt); t = t0
        for w, x in zip(ws, wt):
            d = (t1 - t0) * x / tot
            words.append({"text": w, "type": "word", "start": round(t, 3), "end": round(t + d * 0.9, 3)}); t += d
        print(f"{t0:6.2f}-{t1:6.2f}  {s}")
    json.dump({"words": words}, open(out, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:5])
