#!/usr/bin/env python3
"""Baut ein Shorts-Video: Clip + Stimme + Untertitel + Pfeile/Kreise + Soundeffekte + Zoom.
Aufruf: python3 build.py config.json
"""
import json, subprocess, sys, os
from PIL import Image, ImageDraw

W, H, FPS = 1080, 1920, 30
FONT = "Inter Black"

def run(cmd):
    subprocess.run(cmd, check=True)

def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())

def make_arrow(path, color=(255, 30, 30, 255)):
    im = Image.new("RGBA", (260, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Pfeil zeigt nach unten-rechts (Spitze unten rechts)
    pts = [(20, 60), (60, 20), (170, 130), (200, 100), (230, 230), (100, 200), (130, 170)]
    d.polygon(pts, fill=(0, 0, 0, 255))
    inner = [(34, 60), (60, 34), (172, 146), (198, 120), (216, 216), (120, 198), (146, 172)]
    d.polygon(inner, fill=color)
    im.save(path)

def make_circle(path, color=(255, 30, 30, 255)):
    im = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((10, 10, 410, 410), outline=(0, 0, 0, 255), width=26)
    d.ellipse((16, 16, 404, 404), outline=color, width=14)
    im.save(path)

def ass_time(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def make_ass_words(path, captions, font="Bangers", size=150):
    """Ein Wort pro Einblendung, wie bei ClipErklaert: dicker Comic-Font, weiss mit schwarzem Rand."""
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,2,0,1,9,4,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for c in captions:
        words = c["text"].split()
        weights = [len(w) + 2 for w in words]
        tot = sum(weights); t = c["start"]; span = c["end"] - c["start"]
        hl = [w.lower() for w in c.get("highlight", [])]
        for w, wt in zip(words, weights):
            d = span * wt / tot
            col = "{\\c&H00E5FF&}" if w.strip(".,…–!?").lower() in hl else ""
            pop = "{\\pos(540,1150)\\fscx70\\fscy70\\t(0,70,\\fscx112\\fscy112)\\t(70,130,\\fscx100\\fscy100)}"
            lines.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t + d)},Cap,,0,0,0,,{pop}{col}{w.upper()}")
            t += d
    open(path, "w").write(head + "\n".join(lines) + "\n")

def make_ass(path, captions, words_per_chunk=3):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONT},96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,7,3,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for c in captions:
        words = c["text"].split()
        chunks = [words[i:i + words_per_chunk] for i in range(0, len(words), words_per_chunk)]
        total = sum(len(" ".join(ch)) for ch in chunks)
        t = c["start"]; span = c["end"] - c["start"]
        hl = [w.lower() for w in c.get("highlight", [])]
        for ch in chunks:
            d = span * len(" ".join(ch)) / total
            txt = " ".join(
                ("{\\c&H00E5FF&}" + w.upper() + "{\\c&HFFFFFF&}") if w.strip(".,…–!?").lower() in hl
                else w.upper()
                for w in ch)
            pop = "{\\pos(540,1180)\\fscx80\\fscy80\\t(0,90,\\fscx105\\fscy105)\\t(90,160,\\fscx100\\fscy100)}"
            lines.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t + d)},Cap,,0,0,0,,{pop}{txt}")
            t += d
    open(path, "w").write(head + "\n".join(lines) + "\n")

