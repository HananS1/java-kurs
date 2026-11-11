"""Fuellt dunkle Loecher (fehlende Satellitendaten) in den Mosaiken. Aufruf: python3 -I fill_holes.py <patches-ordner>"""
import sys, json
from PIL import Image, ImageFilter
import numpy as np
d = sys.argv[1]
for k in json.load(open(d + '/meta.json')):
    a = np.asarray(Image.open(f'{d}/{k}.jpg').convert('RGB'), dtype=np.float32)
    bad = np.asarray(Image.fromarray(((a.mean(-1) < 14) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
    good = (~bad).astype(np.float32); out = a.copy()
    for r in (4, 10, 24):
        w = np.asarray(Image.fromarray((good * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255
        num = np.stack([np.asarray(Image.fromarray((a[..., c] * good).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) for c in range(3)], -1)
        sel = bad & (w > 0.05); out[sel] = (num / np.maximum(w[..., None], 1e-3))[sel]
        a = out.copy(); good = np.maximum(good, sel.astype(np.float32)); bad = bad & ~sel
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(f'{d}/{k}.jpg', quality=92)
    print(k, 'ok')
