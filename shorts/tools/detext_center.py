#!/usr/bin/env python3
"""Eingebrannte, MITTIG zentrierte Wort-Untertitel (weiss mit schwarzem Rand, 1 Wort) entfernen.
Anders als detext.py: sucht pro Bild nur den zusammenhaengenden Textblock um die Bildmitte (cx) in der Zeile y0..y1
-> weisse Hemden/Schilder daneben werden NICHT angefasst.
Aufruf: python3 detext_center.py src.mp4 out.mp4 y0 y1 [cx=W/2]
"""
import subprocess, sys
import cv2, numpy as np


def text_rect(g, cx, gap=28):
    w = g > 200; d = g < 45
    near = cv2.dilate(d.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    cols = (w & near).sum(0)
    on = cols > 3
    if not on[max(0, cx - 120):cx + 120].any():
        return None
    # von der Mitte nach aussen laufen, Luecken bis gap Pixel erlauben
    def edge(step):
        x = cx; last = cx; miss = 0
        while 0 <= x < len(on):
            if on[x]: last = x; miss = 0
            else:
                miss += 1
                if miss > gap: break
            x += step
        return last
    l, r = edge(-1), edge(1)
    # Untertitel sind symmetrisch: Ausreisser auf einer Seite kappen
    half = min(cx - l, r - cx) + 25
    return max(0, cx - half), min(len(on) - 1, cx + half)


def main(src, out, y0, y1, cx=None):
    y0, y1 = int(y0), int(y1)
    cap = cv2.VideoCapture(src)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)); fps = cap.get(cv2.CAP_PROP_FPS)
    cx = int(cx) if cx else W // 2
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                          "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a?",
                          "-c:v", "libx264", "-crf", "10", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "copy", out],
                         stdin=subprocess.PIPE)
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        band = fr[y0:y1]; g = cv2.cvtColor(band, cv2.COLOR_BGR2GRAY)
        rr = text_rect(g, cx)
        if rr:
            l, r = rr
            m = np.zeros(fr.shape[:2], np.uint8)
            sub = ((g > 185) | (g < 55)).astype(np.uint8)
            sub[:, :l] = 0; sub[:, r + 1:] = 0
            m[y0:y1] = cv2.dilate(sub, np.ones((7, 7), np.uint8)) * 255
            fr = cv2.inpaint(fr, m, 6, cv2.INPAINT_TELEA)
            soft = cv2.GaussianBlur(m, (21, 21), 0)[..., None] / 255.0
            fr = (fr * (1 - soft) + cv2.GaussianBlur(fr, (31, 31), 0) * soft).astype(np.uint8)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    print("fertig:", out)


if __name__ == "__main__":
    main(*sys.argv[1:])