def resolve_sfx(cfg):
    """'@gruppe' -> naechster Sound der Gruppe (nie zweimal derselbe hintereinander),
    Lautstaerke und Vorlauf aus library.json. Einzelne Sounds per Name gehen auch."""
    lib_dir = cfg.get("sfx_lib")
    if not lib_dir:
        return [{"path": f"sfx/{s['sound']}.wav", "time": s["time"], "vol": s.get("vol", 0.6)}
                for s in cfg.get("sfx", [])]
    lib = json.load(open(os.path.join(lib_dir, "library.json")))
    pos = {g: 0 for g in lib["groups"]}
    last = None
    out = []
    for s in sorted(cfg.get("sfx", []), key=lambda x: x["time"]):
        name = s["sound"]
        if name.startswith("@"):
            g = lib["groups"][name[1:]]
            for _ in range(len(g)):
                cand = g[pos[name[1:]] % len(g)]
                pos[name[1:]] += 1
                if cand != last or len(set(g)) == 1:
                    break
            name = cand
        meta = lib["sounds"][name]
        last = name
        t = s["time"] - (meta["lead"] if s.get("on_cut", name in sum([lib["groups"]["transition"]], [])) else 0)
        out.append({"path": os.path.join(lib_dir, name + ".wav"), "time": t,
                    "vol": round(meta["vol"] * s.get("gain", 1.0), 3), "name": name})
    print("Sounds:", ", ".join(f"{o['name']}@{o['time']:.2f}" for o in out))
    return out

