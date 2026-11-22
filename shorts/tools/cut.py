#!/usr/bin/env python3
"""Schneidet aus einem 16:9-Clip ein 9:16-Video passend zur Stimme.
Jeder Shot: [Start im Video, Ende im Video, Start in der Quelle, Ausschnitt x,y,w,h, optional x_end fuer Kamerafahrt]
Aufruf: python3 cut.py shots.json
"""
import json, subprocess, sys, os

W, H, FPS = 1080, 1920, 30

def main(path):
    cfg = json.load(open(path))
    os.chdir(os.path.dirname(os.path.abspath(path)))
    parts = []
    shots = []
    for s in cfg["shots"]:
        # Punch-in ab Zeitpunkt punch_at: zweiter Teil mit engerem Ausschnitt AUS DEN ORIGINALPIXELN
        if "punch_at" in s and s["start"] < s["punch_at"] < s["end"]:
            f = s.get("punch", 1.18)
            a = dict(s); a["end"] = s["punch_at"]; a.pop("punch_at"); a.pop("x_end", None)
            b = dict(s); b.pop("punch_at"); b.pop("x_end", None)
            b["start"] = s["punch_at"]; b["src"] = s["src"] + (s["punch_at"] - s["start"])
            w, h = s.get("w", 405), s.get("h", 720)
            nw, nh = int(w / f) // 2 * 2, int(h / f) // 2 * 2
            b["x"] = int(s["x"] + (w - nw) / 2); b["y"] = int(s.get("y", 0) + (h - nh) / 2); b["w"], b["h"] = nw, nh
            if b.get("mode") == "fit": b.pop("mode")
            shots += [a, b]
        else:
            shots.append(s)
    for i, s in enumerate(shots):
        d = s["end"] - s["start"]
        w, h = s.get("w", 405), s.get("h", 720)
        x0, y = s["x"], s.get("y", 0)
        x1 = s.get("x_end", x0)
        xexpr = f"{x0}+({x1}-{x0})*min(t/{d:.3f}\\,1)" if x1 != x0 else str(x0)
        # framegenau: Laenge aus gerundeten Bildnummern, damit sich nichts verschiebt
        nfr = round(s["end"] * FPS) - round(s["start"] * FPS)
        sf = round(s["src"] * FPS)
        base = (f"[0:v]fps={FPS},trim=start_frame={sf}:end_frame={sf + nfr},"
                f"setpts=PTS-STARTPTS")
        sp = s.get("speed", 1.0)
        if sp != 1.0:
            # Zeitlupe/Zeitraffer: aus der Quelle (am besten 60 fps) d*speed Sekunden nehmen und strecken
            base = (f"[0:v]trim=start={s['src']}:duration={nfr / FPS * sp:.4f},setpts=(PTS-STARTPTS)/{sp},"
                    f"fps={FPS},trim=end_frame={nfr},setpts=PTS-STARTPTS")
        if s.get("delogo"):
            lx, ly, lw, lh = s["delogo"]
            base += f",delogo=x={lx}:y={ly}:w={lw}:h={lh}"
        if s.get("blur"):
            # eingebrannten Text stark verwischen (Bereich in Quell-Pixeln)
            bx, by, bw, bh = s["blur"]
            base += (f",split[m{i}][r{i}];[r{i}]crop={bw}:{bh}:{bx}:{by},boxblur=28:4[b{i}];"
                     f"[m{i}][b{i}]overlay={bx}:{by}")
        if s.get("mode") == "fit":
            # ganzes Bild zeigen, Hintergrund unscharf
            parts.append(
                f"{base},split[a{i}][b{i}];"
                f"[a{i}]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=25:2,"
                f"eq=brightness=-0.15[bg{i}];"
                f"[b{i}]scale={W}:-2:flags=lanczos[fg{i}];"
                f"[bg{i}][fg{i}]overlay=0:(H-h)/2-{s.get('lift', 250)},setsar=1[p{i}]")
        else:
            parts.append(
                f"{base},crop={w}:{h}:'{xexpr}':{y},scale={W}:{H}:flags=lanczos"
                + (",unsharp=5:5:0.45:5:5:0.0" if w < 540 else "")   # starke Vergroesserung: leicht nachschaerfen
                + f",setsar=1[p{i}]")
    n = len(parts)
    fc = ";".join(parts) + ";" + "".join(f"[p{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", cfg["source"],
                    "-filter_complex", fc, "-map", "[v]", "-an",
                    "-c:v", "libx264", "-crf", "6", "-preset", "fast", "-pix_fmt", "yuv420p",
                    cfg["out"]], check=True)
    print("Schnitt fertig:", cfg["out"])

if __name__ == "__main__":
    main(sys.argv[1])
