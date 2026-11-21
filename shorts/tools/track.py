#!/usr/bin/env python3
"""Automatische Platzierung von Kreisen/Pfeilen auf Gesichter oder Personen.

Overlay-Felder:
  target: "face" | "person"   -> wonach gesucht wird
  hint:   [x, y]              -> grobe Stelle im 1080x1920-Bild (nimmt die naechste Erkennung)
Ergebnis:
  Kreis  -> Mittelpunkt + Groesse so, dass der Kreis das Ziel UMSCHLIESST (nicht verdeckt)
  Pfeil  -> Spitze sitzt mit Abstand VOR dem Ziel und zeigt auf dessen Mitte
  Bewegt sich das Ziel, wandert das Overlay mit (x_end/y_end).
Benoetigt opencv-python-headless 4.x (mit Haar-Cascades).
"""
import math
import cv2

_face = None
_face2 = None
_profile = None
_hog = None

def _init():
    global _face, _face2, _profile, _hog
    if _face is None:
        d = cv2.data.haarcascades
        _face = cv2.CascadeClassifier(d + "haarcascade_frontalface_default.xml")
        _face2 = cv2.CascadeClassifier(d + "haarcascade_frontalface_alt2.xml")
        _profile = cv2.CascadeClassifier(d + "haarcascade_profileface.xml")
        _hog = cv2.HOGDescriptor()
        _hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def grab(video, t):
    cap = cv2.VideoCapture(video)
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, frame = cap.read()
    cap.release()
    return frame if ok else None

def faces(frame):
    _init()
    g = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    out = []
    for c in (_face, _face2):
        out += [tuple(b) for b in c.detectMultiScale(g, 1.08, 5, minSize=(60, 60))]
    for flip in (False, True):
        gg = cv2.flip(g, 1) if flip else g
        for (x, y, w, h) in _profile.detectMultiScale(gg, 1.08, 5, minSize=(60, 60)):
            out.append((g.shape[1] - x - w if flip else x, y, w, h))
    return out

def persons(frame):
    _init()
    small = cv2.resize(frame, (540, 960))
    rects, _ = _hog.detectMultiScale(small, winStride=(8, 8), padding=(16, 16), scale=1.05)
    return [(x * 2, y * 2, w * 2, h * 2) for (x, y, w, h) in rects]

def _nearest(boxes, hint):
    if not boxes:
        return None
    hx, hy = hint
    return min(boxes, key=lambda b: (b[0] + b[2] / 2 - hx) ** 2 + (b[1] + b[3] / 2 - hy) ** 2)

def locate(video, t, target, hint):
    """Gibt (cx, cy, radius) des Ziels zurueck oder None."""
    fr = grab(video, t)
    if fr is None:
        return None
    if target == "face":
        b = _nearest(faces(fr), hint)
        if b:
            x, y, w, h = b
            return (x + w / 2, y + h / 2, max(w, h) * 0.62)
        target = "person"          # Rueckfall: Kopf aus Personen-Box schaetzen
    b = _nearest(persons(fr), hint)
    if b:
        x, y, w, h = b
        if target == "person_body":
            return (x + w / 2, y + h / 2, max(w, h) * 0.55)
        head = h * 0.17
        return (x + w / 2, y + h * 0.16, head * 1.0)
    return None

