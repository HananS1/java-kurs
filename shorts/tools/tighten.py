#!/usr/bin/env python3
"""Stimme ohne Pausen bauen – sauber ZWISCHEN den Woertern, nichts wird angeschnitten.
Wortzeiten kommen aus ElevenLabs; Wortanfang/-ende werden zusaetzlich per Pegel auf den echten Klang gekuerzt.
Aufruf: python3 tighten.py roh.mp3 words.json voice.wav sentences.json script.txt [tempo=1.12] [luecke=0.04]
script.txt: ein Satz pro Zeile (genau wie Untertitel-Saetze) -> bestimmt die Satzaufteilung
"""
import json, os, re, subprocess, sys
import numpy as np

def _norm(t): return re.sub(r"[^\wäöüß]", "", t.lower())

def load(raw, sr=16000):
    b = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", raw, "-ac", "1", "-ar", str(sr),
                        "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(b, np.float32), sr

def main(raw, words_json, out_wav, out_sent, script, tempo="1.12", gap="0.04"):
    tempo, gap = float(tempo), float(gap)
    d = json.load(open(words_json))
    d = d["words"] if isinstance(d, dict) else d
    ws, intag = [], False
    for w in d:                                   # Regie-Tags [ ... ] ueberspringen (auch mehrteilig)
        t = w["text"]
        if t.startswith("["): intag = True
        if not intag and w.get("type", "word") == "word" and _norm(t):
            ws.append(dict(w))
        if t.endswith("]"): intag = False
    x, sr = load(raw)
    hop = 160
    env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    db = 20 * np.log10(env + 1e-9)
    thr = np.percentile(db, 90) - 30
    for w in ws:                                  # auf echten Klang kuerzen
        i0, i1 = int(w["start"] * sr / hop), int(w["end"] * sr / hop)
        loud = np.where(db[i0:i1 + 1] > thr)[0]
        if len(loud):
            w["start"] = (i0 + loud[0]) * hop / sr
            w["end"] = min(w["end"], (i0 + loud[-1] + 1) * hop / sr + 0.03)
    # PAUSE_AFTER="wort:0.3" -> genau EINE bewusste Mini-Pause vor dem Twist (erstes Vorkommen)
    pause_i, pause_s = -1, 0.0
    if os.environ.get("PAUSE_AFTER"):
        pw, ps = os.environ["PAUSE_AFTER"].rsplit(":", 1)       # "wort:0.3" oder "wort#2:0.3" (2. Vorkommen)
        pw, nth = (pw.split("#") + ["1"])[:2]
        hits = [i for i, w in enumerate(ws) if _norm(w["text"]) == _norm(pw)]
        pause_i = hits[int(nth) - 1]; pause_s = float(ps) * tempo
    segs, t_out, timed = [], 0.0, []
    for i, w in enumerate(ws):
        a = max(0.0, w["start"] - 0.015)
        b = w["end"] + 0.015
        if i + 1 < len(ws):
            b = min(b, ws[i + 1]["start"] - 0.005)
        segs.append((a, b))
        st = t_out + (w["start"] - a)
        timed.append([w["text"], st, st + (w["end"] - w["start"])])
        g = gap + (pause_s if i == pause_i else 0.0)
        segs[-1] = (a, b, g)
        t_out += (b - a) + g
    parts = "".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,apad=pad_dur={g:.3f}[s{i}];"
                    for i, (a, b, g) in enumerate(segs))
    cat = "".join(f"[s{i}]" for i in range(len(segs)))
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", raw, "-filter_complex",
                    parts + f"{cat}concat=n={len(segs)}:v=0:a=1,atempo={tempo}[o]",
                    "-map", "[o]", "-ac", "1", "-ar", "44100", out_wav], check=True)
    timed = [[t, round(s / tempo, 3), round(e / tempo, 3)] for t, s, e in timed]
    lines = [l.strip() for l in open(script, encoding="utf-8") if l.strip()]
    out, k = [], 0
    for line in lines:                            # Saetze nach Wortanzahl der Skriptzeilen
        n = len(line.split())
        s = timed[k:k + n]; k += n
        out.append({"text": line, "start": s[0][1], "end": s[-1][2], "words": s})
    assert k == len(timed), f"Skript hat {k} Woerter, Stimme {len(timed)}"
    json.dump(out, open(out_sent, "w"), indent=1, ensure_ascii=False)
    print(f"{len(timed)} Woerter, {len(out)} Saetze, Laenge {timed[-1][2]:.2f}s")

if __name__ == "__main__":
    main(*sys.argv[1:])
