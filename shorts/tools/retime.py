#!/usr/bin/env python3
"""Neue Stimme einsetzen: alle Zeiten (Shots, Untertitel, Overlays, Sounds) von den alten auf die neuen
Satzgrenzen umrechnen (stueckweise linear). Gleiche Satzanzahl vorausgesetzt.
Aufruf: python3 retime.py <ordner> <neue_align.json>   (config.json/shots.json werden angepasst)
"""
import json, sys, os
import numpy as np

def main(folder, new_align):
    os.chdir(folder)
    c = json.load(open("config.json"))
    new = json.load(open(new_align))
    old = c["captions"]
    assert len(old) == len(new), f"Satzanzahl alt {len(old)} != neu {len(new)}"
    ox = [0.0] + [x["end"] for x in old]
    nx = [0.0] + [x["end"] for x in new]
    tail_o, tail_n = ox[-1] + 5, nx[-1] + 5
    ox.append(tail_o); nx.append(tail_n)
    f = lambda t: round(float(np.interp(t, ox, nx)), 3)
    for o_cap, n_cap in zip(old, new):
        o_cap["start"], o_cap["end"], o_cap["text"] = n_cap["start"], n_cap["end"], n_cap["text"]
    for o in c["overlays"]:
        o["start"], o["end"] = f(o["start"]), f(o["end"])
        if "keys" in o:
            o["keys"] = [[f(k[0])] + k[1:] for k in o["keys"]]
    for x in c["sfx"]:
        x["time"] = f(x["time"])
    s = json.load(open("shots.json"))
    for x in s["shots"]:
        x["start"], x["end"] = f(x["start"]), f(x["end"])
    json.dump(s, open("shots.json", "w"), indent=1)
    json.dump(c, open("config.json", "w"), indent=1, ensure_ascii=False)
    print("umgerechnet; neue Laenge", nx[-2])

if __name__ == "__main__":
    main(*sys.argv[1:])