def place(o, video):
    """Setzt x, y, x_end, y_end, size (und bei Pfeilen die Spitze) anhand der Erkennung."""
    hint = o.get("hint", [540, 900])
    t0 = o["start"] + 0.05
    t1 = max(o["end"] - 0.08, t0)
    a = locate(video, t0, o["target"], hint)
    b = locate(video, t1, o["target"], [a[0], a[1]] if a else hint)
    if a is None and b is None:
        print(f"  !! kein Ziel gefunden fuer {o['style']} @ {o['start']} -> Hinweis-Position bleibt")
        a = b = (hint[0], hint[1], o.get("size", 300) / 2)
    a = a or b
    b = b or a
    # Sprung zwischen Start und Ende zu gross -> falsche Erkennung, nicht mitwandern
    if math.hypot(a[0] - b[0], a[1] - b[1]) > 260:
        b = a
    r = max(a[2], b[2])
    # Regel: Gesicht fuellt fast das Bild -> kein Pfeil (wuerde das Gesicht verdecken)
    if o["style"].startswith("arrow") and r > 200:
        print(f"  -> {o['style']} @ {o['start']} entfernt: Ziel zu gross (r={int(r)}), Pfeil wuerde verdecken")
        o["_skip"] = True
        return o
    if o["style"].startswith("circle"):
        ring = r * 1.35 + 30                     # Ring liegt AUSSERHALB des Ziels
        o["size"] = int(ring * 2 / 1.08)
        o["x"], o["y"], o["x_end"], o["y_end"] = int(a[0]), int(a[1]), int(b[0]), int(b[1])
    else:
        ang = math.radians(o.get("angle", 45))
        dx, dy = math.cos(ang), math.sin(ang)
        L = o.get("size", 230)
        def inside(px, py, gap):
            tx, ty = px - dx * gap, py - dy * gap          # Spitze
            bx, by = tx - dx * L * 0.9, ty - dy * L * 0.9   # Pfeil-Ende
            return all(40 <= v <= 1040 for v in (tx, bx)) and all(80 <= v <= 1840 for v in (ty, by))
        gap = r * 1.35 + 40                      # Spitze endet VOR dem Ziel
        # Grosses Ziel (z.B. Gesicht fuellt das Bild): Abstand verkleinern, bis der Pfeil ins Bild passt
        while gap > r * 0.5 and not inside(a[0], a[1], gap):
            gap -= 15
        o["x"], o["y"] = int(a[0] - dx * gap), int(a[1] - dy * gap)
        o["x_end"], o["y_end"] = int(b[0] - dx * gap), int(b[1] - dy * gap)
    o["_target"] = [int(a[0]), int(a[1]), int(r)]
    return o


# ---------------------------------------------------------------------------
# Mitbewegen: Objekt Bild fuer Bild verfolgen (CSRT-Tracker)
# ---------------------------------------------------------------------------
def follow_path(video, t0, t1, cx, cy, box, fps=30):
    """Verfolgt das Objekt mit Mittelpunkt (cx,cy) und Kantenlaenge box ab t0 bis t1.
    Gibt pro Ausgabebild (cx, cy, scale) zurueck – geglaettet, Ausreisser verworfen."""
    import numpy as np
    cap = cv2.VideoCapture(video)
    cap.set(cv2.CAP_PROP_POS_MSEC, t0 * 1000)
    ok, frame = cap.read()
    n = max(1, round((t1 - t0) * fps))
    if not ok:
        return [(cx, cy, 1.0)] * n
    H, W = frame.shape[:2]
    b = int(box)
    x0, y0 = int(max(0, min(W - b, cx - b / 2))), int(max(0, min(H - b, cy - b / 2)))
    tr = cv2.TrackerCSRT_create()
    tr.init(frame, (x0, y0, b, b))
    pts = [(cx, cy, 1.0)]
    last = (cx, cy, 1.0)
    for _ in range(n - 1):
        ok, frame = cap.read()
        if not ok:
            pts.append(last); continue
        ok, r = tr.update(frame)
        if ok:
            nx, ny = r[0] + r[2] / 2, r[1] + r[3] / 2
            sc = max(0.7, min(1.4, r[2] / b))
            # Sprung > 15 % der Bildbreite pro Bild = Fehlgriff -> letzte Position halten
            if abs(nx - last[0]) + abs(ny - last[1]) < W * 0.15:
                last = (nx, ny, sc)
        pts.append(last)
    cap.release()
    a = np.array(pts, dtype=float)
    k = 5                                     # gleitender Mittelwert gegen Zittern
    if len(a) > k:
        pad = np.pad(a, ((k // 2, k // 2), (0, 0)), mode="edge")
        a = np.stack([np.convolve(pad[:, i], np.ones(k) / k, mode="valid") for i in range(3)], 1)
    return [tuple(p) for p in a]
