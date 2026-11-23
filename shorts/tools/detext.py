#!/usr/bin/env python3
"""Eingebrannte Untertitel (bunte/weisse Schrift mit dickem schwarzem Rand) erkennen und wegrechnen (Inpainting),
statt einen ganzen Streifen zu verwischen. Nur im Band y0..y1.
Aufruf: python3 detext.py src.mp4 out.mp4 y0 y1 [x0 x1]
"""
import subprocess, sys
import cv2, numpy as np


def mask_frame(fr, y0, y1, x0, x1):
    band = fr[y0:y1, x0:x1]
    hsv = cv2.cvtColor(band, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(band, cv2.COLOR_BGR2GRAY)
    dark = (gray < 40).astype(np.uint8)
    v, s = hsv[..., 2], hsv[..., 1]
    bright = ((v > 205) & ((s < 50) | (s > 140))).astype(np.uint8)
    near_dark = cv2.dilate(dark, np.ones((9, 9), np.uint8))
    cand = bright & near_dark
    # nur Schrift-artige Bloecke: Komponenten mit genug Pixeln, Hoehe < 140
    cand = cv2.morphologyEx(cand, cv2.MORPH_CLOSE, np.ones((5, 15), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(cand)
    m = np.zeros_like(cand)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a > 60 and h < 150 and w > 12:
            m[lab == i] = 1
    m = cv2.dilate(m, np.ones((15, 15), np.uint8))
    full = np.zeros(fr.shape[:2], np.uint8)
    full[y0:y1, x0:x1] = m * 255
    return full


def main(src, out, y0, y1, x0=0, x1=None):
    y0, y1, x0 = int(y0), int(y1), int(x0)
    cap = cv2.VideoCapture(src)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    x1 = int(x1) if x1 else W
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                          "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a?",
                          "-c:v", "libx264", "-crf", "8", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "copy", out],
                         stdin=subprocess.PIPE)
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        m = mask_frame(fr, y0, y1, x0, x1)
        if m.any():
            fr = cv2.inpaint(fr, m, 5, cv2.INPAINT_TELEA)
            soft = cv2.GaussianBlur(m, (31, 31), 0)[..., None] / 255.0     # Reste weich verwischen
            fr = (fr * (1 - soft) + cv2.GaussianBlur(fr, (41, 41), 0) * soft).astype(np.uint8)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    print("fertig:", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
