#!/usr/bin/env python3
"""Praezise Kopf-Ringe wie bei Top-Shorts: duenner Ring NUR um den Kopf, Bild fuer Bild mitgefuehrt (YOLO-Pose),
zwei Farben fuer zwei Personen, Namensschild mit Mini-Pfeil, Farbblitz + Wackeln an Schluesselstellen.
Wird direkt in das geschnittene Video (clip_edit.mp4) gezeichnet -> build.py braucht keine Kreis-Overlays mehr.

Aufruf: python3 rings.py clip_edit.mp4 rings.json clip_fx.mp4
rings.json:
{"model": ".../yolov8m-pose.pt",
 "rings":  [{"start":0.2,"end":2.1,"seed":[540,600],"color":"yellow","label":"OPA"}],   # seed = Kopf ungefaehr bei start
 "arrows": [{"start":3,"end":4,"seed":[300,900],"color":"red","from":"left"}],          # Pfeil auf Kopf (optional)
 "flash":  [{"time":8.2,"dur":0.45,"color":"red"}],                                     # Farbblitz
 "shake":  [{"time":8.2,"dur":0.35,"amp":14}]}
Ringe nie ueber einen Schnitt: start/end je Shot setzen.
"""
import json, math, subprocess, sys
import numpy as np
import cv2

COL = {"yellow": (40, 230, 255), "red": (40, 40, 245), "white": (255, 255, 255), "green": (80, 230, 80),
       "blue": (255, 160, 40)}
FONT = None


def head_from_pose(kp, cf, box):
    """kp: (17,2), cf: (17,) -> (cx, cy, r) oder None"""
    pts = [kp[i] for i in (0, 1, 2, 3, 4) if cf[i] > 0.35]
    x1, y1, x2, y2 = box
    bw, bh = x2 - x1, y2 - y1
    rs = []
    if cf[3] > 0.35 and cf[4] > 0.35:
        rs.append(0.62 * np.linalg.norm(kp[3] - kp[4]))
    if cf[1] > 0.35 and cf[2] > 0.35:
        rs.append(1.25 * np.linalg.norm(kp[1] - kp[2]))
    if cf[5] > 0.35 and cf[6] > 0.35:
        rs.append(0.30 * np.linalg.norm(kp[5] - kp[6]))
    rs.append(0.075 * bh)                      # Kopf ~ 1/7 der sichtbaren Koerperhoehe (grob, nur Untergrenze)
    r = float(max(rs))                          # max: Seitenansicht unterschaetzt Augen-/Ohrenabstand
    if pts:
        c = np.mean(pts, axis=0)
        # Mittelpunkt etwas Richtung Schaedel (Keypoints sitzen im Gesicht)
        cx, cy = float(c[0]), float(c[1] - 0.15 * r)
    else:
        cx, cy = (x1 + x2) / 2, y1 + r
    r = max(22.0, min(r, 0.5 * max(bw, 40)))
    return cx, cy, r


def detect_all(video, model_path, t0, t1, fps):
    from ultralytics import YOLO
    m = YOLO(model_path)
    cap = cv2.VideoCapture(video)
    cap.set(cv2.CAP_PROP_POS_MSEC, t0 * 1000)
    out = {}
    f0 = round(t0 * fps)
    for f in range(f0, round(t1 * fps) + 1):
        ok, fr = cap.read()
        if not ok:
            break
        # ByteTrack: jede Person behaelt ihre ID -> Ring springt nicht auf andere Personen
        r = m.track(fr, persist=True, verbose=False, imgsz=960, conf=0.15, tracker="bytetrack.yaml")[0]
        heads = []
        if r.keypoints is not None and len(r.boxes):
            kps = r.keypoints.xy.cpu().numpy(); cfs = r.keypoints.conf.cpu().numpy()
            bxs = r.boxes.xyxy.cpu().numpy()
            ids = r.boxes.id.cpu().numpy().astype(int) if r.boxes.id is not None else [-1] * len(bxs)
            for kp, cf, bx, tid in zip(kps, cfs, bxs, ids):
                heads.append({"kp": kp.round(1).tolist(), "cf": cf.round(3).tolist(), "box": bx.round(1).tolist(),
                              "id": int(tid)})
        out[f] = heads
    return out


