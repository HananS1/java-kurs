#!/usr/bin/env python3
"""Animierte Kreise und Pfeile als PNG-Sequenz (mit Transparenz) fuer ffmpeg-Overlays.

Stile:
  Kreise: circle_red (wird gezeichnet + pulsiert), circle_yellow (handgemalt, wackelt),
          circle_glow (weisser Leuchtring, ploppt rein + pulsiert)
  Pfeile: arrow_red (gerade, fliegt rein + federt), arrow_yellow (gebogen, wird gezeichnet + federt),
          arrow_white (handgemalt, wird gezeichnet + wackelt)
Position: Kreis -> Mittelpunkt (x,y); Pfeil -> Spitze (x,y). angle = Richtung, in die der Pfeil zeigt
(0 = rechts, 90 = unten, 180 = links, 270 = oben).
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter

FPS = 30
COLORS = {"red": (255, 40, 40, 255), "yellow": (255, 214, 0, 255), "white": (255, 255, 255, 255)}
BLACK = (0, 0, 0, 255)

def ease_out(p):
    return 1 - (1 - min(max(p, 0), 1)) ** 3

def _ring_points(cx, cy, r, p, wobble=0.0, seed=1, loops=1.0):
    rnd = random.Random(seed)
    n = 120
    noise = [rnd.uniform(-1, 1) for _ in range(8)]
    pts = []
    total = int(n * loops * p) + 1
    for i in range(total):
        a = -math.pi / 2 + 2 * math.pi * i / n
        w = sum(noise[k] * math.sin((k + 1) * a + k) for k in range(8)) / 8
        rr = r * (1 + wobble * w + (0.04 * i / n if loops > 1 else 0))
        pts.append((cx + rr * math.cos(a) * 1.08, cy + rr * math.sin(a)))
    return pts

def circle_frame(style, size, f, n):
    S = int(size * 1.4)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    t = f / FPS
    r0 = size / 2
    if style == "circle_red":
        p = ease_out(f / 8)
        r = r0 * (1 + 0.05 * math.sin(2 * math.pi * 2.2 * t) * (f > 8))
        pts = _ring_points(c, c, r, p)
        if len(pts) > 1:
            d.line(pts, fill=BLACK, width=max(6, size // 16), joint="curve")
            d.line(pts, fill=COLORS["red"], width=max(4, size // 26), joint="curve")
    elif style == "circle_yellow":
        p = ease_out(f / 10)
        jitter = 0.03 * math.sin(2 * math.pi * 6 * t)
        pts = _ring_points(c, c, r0 * (1 + jitter), p, wobble=0.12, seed=7, loops=1.25)
        if len(pts) > 1:
            d.line(pts, fill=BLACK, width=max(6, size // 15), joint="curve")
            d.line(pts, fill=COLORS["yellow"], width=max(4, size // 24), joint="curve")
    else:  # circle_glow
        if f < 6:
            k = [0.3, 0.6, 0.95, 1.12, 1.05, 1.0][f]
        else:
            k = 1 + 0.06 * math.sin(2 * math.pi * 1.8 * t)
        r = r0 * k
        glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse((c - r, c - r, c + r, c + r), outline=(255, 255, 255, 200), width=max(10, size // 10))
        glow = glow.filter(ImageFilter.GaussianBlur(size / 25))
        im.alpha_composite(glow)
        d = ImageDraw.Draw(im)
        d.ellipse((c - r, c - r, c + r, c + r), outline=COLORS["white"], width=max(4, size // 30))
    return im

def _arrow_shape(L, W, curved, p):
    """Pfeil zeigt nach rechts, Spitze bei (0,0). Gibt Schaft-Punkte und Spitzen-Polygon zurueck."""
    head = W * 2.6
    if curved:
        # Bezier von hinten-oben zur Spitze
        P0, P1, P2 = (-L, -L * 0.55), (-L * 0.35, -L * 0.6), (-head * 0.6, 0)
        steps = max(2, int(40 * p))
        shaft = []
        for i in range(steps + 1):
            u = i / 40
            x = (1 - u) ** 2 * P0[0] + 2 * (1 - u) * u * P1[0] + u * u * P2[0]
            y = (1 - u) ** 2 * P0[1] + 2 * (1 - u) * u * P1[1] + u * u * P2[1]
            shaft.append((x, y))
    else:
        start = -L
        end = -head * 0.6
        shaft = [(start, 0), (start + (end - start) * max(p, 0.05), 0)]
    tip = [(0, 0), (-head, -head * 0.6), (-head * 0.75, 0), (-head, head * 0.6)] if p >= 0.95 else None
    return shaft, tip

def arrow_frame(style, size, angle, f, n):
    S = int(size * 2.4)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    t = f / FPS
    L = size
    W = max(8, size // 9)
    curved = style == "arrow_yellow"
    color = COLORS["yellow" if curved else ("white" if style == "arrow_white" else "red")]
    if style == "arrow_red":
        p = 1.0
        back = (1 - ease_out(f / 6)) * size * 0.9 + abs(math.sin(2 * math.pi * 2.5 * t)) * size * 0.12 * (f >= 6)
    else:
        p = ease_out(f / 9)
        back = abs(math.sin(2 * math.pi * 2.2 * t)) * size * 0.10 * (f >= 9)
    shaft, tip = _arrow_shape(L, W, curved, p)
    wig = (math.sin(2 * math.pi * 5 * t) * size * 0.02) if style == "arrow_white" else 0
    def tr(pt):
        return (c + pt[0] - back, c + pt[1] + wig)
    shaft_t = [tr(q) for q in shaft]
    d.line(shaft_t, fill=BLACK, width=W + 10, joint="curve")
    if tip:
        d.polygon([tr(q) for q in tip], fill=BLACK)
        # Kontur der Spitze dicker
        tip_big = [(q[0] * 1.18 + 4, q[1] * 1.18) for q in tip]
        d.polygon([tr(q) for q in tip_big], fill=BLACK)
    d.line(shaft_t, fill=color, width=W, joint="curve")
    if tip:
        d.polygon([tr(q) for q in tip], fill=color)
    return im.rotate(-angle, resample=Image.BICUBIC, center=(c, c))

def render(o, out_dir):
    """o: dict mit style, start, end, size, angle. Schreibt out_dir/f0001.png ... und gibt (w,h) zurueck."""
    os.makedirs(out_dir, exist_ok=True)
    n = max(1, round((o["end"] - o["start"]) * FPS))
    size = o.get("size", 380 if o["style"].startswith("circle") else 230)
    for f in range(n):
        if o["style"].startswith("circle"):
            im = circle_frame(o["style"], size, f, n)
        else:
            im = arrow_frame(o["style"], size, o.get("angle", 45), f, n)
        im.save(os.path.join(out_dir, f"f{f + 1:04d}.png"))
    return im.size
