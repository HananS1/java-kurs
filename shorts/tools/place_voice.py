#!/usr/bin/env python3
"""Stimme in BLOECKEN an feste Videozeiten legen (Hybrid-Stil: Pausen fuer Originalton/Action).
Schneidet nur an Satzgrenzen (zwischen Saetzen), nie mitten in Woertern.
Aufruf: python3 place_voice.py roh.mp3 words.json voice.wav sentences.json blocks.json laenge [tempo=1.1]
blocks.json: [{"first":"Santiago","at":0.0,"lines":["Santiago pennt mitten im Unterricht."]}, ...]
"""
import json, subprocess, sys

def main(raw, words_json, out_wav, out_sent, blocks_json, total, tempo="1.1"):
    tempo, total = float(tempo), float(total)
    d = json.load(open(words_json)); d = d["words"] if isinstance(d, dict) else d
    ws, intag = [], False
    for w in d:
        t = w["text"]
        if t.startswith("["): intag = True
        if not intag and w.get("type", "word") == "word" and any(c.isalnum() for c in t): ws.append(w)
        if t.endswith("]"): intag = False
    blocks = json.load(open(blocks_json))
    pos = 0; filt = []; out = []
    for k, b in enumerate(blocks):
        n = sum(len([x for x in l.split() if any(c.isalnum() for c in x)]) for l in b["lines"])
        seg = ws[pos:pos + n]; assert seg[0]["text"].strip(".,?!…") .startswith(b["first"]), (seg[0]["text"], b["first"])
        s0 = max(0, seg[0]["start"] - 0.04); s1 = seg[-1]["end"] + 0.12
        if pos + n < len(ws): s1 = min(s1, (seg[-1]["end"] + ws[pos + n]["start"]) / 2)
        ms = int(b["at"] * 1000)
        filt.append(f"[0:a]atrim={s0:.3f}:{s1:.3f},asetpts=PTS-STARTPTS,atempo={tempo},adelay={ms}|{ms}[s{k}]")
        j = 0
        for l in b["lines"]:
            m = len([x for x in l.split() if any(c.isalnum() for c in x)])
            tw = [[w["text"], round((w["start"] - s0) / tempo + b["at"], 3), round((w["end"] - s0) / tempo + b["at"], 3)] for w in seg[j:j + m]]
            j += m
            out.append({"text": l, "start": tw[0][1], "end": tw[-1][2], "words": tw})
        pos += n
        print(f"Block {k}: {b['at']:.2f} - {out[-1]['end']:.2f}")
    fc = ";".join(filt) + ";" + "".join(f"[s{k}]" for k in range(len(blocks))) + f"amix=inputs={len(blocks)}:normalize=0[o]"
    subprocess.run(["ffmpeg", "-nostdin", "-y", "-loglevel", "error", "-i", raw, "-filter_complex", fc, "-map", "[o]",
                    "-ac", "1", "-ar", "44100", "-t", str(total), out_wav], check=True)
    json.dump(out, open(out_sent, "w"), indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main(*sys.argv[1:])