def track(dets, f0, f1, seed, want_id=None):
    """Folgt dem Kopf, der am naechsten am Seed liegt; Luecken werden ueberbrueckt; danach geglaettet."""
    px, py = seed; pr = None; vx = vy = 0.0; tid = want_id
    raw = []
    for f in range(f0, f1 + 1):
        hs = dets.get(f, [])
        best = None; bd = 1e9
        if tid is not None:                       # zuerst: dieselbe Personen-ID
            same = [h for h in hs if int(h[3]) == tid and h[3] >= 0]
            if same:
                best = same[0]
        if best is None:
            for h in hs:
                d = math.hypot(h[0] - px, h[1] - py)
                lim = (2.0 * pr + 40) if pr else 250
                if d < bd and d < lim:
                    best, bd = h, d
            if best is not None and tid is None:
                tid = int(best[3]) if best[3] >= 0 else None
        if best:
            vx, vy = best[0] - px, best[1] - py
            px, py = best[0], best[1]; pr = best[2] if pr is None else 0.7 * pr + 0.3 * best[2]
            raw.append((px, py, pr, True))
        else:
            px, py = px + vx * 0.5, py + vy * 0.5; vx *= 0.5; vy *= 0.5
            raw.append((px, py, pr or 60.0, False))
    a = np.array([[x, y, r] for x, y, r, _ in raw], float)
    if len(a) >= 5:   # Glaetten: zentrierter gleitender Mittelwert (kein Nachhinken)
        k = 5
        pad = np.pad(a, ((k // 2, k // 2), (0, 0)), mode="edge")
        a = np.stack([np.convolve(pad[:, j], np.ones(k) / k, mode="valid") for j in range(3)], 1)
        rr = np.pad(a[:, 2], (7, 7), mode="edge")
        a[:, 2] = np.convolve(rr, np.ones(15) / 15, mode="valid")
    hits = sum(1 for *_, h in raw if h)
    return a, hits / max(1, len(raw))


def put_label(img, text, cx, top, color, scale):
    global FONT
    from PIL import Image, ImageDraw, ImageFont
    if FONT is None:
        import os
        FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts", "Bangers-Regular.ttf")
    size = int(70 * scale)
    font = ImageFont.truetype(FONT, size)
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil)
    tw = d.textlength(text, font=font)
    x = int(cx - tw / 2); y = int(top - size - 34 * scale)
    rgb = tuple(int(v) for v in color[::-1])
    d.text((x, y), text, font=font, fill=rgb, stroke_width=max(3, int(6 * scale)), stroke_fill=(0, 0, 0))
    # Mini-Pfeil (Dreieck) unter dem Namen
    ax, ay = cx, top - 14 * scale
    s = 16 * scale
    d.polygon([(ax - s, ay - s * 1.3), (ax + s, ay - s * 1.3), (ax, ay)], fill=rgb, outline=(0, 0, 0))
    img[:] = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def main(video, spec_path, out):
    spec = json.load(open(spec_path))
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    items = spec.get("rings", []) + [dict(a, _arrow=True) for a in spec.get("arrows", [])]
    paths = []
    if items:
        t0 = min(r["start"] for r in items); t1 = max(r["end"] for r in items)
        import os
        cache = video + ".dets.json"              # Erkennung zwischenspeichern (dauert lange)
        if os.path.exists(cache):
            raw = {int(k): v for k, v in json.load(open(cache)).items()}
        else:
            raw = detect_all(video, spec["model"], 0, N / fps, fps)
            json.dump(raw, open(cache, "w"))
        dets = {f: [head_from_pose(np.array(d["kp"]), np.array(d["cf"]), d["box"]) + (d["id"],) for d in v]
                for f, v in raw.items()}
        for r in items:
            f0, f1 = round(r["start"] * fps), round(r["end"] * fps)
            if "keys" in r:          # Fallback: von Hand gemessen [[t,x,y,r],...]
                ts = np.arange(f0, f1 + 1) / fps; k = np.array(r["keys"], float)
                a = np.stack([np.interp(ts, k[:, 0], k[:, j]) for j in (1, 2, 3)], 1); q = 1.0
            else:
                if "id" in r and "seed" not in r:   # Startpunkt aus der ID ableiten
                    for ff in range(f0, f1 + 1):
                        m_ = [h for h in dets.get(ff, []) if int(h[3]) == r["id"]]
                        if m_:
                            r["seed"] = [m_[0][0], m_[0][1]]; break
                a, q = track(dets, f0, f1, r.get("seed", [W / 2, H / 2]), r.get("id"))
            print(f"  {'Pfeil' if r.get('_arrow') else 'Ring '} {r.get('label', ''):8s} {r['start']:6.2f}-{r['end']:6.2f}"
                  f"  erkannt {q*100:3.0f}%  Kopf r~{np.median(a[:, 2]):.0f}px")
            if q < 0.6 and "keys" not in r:
                print("   !! WARNUNG: Kopf oft nicht erkannt -> Ergebnis pruefen oder keys setzen")
            paths.append((r, f0, a))
    flashes = spec.get("flash", []); shakes = spec.get("shake", [])
    cap.release(); cap = cv2.VideoCapture(video)
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                          "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "6", "-preset", "fast",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    sc = W / 1080
    for f in range(N):
        ok, fr = cap.read()
        if not ok:
            break
        t = f / fps
        for fl in flashes:   # Farbblitz: kraeftige Toenung, klingt aus
            dt = t - fl["time"]
            if 0 <= dt < fl.get("dur", 0.45):
                k = 0.55 * (1 - dt / fl.get("dur", 0.45))
                tint = np.zeros_like(fr); tint[:] = COL[fl.get("color", "red")]
                fr = cv2.addWeighted(fr, 1 - k, tint, k, 0)
        for r, f0, a in paths:
            i = f - f0
            if not (0 <= i < len(a)):
                continue
            cx, cy, hr = a[i]
            col = COL[r.get("color", "yellow")]
            prog = min(1.0, i / (0.18 * fps))           # Ring wird in 0,18 s gezeichnet
            if r.get("_arrow"):
                # gerader Pfeil, Spitze kurz vor dem Kopf
                side = r.get("from", "left"); L = 170 * sc * (0.4 + 0.6 * prog)
                ang = {"left": 180, "right": 0, "top": 270, "bottom": 90}[side]
                ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
                tip = (cx + ux * (hr * 1.35 + 10), cy + uy * (hr * 1.35 + 10))
                tail = (tip[0] + ux * L, tip[1] + uy * L)
                cv2.arrowedLine(fr, (int(tail[0]), int(tail[1])), (int(tip[0]), int(tip[1])), (0, 0, 0),
                                int(16 * sc), cv2.LINE_AA, tipLength=0.32)
                cv2.arrowedLine(fr, (int(tail[0]), int(tail[1])), (int(tip[0]), int(tip[1])), col,
                                int(9 * sc), cv2.LINE_AA, tipLength=0.32)
                continue
            R = int(hr * r.get("scale", 1.45))
            th = max(4, int(r.get("thick", 7) * sc))
            pop = 1.0 + 0.12 * max(0.0, 1 - i / (0.25 * fps))
            R2 = int(R * pop)
            end = int(-90 + 360 * prog)
            cv2.ellipse(fr, (int(cx), int(cy)), (R2, R2), 0, -90, end, (0, 0, 0), th + 4, cv2.LINE_AA)
            cv2.ellipse(fr, (int(cx), int(cy)), (R2, R2), 0, -90, end, col, th, cv2.LINE_AA)
            if r.get("label") and prog >= 1.0:
                put_label(fr, r["label"], cx, cy - R2, col, sc)
        for s in shakes:
            dt = t - s["time"]
            if 0 <= dt < s.get("dur", 0.35):
                amp = s.get("amp", 14) * sc * (1 - dt / s.get("dur", 0.35))
                dx, dy = amp * math.sin(dt * 90), amp * math.cos(dt * 70)
                M = np.float32([[1.04, 0, -W * 0.02 + dx], [0, 1.04, -H * 0.02 + dy]])
                fr = cv2.warpAffine(fr, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    print("fertig:", out)


if __name__ == "__main__":
    main(*sys.argv[1:4])
