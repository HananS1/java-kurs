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

HL_COLORS = ["{\\c&H00E5FF&}", "{\\c&HFFF000&}", "{\\c&HFF55FF&}", "{\\c&H55FF55&}"]   # gelb, cyan, pink, gruen (BGR)

def make_ass_words(path, captions, font="Bangers", size=150, y=1150, multicolor=False, actions=None):
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
    allw = [w for c in captions for w in c.get("words", [])]
    hl_i = 0
    for a in (actions or []):
        # *Aktions-Text* (Shorts-Render-Stil): gelb, kleiner, oben, ploppt rein
        ay = a.get("y", 330)
        pop = "{\\pos(540,%d)\\fs%d\\c&H00E5FF&\\fscx60\\fscy60\\t(0,90,\\fscx110\\fscy110)\\t(90,150,\\fscx100\\fscy100)}" % (ay, int(size * 0.75))
        lines.append(f"Dialogue: 1,{ass_time(a['start'])},{ass_time(a['end'])},Cap,,0,0,0,,{pop}*{a['text'].upper()}*")
    for c in captions:
        hl = [w.lower() for w in c.get("highlight", [])]
        if c.get("words"):
            # exakte Wortzeiten (ElevenLabs): jedes Wort bleibt bis zum naechsten stehen
            for w, s, e in c["words"]:
                nxt = next((x[1] for x in allw if x[1] > s + 0.001), e + 0.3)
                col = ""
                if w.strip(".,…–!?").lower() in hl:
                    col = HL_COLORS[hl_i % len(HL_COLORS)] if multicolor else HL_COLORS[0]; hl_i += 1
                pop = "{\\pos(540,%d)\\fscx70\\fscy70\\t(0,70,\\fscx112\\fscy112)\\t(70,130,\\fscx100\\fscy100)}" % y
                lines.append(f"Dialogue: 0,{ass_time(s)},{ass_time(min(nxt, e + 0.6))},Cap,,0,0,0,,{pop}{col}{w.upper()}")
            continue
        words = c["text"].split()
        weights = [len(w) + 2 for w in words]
        tot = sum(weights); t = c["start"]; span = c["end"] - c["start"]
        for w, wt in zip(words, weights):
            d = span * wt / tot
            col = "{\\c&H00E5FF&}" if w.strip(".,…–!?").lower() in hl else ""
            pop = "{\\pos(540,%d)\\fscx70" % y + "\\fscy70\\t(0,70,\\fscx112\\fscy112)\\t(70,130,\\fscx100\\fscy100)}"
            lines.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t + d)},Cap,,0,0,0,,{pop}{col}{w.upper()}")
            t += d
    open(path, "w").write(head + "\n".join(lines) + "\n")

def make_ass_chunks(path, captions, font="MontserratXB", size=78, y=1210, actions=None, max_words=2):
    """1:1 Stil @shortsrender (gemessen): Montserrat ExtraBold, Versalhoehe ~55 px, weiss, duenner schwarzer Rand + weicher Schatten,
    1-3 Woerter, EIN Wort farbig (pink/gelb/cyan/gruen). Aktions-Texte: ganz cyan mit gelben Sternchen, Leucht-Rand, 2 Zeilen."""
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,0,0,0,0,100,100,1,0,1,3.5,3,5,120,120,0,1
Style: Act,{font},{int(size * 1.25)},&H00FFE618,&H00FFE618,&H00000000,&H78000000,0,0,0,0,100,100,1,0,1,4,2,5,110,110,0,1
Style: Glow,{font},{int(size * 1.25)},&H00FFE618,&H00FFE618,&H00FFE618,&H00000000,0,0,0,0,100,100,1,0,1,9,0,5,110,110,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    cols = ["&HD62BFF&", "&H00E6FF&", "&HFFE618&", "&H39FF14&"]          # pink, gelb, cyan, gruen (BGR)
    lines = []; ci = 0
    words = [w for c in captions for w in c.get("words", [])]
    hl = {h.lower() for c in captions for h in c.get("highlight", [])}
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= max_words or w[0][-1] in ".,!?…:" or sum(len(x[0]) for x in cur) > 14:
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    for k, ch in enumerate(chunks):
        s0 = ch[0][1]; e0 = ch[-1][2]
        nxt = chunks[k + 1][0][1] if k + 1 < len(chunks) else e0 + 0.4
        end = min(nxt, e0 + 0.35)
        txt, used = [], False
        for w, _, _ in ch:
            t = w.strip(".,…–!?:").upper()
            if not used and w.strip(".,…–!?:").lower() in hl:
                txt.append("{\\c" + cols[ci % 4] + "}" + t + "{\\c&HFFFFFF&}"); used = True; ci += 1
            else:
                txt.append(t)
        pop = "{\\pos(540,%d)\\blur0.6\\fscx90\\fscy90\\t(0,70,\\fscx103\\fscy103)\\t(70,120,\\fscx100\\fscy100)}" % y
        lines.append(f"Dialogue: 0,{ass_time(s0)},{ass_time(end)},Cap,,0,0,0,,{pop}{' '.join(txt)}")
    for a in (actions or []):
        body = a["text"].upper()
        ay = a.get("y", y)
        anim = "\\fscx88\\fscy88\\t(0,80,\\fscx104\\fscy104)\\t(80,140,\\fscx100\\fscy100)"
        star = "{\\c&H00E6FF&}*{\\c&HFFE618&}"
        lines.append(f"Dialogue: 1,{ass_time(a['start'])},{ass_time(a['end'])},Glow,,0,0,0,,{{\\pos(540,{ay})\\blur9\\alpha&H70&{anim}}}*{body}*")
        lines.append(f"Dialogue: 2,{ass_time(a['start'])},{ass_time(a['end'])},Act,,0,0,0,,{{\\pos(540,{ay})\\blur0.6{anim}}}{star}{body}{star}")
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
                    "vol": round(meta["vol"] * s.get("gain", 1.0) * cfg.get("sfx_gain", 1.0), 3), "name": name})
    print("Sounds:", ", ".join(f"{o['name']}@{o['time']:.2f}" for o in out))
    return out

