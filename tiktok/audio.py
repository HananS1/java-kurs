"""Builds music + sound effects from the timeline that engine.js exports.

Everything is synthesised, so beats and hits land exactly on the frames
where text and visuals change. Usage: python3 audio.py timeline.json out.wav
"""
import json
import sys
import wave

import numpy as np

SR = 44100
rnd = np.random.default_rng(7)

NOTE = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}


def hz(name, octave):
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octave + 1) - 69) / 12)


CHORDS = {
    'Am': ['A', 'C', 'E'], 'F': ['F', 'A', 'C'], 'Dm': ['D', 'F', 'A'], 'E': ['E', 'G#', 'B'],
    'C': ['C', 'E', 'G'], 'G': ['G', 'B', 'D'],
}
DARK = ['Am', 'F', 'Dm', 'E']
BRIGHT = ['C', 'G', 'Am', 'F']


def env(n, a, r):
    e = np.ones(n)
    a, r = int(a * SR), int(r * SR)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] *= np.linspace(1, 0, r)
    return e


def lowpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def highpass(x, cutoff):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def add(buf, t, sig, gain=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[:j - i] * gain


# ---------- instruments ----------
def pad(chord, dur, bright=False):
    n = int(dur * SR); tt = np.arange(n) / SR
    out = np.zeros(n)
    for k, note in enumerate(CHORDS[chord]):
        for det in (-0.12, 0.12):
            f = hz(note, 3 if k == 0 else 4) * 2 ** (det / 12)
            for h in range(1, 6):
                out += np.sin(2 * np.pi * f * h * tt) / (h * 1.6)
    root = hz(CHORDS[chord][0], 2)
    out += 1.4 * np.sin(2 * np.pi * root * tt)
    out *= env(n, 0.25, 0.25) * (0.9 + 0.1 * np.sin(2 * np.pi * 0.5 * tt))
    return lowpass(out, 2200 if bright else 1300) * 0.02


def pluck(f, dur=0.45):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (6 + 3 * h)) / h for h in range(1, 6))
    return s * env(n, 0.003, 0.05)


def kick():
    n = int(0.35 * SR); tt = np.arange(n) / SR
    f = 45 + 90 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)


def hat():
    n = int(0.05 * SR)
    return highpass(rnd.standard_normal(n), 7000) * np.exp(-np.arange(n) / SR * 80)


def heartbeat():
    n = int(0.25 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 18)


def saw(f, n, harmonics=8):
    tt = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * h * tt) / h for h in range(1, harmonics + 1))


def bass(f, dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    return lowpass(saw(f, n, 6), 500) * np.exp(-tt * 5) * env(n, 0.004, 0.03)


def stab(f, dur=0.12, cutoff=2800, harmonics=7):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = saw(f, n, harmonics) + saw(f * 1.004, n, harmonics)
    return lowpass(s, cutoff) * np.exp(-tt * 18) * env(n, 0.003, 0.02)


def clap():
    n = int(0.25 * SR); tt = np.arange(n) / SR
    x = rnd.standard_normal(n)
    e = np.exp(-tt * 22) + 0.6 * np.exp(-np.maximum(0, tt - 0.012) * 40) * (tt > 0.012)
    return highpass(lowpass(x, 6000), 900) * e + np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 30) * 0.5


def taiko():
    n = int(0.8 * SR); tt = np.arange(n) / SR
    f = 70 + 60 * np.exp(-tt * 25)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6) + lowpass(rnd.standard_normal(n), 800) * np.exp(-tt * 30) * 0.5


def crash():
    n = int(2.2 * SR); tt = np.arange(n) / SR
    return highpass(rnd.standard_normal(n), 4000) * np.exp(-tt * 2.2) * 0.6


def braam(root):
    n = int(2.4 * SR); tt = np.arange(n) / SR
    s = sum(saw(root * m, n, 10) for m in (1, 1.5, 2, 1.003))
    return lowpass(s, 1200) * env(n, 0.02, 1.5) * np.exp(-tt * 0.9) * 0.4


