#!/usr/bin/env python3
"""Weisse Untertitel-Boxen (TikTok-Stil) aus dem Original wegrechnen: Box per Helligkeit finden, Inpainting + weicher Rand.
Aufruf: python3 debox.py src.mp4 out.mp4 boxes.json    boxes.json: [[t0,t1,x,y,w,h], ...] (Suchbereich)"""
import json, subprocess, sys
import cv2, numpy as np

def main(src, out, bj):
    boxes = json.load(open(bj))
    cap = cv2.VideoCapture(src); fps = cap.get(5)
    W = int(cap.get(3)); H = int(cap.get(4))
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                          "-r", str(fps), "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "8",
                          "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "copy", out], stdin=subprocess.PIPE)
    f = 0
    while True:
        ok, fr = cap.read()
        if not ok: break
        t = f / fps; f += 1
        for t0, t1, x, y, w, h in boxes:
            if t0 <= t <= t1:
                roi = fr[y:y + h, x:x + w]
                m = ((roi.min(axis=2) > 200) & (roi.max(axis=2) - roi.min(axis=2) < 40)).astype(np.uint8)
                m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
                n, l, st, _ = cv2.connectedComponentsWithStats(m)
                mm = np.zeros_like(m)
                for i in range(1, n):
                    if st[i][4] > 800: mm[l == i] = 1
                mm = cv2.dilate(mm, np.ones((11, 11), np.uint8))
                # Text in der Box (schwarz) gehoert dazu: Huelle fuellen
                cnts, _ = cv2.findContours(mm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(mm, cnts, -1, 1, -1)
                full = np.zeros(fr.shape[:2], np.uint8); full[y:y + h, x:x + w] = mm * 255
                if full.any():
                    fr = cv2.inpaint(fr, full, 9, cv2.INPAINT_TELEA)
                    soft = cv2.GaussianBlur(full, (41, 41), 0)[..., None] / 255.0
                    fr = (fr * (1 - soft) + cv2.GaussianBlur(fr, (51, 51), 0) * soft).astype(np.uint8)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait(); print("fertig:", out)

if __name__ == "__main__":
    main(*sys.argv[1:4])
