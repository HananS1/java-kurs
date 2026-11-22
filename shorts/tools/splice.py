#!/usr/bin/env python3
"""Einen Satz in der fertigen Stimme ersetzen und alle Zeiten (Shots, Untertitel, Overlays, Sounds) nachziehen.
Aufruf: python3 splice.py <ordner> <neuer_satz.mp3> "<alter Satzanfang>" "<neuer Satztext>" [highlight-wort ...]
Der alte Satz wird ueber den Untertitel in config.json gefunden (Start/Ende).
"""
import json, subprocess, sys, os

def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)

def main(folder, new_mp3, old_prefix, new_text, *hl):
    os.chdir(folder)
    c = json.load(open("config.json"))
    cap = next(x for x in c["captions"] if x["text"].startswith(old_prefix))
    A, B = cap["start"], cap["end"]
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", new_mp3, "-af",
                    "silenceremove=start_periods=1:start_threshold=-40dB:stop_periods=-1:stop_duration=0.05:"
                    "stop_threshold=-38dB,areverse,silenceremove=start_periods=1:start_threshold=-40dB,areverse,"
                    "atempo=1.12,aresample=44100", "-ac", "1", "_line.wav"], check=True)
    dn = dur("_line.wav")
    delta = dn - (B - A)
    os.replace("voice.wav", "voice_prev.wav")
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", "voice_prev.wav", "-i", "_line.wav",
                    "-filter_complex",
                    f"[0:a]aformat=sample_rates=44100:channel_layouts=mono,asplit[x][y];"
                    f"[x]atrim=0:{A},asetpts=PTS-STARTPTS[p1];[y]atrim={B},asetpts=PTS-STARTPTS[p3];"
                    f"[1:a]aformat=sample_rates=44100:channel_layouts=mono[p2];[p1][p2][p3]concat=n=3:v=0:a=1[o]",
                    "-map", "[o]", "voice.wav"], check=True)
    sh = lambda t: t if t <= A + 0.001 else (A + dn if abs(t - B) < 0.01 else t + delta)
    s = json.load(open("shots.json"))
    for x in s["shots"]:
        x["start"], x["end"] = round(sh(x["start"]), 3), round(sh(x["end"]), 3)
    json.dump(s, open("shots.json", "w"), indent=1)
    cap["text"], cap["highlight"] = new_text, list(hl)
    for x in c["captions"]:
        if x is not cap:
            x["start"], x["end"] = round(sh(x["start"]), 3), round(sh(x["end"]), 3)
    cap["end"] = round(A + dn, 3)
    for o in c["overlays"]:
        for k in ("start", "end"):
            o[k] = round(sh(o[k]), 3)
        if "keys" in o:
            o["keys"] = [[round(sh(k[0]), 3)] + k[1:] for k in o["keys"]]
    for x in c["sfx"]:
        x["time"] = round(sh(x["time"]), 3)
    json.dump(c, open("config.json", "w"), indent=1, ensure_ascii=False)
    print(f"Satz {A:.2f}-{B:.2f} ersetzt: neu {dn:.2f}s (Verschiebung {delta:+.2f}s), Stimme jetzt {dur('voice.wav'):.2f}s")

if __name__ == "__main__":
    main(*sys.argv[1:])