# ---------- sfx ----------
def whoosh(dur=0.35, up=True):
    n = int(dur * SR)
    x = rnd.standard_normal(n)
    out = np.zeros(n); parts = 12
    for p in range(parts):
        a, b = p * n // parts, (p + 1) * n // parts
        k = p / parts if up else 1 - p / parts
        seg = lowpass(x, 600 + 5000 * k)[a:b]
        out[a:b] = seg
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out * e * 0.5


def boom():
    n = int(1.6 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * (40 + 50 * np.exp(-tt * 8)) * tt) * np.exp(-tt * 2.5)
    s += lowpass(rnd.standard_normal(n), 400) * np.exp(-tt * 5) * 0.8
    return s


def hit():
    s = boom() * 1.1
    n = len(s); tt = np.arange(n) / SR
    s += highpass(rnd.standard_normal(n), 3000) * np.exp(-tt * 12) * 0.4
    return s


def stamp_sfx():
    n = int(0.3 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 110 * tt) * np.exp(-tt * 25) + lowpass(rnd.standard_normal(n), 2500) * np.exp(-tt * 40) * 0.8


def click():
    n = int(0.02 * SR)
    return highpass(rnd.standard_normal(n), 2500) * np.exp(-np.arange(n) / SR * 250)


def tick():
    n = int(0.03 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt * 150)


def burner(dur=0.9):
    n = int(dur * SR)
    s = lowpass(rnd.standard_normal(n), 900) + lowpass(rnd.standard_normal(n), 3500) * 0.3
    return s * env(n, 0.06, 0.4) * 0.9


def wind(dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = lowpass(rnd.standard_normal(n), 500)
    return s * env(n, 0.5, 0.8) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * tt))


def riser(dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = 200 * 2 ** (tt / dur * 2.5)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + highpass(rnd.standard_normal(n), 2000) * 0.25
    return s * (tt / dur) ** 2


def sew():
    out = np.zeros(int(2.0 * SR))
    for k in range(36):
        add(out, k * 0.055, click(), 0.8)
    return out


def fizzle():
    n = int(1.2 * SR); tt = np.arange(n) / SR
    return lowpass(rnd.standard_normal(n), 1500) * np.exp(-tt * 3) * (np.sin(2 * np.pi * 9 * tt) > -0.3)


def thud():
    n = int(0.6 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 60 * tt) * np.exp(-tt * 10) + lowpass(rnd.standard_normal(n), 300) * np.exp(-tt * 12)


def splash():
    n = int(1.4 * SR); tt = np.arange(n) / SR
    s = lowpass(rnd.standard_normal(n), 2500) * np.exp(-tt * 4) + np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 12)
    bub = np.zeros(n)
    for k in range(14):
        i = int((0.15 + rnd.random() * 1.0) * SR); m = int(0.04 * SR)
        if i + m < n:
            f = 400 + rnd.random() * 700
            bub[i:i + m] += np.sin(2 * np.pi * f * (1 + np.arange(m) / m) * np.arange(m) / SR) * np.exp(-np.arange(m) / SR * 60)
    return s + bub * 0.3


def smash():
    n = int(0.9 * SR); tt = np.arange(n) / SR
    s = highpass(rnd.standard_normal(n), 1500) * np.exp(-tt * 7) * 0.8
    for k in range(10):
        i = int(rnd.random() * 0.5 * SR); m = int(0.03 * SR)
        s[i:i + m] += highpass(rnd.standard_normal(m), 3000) * np.exp(-np.arange(m) / SR * 80)
    return s + boom()[:n] * 0.6


def flash_sfx():
    n = int(0.25 * SR); tt = np.arange(n) / SR
    c = click()
    return np.concatenate([c, np.zeros(n - len(c))]) + np.sin(2 * np.pi * (3000 + 4000 * tt) * tt) * np.exp(-tt * 20) * 0.3


