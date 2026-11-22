#!/usr/bin/env python3
"""Zeigt alle erkannten Koepfe (aus rings.py-Cache) mit Personen-ID auf Standbildern -> Seeds sicher waehlen.
Aufruf: python3 heads_view.py clip_edit.mp4 0.5,3.2,8.0 out.jpg
Ausgabe pro Zeit: id -> (x, y, r)
"""
import json, sys
import cv2, numpy as np
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from rings import head_from_pose


def main(video, times, out):
    raw = {int(k): v for k, v in json.load(open(video + ".dets.json")).items()}
    cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS) or 30
    tiles = []
    for t in [float(x) for x in times.split(",")]:
        f = round(t * fps); cap.set(cv2.CAP_PROP_POS_FRAMES, f); ok, fr = cap.read()
        hs = []
        for d in raw.get(f, []):
            cx, cy, r = head_from_pose(np.array(d["kp"]), np.array(d["cf"]), d["box"])
            hs.append((d["id"], int(cx), int(cy), int(r)))
            cv2.circle(fr, (int(cx), int(cy)), int(r * 1.45), (0, 255, 255), 4)
            cv2.putText(fr, str(d["id"]), (int(cx) - 20, int(cy - r * 1.6)), 0, 2.2, (0, 0, 255), 6)
        cv2.putText(fr, f"t{t}", (20, 1880), 0, 3, (0, 255, 0), 8)
        print(t, hs)
        tiles.append(cv2.resize(fr, (270, 480)))
    while len(tiles) % 6: tiles.append(np.zeros_like(tiles[0]))
    cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i + 6]) for i in range(0, len(tiles), 6)]))


if __name__ == "__main__":
    main(*sys.argv[1:4])
