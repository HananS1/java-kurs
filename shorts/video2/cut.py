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
    for i, s in enumerate(cfg["shots"]):
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
        if s.get("delogo"):
            lx, ly, lw, lh = s["delogo"]
            base += f",delogo=x={lx}:y={ly}:w={lw}:h={lh}"
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
                f"{base},crop={w}:{h}:'{xexpr}':{y},scale={W}:{H}:flags=lanczos,setsar=1[p{i}]")
    n = len(parts)
    fc = ";".join(parts) + ";" + "".join(f"[p{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", cfg["source"],
                    "-filter_complex", fc, "-map", "[v]", "-an",
                    "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p",
                    cfg["out"]], check=True)
    print("Schnitt fertig:", cfg["out"])

if __name__ == "__main__":
    main(sys.argv[1])