def trumpet(dur=0.9):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = 330 + 260 * np.sin(np.pi * np.minimum(1, tt / dur)) + 12 * np.sin(2 * np.pi * 7 * tt)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(np.sin(ph * h) / h for h in range(1, 9))
    return lowpass(s, 3500) * env(n, 0.05, 0.25) * 0.5


def thunder():
    n = int(2.5 * SR); tt = np.arange(n) / SR
    crack = highpass(rnd.standard_normal(n), 2000) * np.exp(-tt * 18)
    roll = lowpass(rnd.standard_normal(n), 180) * np.exp(-tt * 1.4) * (1 + 0.5 * np.sin(2 * np.pi * 3 * tt))
    return crack * 0.7 + roll * 2.2


def rain_sfx(dur):
    n = int(dur * SR)
    return highpass(lowpass(rnd.standard_normal(n), 6000), 800) * env(n, 0.4, 0.6) * 0.35


# ---------- dark epic style (sub drone, staccato strings, hits on every beat) ----------
def sub(f, dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt)
    return np.tanh(s * 1.6) * env(n, 0.02, 0.08)


def choir(notes, dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    out = np.zeros(n)
    for f in notes:
        for det in (-0.08, 0.08):
            ff = f * 2 ** (det / 12) * (1 + 0.004 * np.sin(2 * np.pi * 5 * tt))
            ph = 2 * np.pi * np.cumsum(ff) / SR
            out += np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    return lowpass(out, 1800) * env(n, 0.4, 0.4) * 0.03


def perc_hit():
    n = int(0.5 * SR); tt = np.arange(n) / SR
    f = 60 + 90 * np.exp(-tt * 30)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 8)
    return body + highpass(rnd.standard_normal(n), 1200) * np.exp(-tt * 35) * 0.5


def dark_epic(tl, n):
    beat = tl['beat']; off = tl.get('offset', 0)
    music = np.zeros(n)
    roots = tl.get('roots') or [[0, 'F#']]
    def root_at(t):
        r = roots[0][1]
        for t0, name in roots:
            if t >= t0: r = name
        return r
    for sc in tl['scenes']:
        mode = sc['music']
        nb = int(round((sc['end'] - sc['start']) / beat))
        for b in range(nb):
            bt = sc['start'] + b * beat
            r = root_at(bt)
            f1 = hz(r, 1)
            bright = mode in ('reveal', 'outro')
            third = 4 if bright else 3
            if mode != 'outro' or b % 4 == 0:
                add(music, bt, sub(f1, beat * (1.0 if mode != 'outro' else 4)), 0.42)
            # staccato string ostinato: root, fifth, octave, flat second (phrygian bite)
            pat = [0, 7, 12, 13] if not bright else [0, 7, 12, third + 12]
            if mode in ('drive', 'reveal', 'intro'):
                for e in range(2):
                    semis = pat[(b * 2 + e) % 4]
                    acc = 0.34 if e == 0 else 0.22
                    if mode == 'intro': acc *= 0.6 + 0.4 * b / max(1, nb)
                    add(music, bt + e * beat / 2, stab(f1 * 4 * 2 ** (semis / 12), 0.16, 6000, 14), acc)
                    add(music, bt + e * beat / 2, stab(f1 * 8 * 2 ** (semis / 12), 0.1, 7000, 10), acc * 0.7)
            if mode in ('drive', 'reveal'):
                add(music, bt, perc_hit(), 0.55)
                add(music, bt + beat / 2, hat(), 0.32)
                add(music, bt, hat(), 0.2)
                if b % 2 == 1: add(music, bt, clap(), 0.45)
            elif mode == 'intro':
                add(music, bt, taiko(), 0.5 if b % 2 == 0 else 0.3)
            elif mode == 'tension':
                if b % 2 == 0: add(music, bt, heartbeat(), 0.6); add(music, bt + 0.22, heartbeat(), 0.4)
                add(music, bt + beat / 2, tick(), 0.12)
            if b % 4 == 0 and mode != 'outro':
                ch = [f1 * 4, f1 * 4 * 2 ** (third / 12), f1 * 6]
                add(music, bt, choir(ch, beat * 4.2), 2.6 if mode != 'tension' else 1.8)
        prev = [x for x in tl['scenes'] if abs(x['end'] - sc['start']) < 1e-6]
        if prev and prev[0]['music'] != mode and mode in ('drive', 'reveal'):
            add(music, sc['start'], braam(hz(root_at(sc['start']), 1)), 0.8)
            add(music, sc['start'], crash(), 0.5)
    return tilt_eq(music, [(80, 0), (250, -4), (1000, 1), (2500, 11), (7000, 7), (12000, 3)])