def main(cfg_path):
    cfg = json.load(open(cfg_path))
    base = os.path.dirname(os.path.abspath(cfg_path))
    os.chdir(base)
    voice = cfg["voice"]
    length = dur(voice) + cfg.get("tail", 0.6)

    make_arrow("arrow.png"); make_circle("circle.png")
    if cfg.get("caption_mode") == "word":
        make_ass_words("subs.ass", cfg["captions"], cfg.get("font", "Bangers"), cfg.get("font_size", 150))
    else:
        make_ass("subs.ass", cfg["captions"])

    # --- Video-Quelle ---
    clip = cfg.get("clip")
    if clip and os.path.exists(clip):
        vin = ["-stream_loop", "-1", "-ss", str(cfg.get("clip_start", 0)), "-i", clip]
        vsrc = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"setsar=1,fps={FPS}")
        if cfg.get("mirror"):
            vsrc += ",hflip"
    else:
        vin = ["-f", "lavfi", "-i", f"color=c=0x1b1f2a:s={W}x{H}:r={FPS}"]
        vsrc = ("[0:v]drawtext=font='Inter Black':text='DEIN CLIP HIER':fontcolor=0x5a6375:"
                "fontsize=90:x=(w-tw)/2:y=500")

    # Punch-in-Zooms
    zooms = cfg.get("zooms", [])
    if zooms:
        cond = "+".join(f"between(in,{int(z['start']*FPS)},{int(z['end']*FPS)})" for z in zooms)
        vsrc += (f",zoompan=z='if({cond},{cfg.get('zoom_factor',1.18)},1)':d=1:"
                 f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    filt = [vsrc + "[v0]"]

    # Overlays (Pfeile/Kreise)
    inputs = vin + ["-i", voice, "-i", "arrow.png", "-i", "circle.png"]
    last = "v0"
    anim = []
    for i, o in enumerate(cfg.get("overlays", [])):
        lbl = f"ov{i}"
        if "style" in o:
            anim.append((i, o))
            continue
        src = "2:v" if o["type"] == "arrow" else "3:v"
        filt.append(f"[{src}]scale={o.get('size', 260 if o['type']=='arrow' else 420)}:-1[s{i}]")
        filt.append(f"[{last}][s{i}]overlay=x={o['x']}:y={o['y']}:"
                    f"enable='between(t,{o['start']},{o['end']})'[{lbl}]")
        last = lbl
    # animierte Kreise/Pfeile (PNG-Sequenzen aus fx.py); x,y = Mittelpunkt bzw. Pfeilspitze,
    # optional x_end/y_end = Bewegung waehrend der Einblendung
    import importlib.util, shutil
    spec = importlib.util.spec_from_file_location("fx", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fx.py"))
    fx = importlib.util.module_from_spec(spec); spec.loader.exec_module(fx)
    shutil.rmtree("fx_tmp", ignore_errors=True)
    idx = 4
    if any("target" in o for _, o in anim):
        tspec = importlib.util.spec_from_file_location("track", os.path.join(os.path.dirname(os.path.abspath(__file__)), "track.py"))
        track = importlib.util.module_from_spec(tspec); tspec.loader.exec_module(track)
        for _, o in anim:
            if "target" in o:
                track.place(o, clip)
                if o.get("_skip"):
                    continue
                print(f"  {o['style']:13s} @{o['start']:5.2f}  Ziel {o['_target']}  -> x={o['x']} y={o['y']} size={o.get('size')}")
        anim = [(i, o) for i, o in anim if not o.get("_skip")]
        # Regel: waehrend eines Zooms keine Overlays (sonst passen Positionen nicht)
        for z in cfg.get("zooms", []):
            for _, o in anim:
                if o["start"] < z["end"] and o["end"] > z["start"]:
                    print(f"  !! WARNUNG: {o['style']} @{o['start']} ueberlappt Zoom {z}")
    for i, o in anim:
        d = f"fx_tmp/o{i}"
        w, h = fx.render(o, d)
        inputs += ["-itsoffset", f"{o['start']:.3f}", "-framerate", str(FPS), "-i", f"{d}/f%04d.png"]
        ov_len = o["end"] - o["start"]
        x1, y1 = o.get("x_end", o["x"]), o.get("y_end", o["y"])
        pos = lambda a, b, half: (f"{a}-{half}+({b}-{a})*min(max((t-{o['start']})/{ov_len:.3f}\\,0)\\,1)")
        lbl = f"ov{i}"
        filt.append(f"[{last}][{idx}:v]overlay=x='{pos(o['x'], x1, w // 2)}':y='{pos(o['y'], y1, h // 2)}':"
                    f"eof_action=pass:enable='between(t,{o['start']},{o['end']})'[{lbl}]")
        last = lbl
        idx += 1
    filt.append(f"[{last}]ass=subs.ass[vout]")

    # Audio: Stimme + Soundeffekte (+ optional leiser Original-Ton)
    sfx = resolve_sfx(cfg)
    amix = ["[1:a]volume=1.0[a_voice]"]
    labels = ["[a_voice]"]
    for j, s in enumerate(sfx):
        inputs += ["-i", s["path"]]
        ms = max(0, int(s["time"] * 1000))
        amix.append(f"[{idx}:a]adelay={ms}|{ms},volume={s['vol']}[sx{j}]")
        labels.append(f"[sx{j}]")
        idx += 1
    if clip and os.path.exists(clip) and cfg.get("clip_audio", 0) > 0:
        amix.append(f"[0:a]volume={cfg['clip_audio']}[a_clip]")
        labels.append("[a_clip]")
    m = cfg.get("music")
    if m:
        # Musik: Ausschnitt ab m.start, Grundlautstaerke m.gain_db, wird unter der Stimme geduckt
        inputs += ["-ss", str(m.get("start", 0)), "-i", m["path"]]
        amix[0] = "[1:a]volume=1.0,asplit=2[a_voice][a_key]"
        fade_out = max(0, length - m.get("fade_out", 1.0))
        amix.append(f"[{idx}:a]aresample=44100,aformat=channel_layouts=stereo,"
                    f"volume={m.get('gain_db', -16)}dB,afade=t=in:d={m.get('fade_in', 0.3)},"
                    f"afade=t=out:st={fade_out:.2f}:d={m.get('fade_out', 1.0)}[a_mus]")
        amix.append(f"[a_key]aformat=channel_layouts=stereo[a_key2]")
        amix.append(f"[a_mus][a_key2]sidechaincompress=threshold={m.get('duck_threshold', 0.02)}:"
                    f"ratio={m.get('duck_ratio', 4)}:attack=15:release=300:makeup=1[a_musd]")
        labels.append("[a_musd]")
        idx += 1
    amix.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,"
                f"alimiter=limit=0.95[aout]")

    fc = ";".join(filt + amix)
    out = cfg.get("out", "final.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error"] + inputs +
        ["-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
         "-t", f"{length:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    print("fertig:", os.path.abspath(out), f"({length:.1f}s)")

if __name__ == "__main__":
    main(sys.argv[1])
