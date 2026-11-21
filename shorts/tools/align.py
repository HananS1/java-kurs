#!/usr/bin/env python3
"""Satzgrenzen einer Stimme ohne Pausen finden: Schaetzung nach Textlaenge,
dann auf die naechste Lautstaerke-Senke (Wortgrenze) einrasten.
Aufruf: python3 align.py voice.wav "Satz 1." "Satz 2." ...  -> gibt start/end je Satz aus (JSON)"""
import sys, json, subprocess
import numpy as np

def dips(path, sr=16000, hop=80):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    e = np.array([np.sqrt(np.mean(x[i:i + 2 * hop] ** 2)) for i in range(0, len(x) - 2 * hop, hop)])
    db = 20 * np.log10(e + 1e-9)
    db = np.convolve(db, np.ones(3) / 3, mode="same")
    pk = np.percentile(db, 90)
    t = np.arange(len(db)) * hop / sr
    # lokale Minima, die deutlich unter dem Sprachpegel liegen
    mins = [(t[i], db[i]) for i in range(2, len(db) - 2)
            if db[i] < db[i - 1] and db[i] <= db[i + 1] and db[i] < pk - 14]
    return len(x) / sr, mins, pk

def align(path, sents):
    T, mins, pk = dips(path)
    L = np.array([len(s) + 3 for s in sents], float)
    est = np.concatenate([[0], np.cumsum(L) / L.sum() * T])
    bounds = [0.0]
    for b in est[1:-1]:
        cand = [(abs(t - b) + (d - (pk - 40)) * 0.004, t) for t, d in mins if abs(t - b) < 0.6 and t > bounds[-1] + 0.25]
        bounds.append(min(cand)[1] if cand else b)
    bounds.append(T)
    return [{"start": round(bounds[i], 2), "end": round(bounds[i + 1], 2), "text": s} for i, s in enumerate(sents)]

if __name__ == "__main__":
    print(json.dumps(align(sys.argv[1], sys.argv[2:]), ensure_ascii=False, indent=1))