def tilt_eq(x, points):
    """Smooth EQ curve through (Hz, dB) points, applied in the frequency domain."""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    fs, gs = zip(*points)
    g = np.interp(np.log10(np.maximum(f, 20)), np.log10(fs), gs)
    return np.fft.irfft(X * 10 ** (g / 20), len(x))


def load_track(path, start, n, dur):
    """Decode an external music file (mono, SR) from `start` seconds, faded out at the end."""
    import subprocess
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(dur), '-i', path,
                          '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True, check=True).stdout
    m = np.frombuffer(raw, '<i2').astype(float) / 32768
    out = np.zeros(n); out[:min(n, len(m))] = m[:n]
    fade = int(1.5 * SR); end = int(dur * SR)
    out[end - fade:end] *= np.linspace(1, 0, fade); out[end:] = 0
    return out * 1.6


# ---------- build ----------
def build(tl):
    beat, dur = tl['beat'], tl['duration']
    n = int(dur * SR) + SR
    music = np.zeros(n); fx = np.zeros(n)
    if tl.get('musicFile'):
        music = load_track(tl['musicFile'], tl.get('musicStart', 0), n, tl['duration'])
    if tl.get('musicStyle') == 'darkEpic':
        music = dark_epic(tl, n)
    # music per scene, chords change every 4 beats on a global grid
    # (skipped when the track is added later in the TikTok app)
    for sc in ([] if tl.get('externalMusic') or tl.get('musicStyle') or tl.get('musicFile') else tl['scenes']):
        mode = sc['music']
        bar = 4 * beat
        t = sc['start']
        while t < sc['end'] - 1e-6:
            idx = int(round(t / bar))
            seg = min(bar, sc['end'] - t)
            bright = mode in ('reveal', 'outro')
            chord = (BRIGHT if bright else DARK)[idx % 4]
            notes = CHORDS[chord]
            root = hz(notes[0], 1)
            g = {'intro': 0.7, 'drive': 0.8, 'tension': 0.9, 'reveal': 1.0, 'outro': 0.9}[mode]
            add(music, t, pad(chord, seg + 0.3, bright), g)
            for b in range(int(round(seg / beat))):
                bt = t + b * beat
                if mode in ('drive', 'reveal'):
                    add(music, bt, kick(), 0.75)
                    if b % 2 == 1: add(music, bt, clap(), 0.35)
                    for e in range(2): add(music, bt + e * beat / 2, bass(root * 2, beat / 2), 0.5)
                    for e in range(4):
                        nn = notes[(b * 4 + e) % 3]
                        add(music, bt + e * beat / 4, stab(hz(nn, 4 if not bright else 5)), 0.11 if e % 2 == 0 else 0.07)
                    add(music, bt + beat / 2, hat(), 0.12)
                elif mode == 'intro':
                    add(music, bt, taiko(), 0.6 if b % 2 == 0 else 0.35)
                    for e in range(4): add(music, bt + e * beat / 4, stab(hz(notes[0], 3)), 0.05 + 0.01 * b)
                elif mode == 'tension':
                    add(music, bt, kick(), 0.6)
                    for e in range(4): add(music, bt + e * beat / 4, hat(), 0.08 + 0.04 * (e == 2))
                    add(music, bt, bass(root, beat * 0.9), 0.5)
                    add(music, bt, stab(hz(notes[0], 4), 0.2), 0.08)
                elif mode == 'outro':
                    if b % 2 == 0: add(music, bt, pluck(hz(notes[0], 5), 1.2), 0.1)
                    if b % 4 == 0: add(music, bt, bass(root, beat * 2), 0.4)
            t += seg
        # mark a new section with a crash
        if mode in ('drive', 'reveal') and sc['start'] > 0:
            prev = [x for x in tl['scenes'] if abs(x['end'] - sc['start']) < 1e-6]
            if prev and prev[0]['music'] != mode:
                add(fx, sc['start'], crash(), 0.6)
                add(fx, sc['start'], braam(hz(CHORDS[(BRIGHT if mode == 'reveal' else DARK)[0]][0], 1)), 0.7)
    # sfx
    for ev in tl['events']:
        t, k = ev['t'], ev['type']
        if k == 'cut': add(fx, max(0, t - 0.15), whoosh(0.3), 0.5)
        elif k == 'line': add(fx, max(0, t - 0.05), whoosh(0.2), 0.25)
        elif k == 'line2': add(fx, max(0, t - 0.4), riser(0.4), 0.22); add(fx, max(0, t - 0.08), whoosh(0.22), 0.35); add(fx, t, taiko(), 0.45)
        elif k == 'type':
            for c in np.arange(0, ev['dur'], 0.06): add(fx, t + c, click(), 0.35)
        elif k == 'burner': add(fx, t, burner(), 0.5)
        elif k == 'boom': add(fx, t, boom(), 0.9); add(fx, t, braam(hz('A', 1)), 0.5)
        elif k == 'hit': add(fx, t, hit(), 1.0); add(fx, t, crash(), 0.6); add(fx, t, braam(hz('C', 1)), 0.8)
        elif k == 'stamp': add(fx, t, stamp_sfx(), 0.9)
        elif k == 'ticks':
            for c in np.linspace(0, ev['dur'], ev.get('n', 10), endpoint=False): add(fx, t + c, tick(), 0.4)
        elif k == 'wind': add(fx, t, wind(ev['dur']), 0.35)
        elif k == 'riser': add(fx, t, riser(ev['dur']), 0.35)
        elif k == 'sew': add(fx, t, sew(), 0.5)
        elif k == 'fizzle': add(fx, t, fizzle(), 0.5)
        elif k == 'thud': add(fx, t, thud(), 0.8)
        elif k == 'word': add(fx, t, tick(), 0.12); add(fx, t, click(), 0.25)
        elif k == 'pop': add(fx, t, stamp_sfx(), 0.45); add(fx, t, whoosh(0.15), 0.3)
        elif k == 'crash': add(fx, t, crash(), 0.6)
        elif k == 'splash': add(fx, t, splash(), 0.9)
        elif k == 'smash': add(fx, t, smash(), 0.9)
        elif k == 'flash':
            for c in np.arange(0, ev.get('dur') or 1.5, 0.35): add(fx, t + c, flash_sfx(), 0.25)
        elif k == 'trumpet': add(fx, t, trumpet(), 0.6)
        elif k == 'thunder': add(fx, t, thunder(), 0.9)
        elif k == 'rain': add(fx, t, rain_sfx(ev['dur']), 0.5)
    # duck music under heavy hits; silence right before a reveal hit
    for ev in tl['events']:
        if ev['type'] == 'hit':
            a = int((ev['t'] - 0.45) * SR); b = int(ev['t'] * SR)
            music[a:b] *= np.linspace(1, 0.05, b - a)
            fx[a:b] *= np.linspace(1, 0.1, b - a)
    mix = music + fx
    fade = int(0.8 * SR); end = int(dur * SR)
    mix[end - fade:end] *= np.linspace(1, 0, fade); mix[end:] = 0
    mix = np.tanh(mix * 1.1)
    mix /= max(1e-9, np.abs(mix).max()) / 0.89
    return mix[:end]


def write(path, x):
    st = np.stack([x, x], 1)
    data = (st * 32767).astype('<i2').tobytes()
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data)


if __name__ == '__main__':
    tl = json.load(open(sys.argv[1]))
    write(sys.argv[2], build(tl))