def curve(m):
    """gain_curve [[t, dB], ...] -> ',volume=...' Ausdruck (z.B. Musik nur im Setup + Ende, im Tanzteil weg)."""
    gc = m.get("gain_curve")
    if not gc:
        return ""
    e = f"{10 ** (gc[-1][1] / 20):.4f}"
    for (t0, d0), (t1, d1) in reversed(list(zip(gc[:-1], gc[1:]))):
        a0, a1 = 10 ** (d0 / 20), 10 ** (d1 / 20)
        e = f"if(lt(t,{t1}),{a0:.4f}+({a1:.4f}-{a0:.4f})*clip((t-{t0})/{max(t1 - t0, 0.01)},0,1),{e})"
    return f",volume='{e}':eval=frame"


def main(cfg_path):
    cfg = json.load(open(cfg_path))
    base = os.path.dirname(os.path.abspath(cfg_path))
    os.chdir(base)
    voice = cfg["voice"]
    length = dur(voice) + cfg.get("tail", 0.6)

    make_arrow("arrow.png"); make_circle("circle.png")
    if cfg.get("caption_mode") == "chunk":
        make_ass_chunks("subs.ass", cfg["captions"], cfg.get("font", "MontserratXB"), cfg.get("font_size", 78),
                        cfg.get("caption_y", 1210), cfg.get("actions"), cfg.get("max_words", 2))
    elif cfg.get("caption_mode") == "word":
        make_ass_words("subs.ass", cfg["captions"], cfg.get("font", "Bangers"), cfg.get("font_size", 150), cfg.get("caption_y", 1150),
                       cfg.get("multicolor", False), cfg.get("actions"))
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
    zooms = cfg.get("zooms", []) if cfg.get("zoom_mode") == "zoompan" else []
    if zooms:
        cond = "+".join(f"between(in,{int(z['start']*FPS)},{int(z['end']*FPS)})" for z in zooms)
        vsrc += (f",zoompan=z='if({cond},{cfg.get('zoom_factor',1.18)},1)':d=1:"
                 f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}")
    filt = [vsrc + "[v0]"]

    # Overlays (Pfeile/Kreise)
    inputs = vin + ["-i", voice, "-i", "arrow.png", "-i", "circle.png"]
    # Regel: Overlay endet spaetestens am Schnitt seines Shots (nie ueber einen Schnitt hinweg)
    if os.path.exists("shots.json"):
        shot_list = json.load(open("shots.json"))["shots"]
        for o in cfg.get("overlays", []):
            sh = next((s for s in shot_list if s["start"] <= o["start"] + 0.001 < s["end"]), None)
            if sh and o["end"] > sh["end"]:
                print(f"  Overlay {o.get('style')} @{o['start']}: Ende {o['end']} -> Schnitt {sh['end']}")
                o["end"] = sh["end"]
                if "keys" in o:
                    o["keys"] = [k for k in o["keys"] if k[0] <= sh["end"]] or o["keys"][:1]
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
        if o.get("follow", True) and clip and os.path.exists(clip) and (o["style"].startswith("circle") or "track" in o):
            # Mitbewegen: Ziel Bild fuer Bild verfolgen, Overlay als Vollbild-Sequenz
            tspec2 = importlib.util.spec_from_file_location("track", os.path.join(os.path.dirname(os.path.abspath(__file__)), "track.py"))
            trk = importlib.util.module_from_spec(tspec2); tspec2.loader.exec_module(trk)
            if o["style"].startswith("circle"):
                cx, cy, box = o["x"], o["y"], o.get("track_box", int(o.get("size", 380) * 0.55))
            else:
                cx, cy, box = o["track"]          # Pfeil: [Ziel-x, Ziel-y, Ziel-Groesse]
            if "keys" in o:
                # Keyframes [[t, x, y, scale], ...] (gemessen) -> weich interpolieren; zuverlaessiger bei schnellen Schwenks
                import numpy as np
                ks = sorted(o["keys"])
                n = max(1, round((o["end"] - o["start"]) * FPS))
                ts = o["start"] + np.arange(n) / FPS
                kt = [k[0] for k in ks]
                path = list(zip(np.interp(ts, kt, [k[1] for k in ks]), np.interp(ts, kt, [k[2] for k in ks]),
                                np.interp(ts, kt, [k[3] if len(k) > 3 else 1.0 for k in ks])))
                if not o["style"].startswith("circle"):
                    # Pfeil: Spitze relativ zum ersten Keyframe-Ziel
                    o.setdefault("track", [ks[0][1], ks[0][2], 150])
                    path = [(x + (o["track"][0] - ks[0][1]) * 0, y, s) for x, y, s in path]
            else:
                path = trk.follow_path(clip, o["start"], o["end"], cx, cy, box, FPS)
            fx.render_follow(o, path, d)
            moved = max(abs(p[0] - path[0][0]) + abs(p[1] - path[0][1]) for p in path)
            print(f"  folgt: {o['style']:13s} @{o['start']:5.2f}  Bewegung max {moved:.0f}px")
            inputs += ["-itsoffset", f"{o['start']:.3f}", "-framerate", str(FPS), "-i", f"{d}/f%04d.png"]
            lbl = f"ov{i}"
            filt.append(f"[{last}][{idx}:v]overlay=0:0:eof_action=pass:"
                        f"enable='between(t,{o['start']},{o['end']})'[{lbl}]")
            last = lbl
            idx += 1
            continue
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
    oa = cfg.get("orig_audio")
    if oa:
        # Originalton (Hybrid-Stil): voll in den Sprechpausen, unter der Stimme stark geduckt
        # Lautstaerke-Kurve: unter jedem Stimm-Block auf under_db, mit weichen Rampen
        blocks = []
        for c in cfg["captions"]:
            a0, b0 = c["start"] - 0.15, c["end"] + 0.2
            if blocks and a0 <= blocks[-1][1] + 0.4: blocks[-1][1] = b0
            else: blocks.append([a0, b0])
        lo = 10 ** (oa.get("under_db", -20) / 20); r = 0.15
        expr = "1"
        for a0, b0 in blocks:
            expr = (f"min({expr},1-(1-{lo:.4f})*clip(min((t-{a0 - r:.3f})/{r},({b0 + r:.3f}-t)/{r}),0,1))")
        inputs += ["-i", oa["path"]]
        g = f"volume={oa.get('gain_db', 0)}dB"
        if oa.get("gain_curve"):   # [[t, dB], ...] Grundlautstaerke ueber die Zeit (z.B. Anfang lauter, Tanzteil leiser)
            gc = oa["gain_curve"]; e = f"{10 ** (gc[-1][1] / 20):.4f}"
            for (t0, d0), (t1, d1) in reversed(list(zip(gc[:-1], gc[1:]))):
                a0, a1 = 10 ** (d0 / 20), 10 ** (d1 / 20)
                e = f"if(lt(t,{t1}),{a0:.4f}+({a1:.4f}-{a0:.4f})*clip((t-{t0})/{max(t1 - t0, 0.01)},0,1),{e})"
            g = f"volume='{e}':eval=frame"
        amix.append(f"[{idx}:a]aresample=44100,aformat=channel_layouts=stereo,{g},"
                    f"volume='{expr}':eval=frame[a_od]")
        labels.append("[a_od]")
        idx += 1
    m = cfg.get("music")
    if m:
        amix[0] = "[1:a]volume=1.0,asplit=2[a_voice][a_key]"
        # Musik: Ausschnitt ab m.start, Grundlautstaerke m.gain_db, wird unter der Stimme geduckt
        inputs += ["-ss", str(m.get("start", 0)), "-i", m["path"]]
        fade_out = max(0, length - m.get("fade_out", 1.0))
        amix.append(f"[{idx}:a]aresample=44100,aformat=channel_layouts=stereo,"
                    f"volume={m.get('gain_db', -16)}dB,afade=t=in:d={m.get('fade_in', 0.3)},"
                    f"afade=t=out:st={fade_out:.2f}:d={m.get('fade_out', 1.0)}{curve(m)}[a_mus]")
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
         "-t", f"{length:.2f}", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    print("fertig:", os.path.abspath(out), f"({length:.1f}s)")

if __name__ == "__main__":
    main(sys.argv[1])
