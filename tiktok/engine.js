// Silhouette-story renderer: draws one frame of a story at time t (seconds).
// render.js calls buildTimeline(story) once, then renderFrame(t) per frame.

const W = 1080, H = 1920;
const canvas = document.getElementById('c');
let ctx = canvas.getContext('2d');

const COL = {
  white: '#F4EFE6',
  yellow: '#F2C230',
  red: '#E2413B',
  ink: '#08080c',
  paper: '#E9DFC8',
  crimson: '#E0245E',
};

let TL = null;
const WORD_GAP = 0.085; // seconds between words of the first line
let TEXT_FADE = 1;      // scene-exit fade applied to all text

// ---------- helpers ----------
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const lerp = (a, b, k) => a + (b - a) * k;
const easeOut = k => 1 - Math.pow(1 - clamp(k), 3);
const easeInOut = k => { k = clamp(k); return k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2; };
const easeBack = k => { k = clamp(k); const c = 1.7; return 1 + (c + 1) * Math.pow(k - 1, 3) + c * Math.pow(k - 1, 2); };

function rng(seed) {
  return function () {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

function grad(y0, y1, stops) {
  const g = ctx.createLinearGradient(0, y0, 0, y1);
  stops.forEach(([o, c]) => g.addColorStop(o, c));
  return g;
}

// ---------- timeline ----------
function buildTimeline(story) {
  const bpm = story.bpm || 120;
  const beat = 60 / bpm;
  let t = story.offset || 0; // lead-in so the first beat of an external track lines up
  const scenes = [];
  const events = [];
  story.scenes.forEach((s, i) => {
    const start = t, dur = s.beats * beat;
    const sc = Object.assign({}, s, { i, start, end: start + dur, dur, beat });
    sc.l1t = start + (s.l1At ?? 0) * beat;
    sc.l2t = start + (s.l2At ?? 2) * beat;
    scenes.push(sc);
    events.push({ t: start, type: 'cut', i });
    if (s.label) events.push({ t: start, type: 'type', dur: Math.min(0.6, s.label.length * 0.02) });
    if (s.l1 && story.textStyle === 'cinematic') events.push({ t: sc.l1t, type: 'line' });
    else if (s.l1) s.l1.split(' ').forEach((w, k) => events.push({ t: sc.l1t + k * WORD_GAP, type: 'word' }));
    if (s.big) events.push({ t: sc.l1t, type: 'hit' });
    if (s.l2) events.push({ t: sc.l2t, type: 'line2' });
    (s.tags || []).forEach(g => events.push({ t: start + g.at * beat, type: 'pop' }));
    (s.sfx || []).forEach(f => events.push(Object.assign({}, f, { t: start + f.at * beat, dur: f.dur ? f.dur * beat : undefined })));
    t += dur;
  });
  // impacts drive camera shake, white flashes and shockwave rings
  const IMPACT = { hit: [26, 0.85, 1], boom: [18, 0.5, 1], stamp: [12, 0, 0], thud: [14, 0, 0], line2: [5, 0, 0], crash: [10, 0.6, 1] };
  if (story.textStyle === 'cinematic') { IMPACT.line2 = [0, 0, 0]; IMPACT.hit = [14, 0.5, 1]; IMPACT.boom = [10, 0.3, 1]; }
  const hits = events.filter(e => IMPACT[e.type]).map(e => ({ t: e.t, amp: IMPACT[e.type][0], flash: IMPACT[e.type][1], ring: IMPACT[e.type][2] }));
  (story.hits || []).forEach(h => hits.push({ t: h.t, amp: h.kind === 'blast' ? 12 : 4, flash: h.kind === 'flash' ? 0.35 : 0.2, ring: h.kind === 'blast' ? 1 : 0 }));
  const ramps = (story.hits || []).filter(h => h.kind === 'blast').map(h => h.t);
  scenes.forEach(sc => (sc.lines || []).forEach(ln => { if (ln.color === 'gradient') ramps.push(ln.at); }));
  TL = { story, bpm, beat, scenes, hits, ramps, duration: t + (story.tail || 1) };
  return {
    bpm, beat, duration: TL.duration, events, externalMusic: !!story.externalMusic,
    musicStyle: story.musicStyle || null, roots: story.roots || null, offset: story.offset || 0, noSfx: !!story.noSfx,
    musicFile: story.musicFile ? new URL(story.musicFile, location.href).pathname : null, musicStart: story.musicStart || 0,
    scenes: scenes.map(s => ({ start: s.start, end: s.end, music: s.music || 'groove', art: s.art })),
  };
}

// ---------- primitives ----------
function sky(stops) { ctx.fillStyle = grad(0, H, stops); ctx.fillRect(0, 0, W, H); }

function stars(seed, n, alpha, ymax, t) {
  const r = rng(seed);
  for (let i = 0; i < n; i++) {
    const x = r() * W, y = r() * ymax, s = r() * 2.4 + 0.6, ph = r() * 6.28;
    ctx.globalAlpha = alpha * (0.55 + 0.45 * Math.sin(t * 2 + ph));
    ctx.fillStyle = '#fff';
    ctx.fillRect(x, y, s, s);
  }
  ctx.globalAlpha = 1;
}

function moon(x, y, r, a = 1) {
  const g = ctx.createRadialGradient(x, y, r * 0.5, x, y, r * 4);
  g.addColorStop(0, `rgba(255,240,210,${0.25 * a})`);
  g.addColorStop(1, 'rgba(255,240,210,0)');
  ctx.fillStyle = g; ctx.fillRect(x - r * 4, y - r * 4, r * 8, r * 8);
  ctx.globalAlpha = a; ctx.fillStyle = '#F3E9D2';
  ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill(); ctx.globalAlpha = 1;
}

function hills(baseY, amp, color, seed, freq = 1) {
  const r = rng(seed);
  const p = [r() * 6, r() * 6, r() * 6];
  ctx.fillStyle = color;
  ctx.beginPath(); ctx.moveTo(0, H);
  for (let x = 0; x <= W; x += 12) {
    const y = baseY - amp * (0.5 * Math.sin(x * 0.004 * freq + p[0]) + 0.3 * Math.sin(x * 0.011 * freq + p[1]) + 0.2 * Math.sin(x * 0.023 * freq + p[2]));
    ctx.lineTo(x, y);
  }
  ctx.lineTo(W, H); ctx.closePath(); ctx.fill();
}

function ground(y, color = COL.ink) { ctx.fillStyle = color; ctx.fillRect(0, y, W, H - y); }

function trees(y, seed, n, color, hMin, hMax) {
  const r = rng(seed);
  ctx.fillStyle = color;
  for (let i = 0; i < n; i++) {
    const x = r() * W, h = lerp(hMin, hMax, r()), w = h * 0.32;
    ctx.beginPath(); ctx.moveTo(x, y - h); ctx.lineTo(x - w, y + 4); ctx.lineTo(x + w, y + 4); ctx.closePath(); ctx.fill();
  }
}

function fence(y, color = COL.ink) {
  ctx.strokeStyle = color; ctx.fillStyle = color;
  for (let x = -20; x < W + 40; x += 84) ctx.fillRect(x, y - 150, 9, 150);
  ctx.lineWidth = 2.5;
  for (let k = 0; k < 6; k++) {
    const yy = y - 20 - k * 24;
    ctx.beginPath(); ctx.moveTo(0, yy); ctx.lineTo(W, yy); ctx.stroke();
    for (let x = 10 + (k % 2) * 20; x < W; x += 42) {
      ctx.beginPath(); ctx.moveTo(x - 5, yy - 5); ctx.lineTo(x + 5, yy + 5); ctx.moveTo(x + 5, yy - 5); ctx.lineTo(x - 5, yy + 5); ctx.stroke();
    }
  }
}

function watchtower(x, y, s = 1, lit = true) {
  ctx.fillStyle = COL.ink;
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.beginPath(); ctx.moveTo(-45, 0); ctx.lineTo(-28, -330); ctx.lineTo(28, -330); ctx.lineTo(45, 0); ctx.closePath(); ctx.fill();
  ctx.fillRect(-70, -420, 140, 95);
  ctx.beginPath(); ctx.moveTo(-85, -420); ctx.lineTo(0, -460); ctx.lineTo(85, -420); ctx.closePath(); ctx.fill();
  if (lit) { ctx.fillStyle = '#F7D98A'; ctx.fillRect(-55, -400, 110, 34); }
  ctx.restore();
}

function searchlight(x, y, angle, len, spread, alpha) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(angle);
  const g = ctx.createLinearGradient(0, 0, len, 0);
  g.addColorStop(0, `rgba(255,248,220,${alpha})`);
  g.addColorStop(1, 'rgba(255,248,220,0)');
  ctx.fillStyle = g;
  ctx.beginPath(); ctx.moveTo(0, -6); ctx.lineTo(len, -spread); ctx.lineTo(len, spread); ctx.lineTo(0, 6); ctx.closePath(); ctx.fill();
  ctx.restore();
}

function person(x, y, h, o = {}) {
  ctx.fillStyle = o.color || COL.ink;
  const hr = h * 0.105;
  ctx.beginPath(); ctx.arc(x, y - h + hr, hr, 0, 7); ctx.fill();
  ctx.beginPath();
  ctx.moveTo(x - h * 0.14, y - h * 0.78); ctx.lineTo(x + h * 0.14, y - h * 0.78);
  ctx.lineTo(x + h * 0.12, y - h * 0.4); ctx.lineTo(x - h * 0.12, y - h * 0.4); ctx.closePath(); ctx.fill();
  ctx.fillRect(x - h * 0.11, y - h * 0.42, h * 0.09, h * 0.42);
  ctx.fillRect(x + h * 0.02, y - h * 0.42, h * 0.09, h * 0.42);
  if (o.cap) { ctx.fillRect(x - hr * 1.2, y - h + hr * 0.1, hr * 2.4, hr * 0.7); ctx.fillRect(x - hr * 1.5, y - h + hr * 0.75, hr * 3, hr * 0.25); }
  if (o.arm) { ctx.save(); ctx.translate(x + h * 0.12, y - h * 0.74); ctx.rotate(o.arm); ctx.fillRect(0, -h * 0.035, h * 0.36, h * 0.07); ctx.restore(); }
}

// Balloon silhouette. (cx, cy) = centre of envelope; R = radius.
function balloon(cx, cy, R, o = {}) {
  const mouthY = cy + R * 1.35, mouthW = R * 0.3;
  const path = () => {
    ctx.beginPath();
    ctx.moveTo(cx - mouthW, mouthY);
    ctx.bezierCurveTo(cx - R * 0.9, cy + R * 0.75, cx - R * 1.08, cy + R * 0.2, cx - R, cy);
    ctx.arc(cx, cy, R, Math.PI, 0);
    ctx.bezierCurveTo(cx + R * 1.08, cy + R * 0.2, cx + R * 0.9, cy + R * 0.75, cx + mouthW, mouthY);
    ctx.closePath();
  };
  // glow from the burner
  const f = o.flame || 0;
  if (f > 0) {
    const g = ctx.createRadialGradient(cx, mouthY, 10, cx, mouthY, R * 2.2);
    g.addColorStop(0, `rgba(255,170,70,${0.35 * f})`);
    g.addColorStop(1, 'rgba(255,170,70,0)');
    ctx.fillStyle = g; ctx.fillRect(cx - R * 2.4, mouthY - R * 2.4, R * 4.8, R * 4.8);
  }
  path(); ctx.fillStyle = o.color || '#2a1d27'; ctx.fill();
  // stripes
  ctx.save(); path(); ctx.clip();
  if (f > 0) {
    const g2 = ctx.createRadialGradient(cx, mouthY, 5, cx, mouthY, R * 1.9);
    g2.addColorStop(0, `rgba(255,150,60,${0.75 * f})`);
    g2.addColorStop(1, 'rgba(255,150,60,0)');
    ctx.fillStyle = g2; ctx.fillRect(cx - R * 1.2, cy - R * 1.1, R * 2.4, R * 2.6);
  }
  if (!o.color) {
    const sg = ctx.createLinearGradient(cx - R, 0, cx + R, 0);
    sg.addColorStop(0, 'rgba(0,0,0,0.45)'); sg.addColorStop(0.35, 'rgba(255,190,140,0.10)'); sg.addColorStop(1, 'rgba(0,0,0,0.55)');
    ctx.fillStyle = sg; ctx.fillRect(cx - R * 1.2, cy - R * 1.1, R * 2.4, R * 2.6);
  }
  ctx.strokeStyle = o.color ? 'rgba(255,255,255,0.08)' : 'rgba(255,200,150,0.16)'; ctx.lineWidth = Math.max(2, R * 0.02);
  for (let k = -3; k <= 3; k++) {
    ctx.beginPath(); ctx.moveTo(cx + k * mouthW / 3, mouthY);
    ctx.bezierCurveTo(cx + k * R * 0.3, cy + R * 0.6, cx + k * R * 0.36, cy - R * 0.4, cx, cy - R);
    ctx.stroke();
  }
  ctx.restore();
  if (!o.color) { path(); ctx.strokeStyle = `rgba(255,190,130,${0.18 + 0.25 * f})`; ctx.lineWidth = Math.max(2, R * 0.018); ctx.stroke(); }
  // ropes + platform
  const py = mouthY + R * 0.5;
  ctx.strokeStyle = o.color || '#15121a'; ctx.lineWidth = Math.max(1.5, R * 0.015);
  ctx.beginPath();
  ctx.moveTo(cx - mouthW, mouthY); ctx.lineTo(cx - R * 0.32, py);
  ctx.moveTo(cx + mouthW, mouthY); ctx.lineTo(cx + R * 0.32, py);
  ctx.stroke();
  // flame
  if (f > 0) {
    const fh = R * (0.25 + 0.2 * f);
    ctx.fillStyle = `rgba(255,200,90,${0.9 * Math.min(1, f + 0.2)})`;
    ctx.beginPath(); ctx.moveTo(cx - R * 0.07, mouthY + R * 0.12); ctx.quadraticCurveTo(cx, mouthY - fh, cx + R * 0.07, mouthY + R * 0.12); ctx.fill();
    ctx.fillStyle = 'rgba(120,180,255,0.8)';
    ctx.beginPath(); ctx.arc(cx, mouthY + R * 0.1, R * 0.035, 0, 7); ctx.fill();
  }
  ctx.fillStyle = o.color || '#15121a';
  ctx.fillRect(cx - R * 0.36, py, R * 0.72, R * 0.05);
  const n = o.people || 0;
  for (let k = 0; k < n; k++) {
    const px = cx - R * 0.3 + (k + 0.5) * (R * 0.6 / n);
    const ph = R * (k % 3 === 2 ? 0.17 : 0.24);
    person(px, py, ph, { color: o.color || '#15121a' });
  }
}

function house(x, y, w, h, lit = true) {
  ctx.fillStyle = COL.ink;
  ctx.fillRect(x - w / 2, y - h, w, h);
  ctx.beginPath(); ctx.moveTo(x - w / 2 - 20, y - h); ctx.lineTo(x, y - h - h * 0.6); ctx.lineTo(x + w / 2 + 20, y - h); ctx.closePath(); ctx.fill();
  ctx.fillRect(x + w * 0.22, y - h - h * 0.55, w * 0.1, h * 0.35);
  if (lit) {
    const wins = [[-0.3, 0.55], [0.12, 0.55]];
    wins.forEach(([dx, dy]) => {
      const wx = x + dx * w, wy = y - h * dy - 40, ww = w * 0.2, wh = 90;
      const g = ctx.createRadialGradient(wx + ww / 2, wy + wh / 2, 10, wx + ww / 2, wy + wh / 2, 200);
      g.addColorStop(0, 'rgba(255,200,110,0.35)'); g.addColorStop(1, 'rgba(255,200,110,0)');
      ctx.fillStyle = g; ctx.fillRect(wx - 200, wy - 200, ww + 400, wh + 400);
      ctx.fillStyle = '#F6C978'; ctx.fillRect(wx, wy, ww, wh);
    });
  }
}

function paper(x, y, w, h, rot, draw) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  ctx.fillStyle = 'rgba(0,0,0,0.45)'; ctx.fillRect(-w / 2 + 14, -h / 2 + 18, w, h);
  ctx.fillStyle = COL.paper; ctx.fillRect(-w / 2, -h / 2, w, h);
  ctx.strokeStyle = 'rgba(120,90,50,0.25)'; ctx.lineWidth = 2; ctx.strokeRect(-w / 2 + 12, -h / 2 + 12, w - 24, h - 24);
  ctx.fillStyle = '#2b2620';
  draw(w, h);
  ctx.restore();
}

function stamp(text, x, y, rot, color, dt, size = 64) {
  if (dt < 0) return;
  const k = clamp(dt / 0.12);
  const s = lerp(2.2, 1, easeOut(k));
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.globalAlpha = k * 0.9;
  ctx.font = `${size}px 'Black Ops One'`;
  const tw = ctx.measureText(text).width;
  ctx.strokeStyle = color; ctx.lineWidth = 6;
  ctx.strokeRect(-tw / 2 - 24, -size * 0.8, tw + 48, size * 1.35);
  ctx.lineWidth = 2; ctx.strokeRect(-tw / 2 - 14, -size * 0.68, tw + 28, size * 1.11);
  ctx.fillStyle = color; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText(text, 0, -size * 0.12);
  ctx.restore(); ctx.globalAlpha = 1;
}

function burst(cx, cy, color, rot, alpha = 0.5) {
  ctx.save(); ctx.translate(cx, cy); ctx.rotate(rot); ctx.fillStyle = color; ctx.globalAlpha = alpha;
  for (let k = 0; k < 24; k++) {
    ctx.rotate(Math.PI * 2 / 24);
    if (k % 2) continue;
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(2400, -150); ctx.lineTo(2400, 150); ctx.closePath(); ctx.fill();
  }
  ctx.restore(); ctx.globalAlpha = 1;
}

function ring(cx, cy, r, color, w = 6, a = 1) {
  ctx.globalAlpha = a; ctx.strokeStyle = color; ctx.lineWidth = w;
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.stroke(); ctx.globalAlpha = 1;
}

function clouds(seed, y0, y1, n, alpha, t, color = '#cfd6e6') {
  const r = rng(seed);
  for (let i = 0; i < n; i++) {
    const x = ((r() * (W + 600) + t * (20 + r() * 30)) % (W + 600)) - 300;
    const y = lerp(y0, y1, r()), w = 160 + r() * 220;
    ctx.globalAlpha = alpha * (0.6 + r() * 0.4); ctx.fillStyle = color;
    ctx.beginPath(); ctx.ellipse(x, y, w, w * 0.22, 0, 0, 7); ctx.fill();
  }
  ctx.globalAlpha = 1;
}

function bee(x, y, s, t) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  ctx.rotate(Math.sin(t * 3) * 0.15);
  ctx.fillStyle = 'rgba(230,240,255,0.75)';
  const flap = 0.6 + 0.4 * Math.sin(t * 60);
  ctx.beginPath(); ctx.ellipse(-4, -10, 7, 11 * flap, -0.5, 0, 7); ctx.fill();
  ctx.beginPath(); ctx.ellipse(5, -10, 7, 11 * flap, 0.5, 0, 7); ctx.fill();
  ctx.fillStyle = '#F2C230'; ctx.beginPath(); ctx.ellipse(0, 0, 14, 9, 0, 0, 7); ctx.fill();
  ctx.fillStyle = '#111';
  ctx.fillRect(-4, -9, 4, 18); ctx.fillRect(4, -8, 4, 16);
  ctx.beginPath(); ctx.arc(-13, 0, 5, 0, 7); ctx.fill();
  ctx.restore();
}

// ---------- text ----------
function wrap(text, font, maxW) {
  ctx.font = font;
  const words = text.split(' ');
  const lines = []; let cur = '';
  for (const w of words) {
    const test = cur ? cur + ' ' + w : w;
    if (ctx.measureText(test).width > maxW && cur) { lines.push(cur); cur = w; } else cur = test;
  }
  if (cur) lines.push(cur);
  return lines;
}

function textBlock(text, x, y, size, color, dt, o = {}) {
  text = text.replace(/\*/g, '');
  const font = `${size}px ${o.family || 'Anton'}`;
  const lines = wrap(text, font, o.maxW || 900);
  const lh = size * 1.12;
  if (dt >= 0) {
    // slam: drops in big and lands hard; default: quick springy pop
    const s = o.slam ? lerp(1.6, 1, easeOut(dt / 0.12)) : lerp(0.82, 1, easeBack(dt / 0.16));
    ctx.save();
    ctx.globalAlpha = clamp(dt / (o.slam ? 0.05 : 0.08)) * TEXT_FADE;
    ctx.font = font; ctx.textAlign = 'center'; ctx.textBaseline = 'top';
    ctx.shadowColor = 'rgba(0,0,0,0.75)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 4;
    lines.forEach((l, i) => {
      const ly = y + i * lh;
      ctx.save(); ctx.translate(x, ly + lh / 2); ctx.scale(s, s);
      if (o.slam && dt < 0.3) {
        const ca = 14 * (1 - dt / 0.3);
        ctx.globalCompositeOperation = 'lighter';
        ctx.fillStyle = 'rgba(255,40,60,0.6)'; ctx.fillText(l, ca, -lh / 2);
        ctx.fillStyle = 'rgba(40,200,255,0.6)'; ctx.fillText(l, -ca, -lh / 2);
        ctx.globalCompositeOperation = 'source-over';
      }
      ctx.fillStyle = color; ctx.fillText(l, 0, -lh / 2);
      ctx.restore();
    });
    ctx.restore();
  }
  return y + lines.length * lh;
}

// Reveals text word by word; each word pops on its own. Layout stays fixed.
// Words wrapped in *asterisks* get a yellow marker that wipes in behind them.
function wordBlock(text, x, y, size, color, dt) {
  const font = `${size}px Anton`;
  const raw = text.split(' ');
  const marked = raw.map(w => w.includes('*'));
  const lines = wrap(raw.map(w => w.replace(/\*/g, '')).join(' '), font, 900);
  const lh = size * 1.12;
  ctx.save();
  ctx.font = font; ctx.textAlign = 'left'; ctx.textBaseline = 'top';
  ctx.shadowColor = 'rgba(0,0,0,0.75)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 4;
  const space = ctx.measureText(' ').width;
  let idx = 0;
  lines.forEach((l, i) => {
    let wx = x - ctx.measureText(l).width / 2;
    for (const w of l.split(' ')) {
      const ww = ctx.measureText(w).width;
      const d = dt - idx * WORD_GAP;
      if (d >= 0) {
        const s = lerp(1.35, 1, easeOut(d / 0.1));
        ctx.save(); ctx.globalAlpha = clamp(d / 0.04) * TEXT_FADE;
        ctx.translate(wx + ww / 2, y + i * lh + lh / 2); ctx.scale(s, s);
        if (marked[idx]) {
          const k = easeOut(d / 0.14);
          ctx.save(); ctx.shadowColor = 'transparent';
          ctx.fillStyle = COL.yellow; ctx.fillRect(-ww / 2 - 10, -lh / 2 + size * 0.02, (ww + 20) * k, size * 1.08);
          ctx.restore();
          ctx.shadowColor = 'transparent';
          ctx.fillStyle = '#111'; ctx.fillText(w, -ww / 2, -lh / 2);
        } else {
          ctx.fillStyle = color; ctx.fillText(w, -ww / 2, -lh / 2);
        }
        ctx.restore();
      }
      wx += ww + space; idx++;
    }
  });
  ctx.restore();
  return y + lines.length * lh;
}

// Small coloured label box that pops in (like "AGE: 14" in the originals).
function tag(g, dt) {
  if (dt < 0) return;
  const s = lerp(0, 1, easeBack(dt / 0.18));
  ctx.save(); ctx.translate(g.x, g.y); ctx.rotate(g.rot || 0); ctx.scale(s, s);
  ctx.font = `${g.size || 44}px Anton`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  const tw = ctx.measureText(g.text).width;
  ctx.fillStyle = 'rgba(0,0,0,0.4)'; ctx.fillRect(-tw / 2 - 18 + 6, -34 + 8, tw + 36, 68);
  ctx.fillStyle = COL[g.color || 'red'] || g.color; ctx.fillRect(-tw / 2 - 18, -34, tw + 36, 68);
  ctx.fillStyle = g.ink || COL.white; ctx.fillText(g.text, 0, 2);
  ctx.restore();
}

function label(text, dt) {
  if (!text || dt < 0) return;
  const n = Math.floor(dt / 0.03);
  ctx.save();
  ctx.font = "34px 'Oswald'"; ctx.textAlign = 'center'; ctx.textBaseline = 'top';
  ctx.fillStyle = 'rgba(244,239,230,0.85)';
  if (ctx.letterSpacing !== undefined) ctx.letterSpacing = '6px';
  ctx.shadowColor = 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 10;
  ctx.fillText(text.slice(0, n), W / 2, 300);
  ctx.restore();
}

// Cinematic text (style of the reference): serif caps, white + crimson, centred lower,
// small label above. Lines blur in sharp-fast and blur out at the scene end.
function cineLine(text, y, size, fill, dt, exitK, side = 0) {
  if (dt < 0) return y;
  const kin = TL.story.v8;
  text = text.replace(/\*/g, '');
  const font = `${size}px Cinzel`;
  const lines = wrap(text, font, 960);
  const lh = size * 1.18;
  const b = 10 * (1 - clamp(dt / 0.12)) + 14 * exitK;
  ctx.save();
  ctx.font = font; ctx.textAlign = 'center'; ctx.textBaseline = 'top';
  ctx.globalAlpha = clamp(dt / 0.08) * (1 - exitK);
  if (b > 0.4) ctx.filter = `blur(${b.toFixed(1)}px)`;
  ctx.shadowColor = 'rgba(0,0,0,0.85)'; ctx.shadowBlur = 22; ctx.shadowOffsetY = 3;
  let ox = 0;
  if (kin) {
    // fly in from alternating sides with overshoot; big/gradient words track in
    ox = (side % 2 ? 1 : -1) * 160 * (1 - easeBack(dt / 0.22));
    if (fill === 'gradient' && ctx.letterSpacing !== undefined) ctx.letterSpacing = `${(26 * (1 - easeOut(dt / 0.35))).toFixed(1)}px`;
  }
  lines.forEach((l, i) => {
    if (fill === 'gradient') {
      const g = ctx.createLinearGradient(0, y + i * lh, 0, y + i * lh + size);
      g.addColorStop(0, '#ffffff'); g.addColorStop(0.55, '#f6c6d2'); g.addColorStop(1, COL.crimson);
      ctx.fillStyle = g;
    } else ctx.fillStyle = fill;
    ctx.fillText(l, W / 2 + ox, y + i * lh);
  });
  ctx.restore();
  return y + lines.length * lh;
}

function cineText(sc, t) {
  const exitK = sc.i < TL.scenes.length - 1 ? clamp(1 - (sc.end - t) / 0.14) : 0;
  let y = sc.textY || 1000;
  if (sc.label && t >= sc.start) {
    ctx.save(); ctx.font = "30px 'Oswald'"; ctx.textAlign = 'center'; ctx.textBaseline = 'bottom';
    if (ctx.letterSpacing !== undefined) ctx.letterSpacing = '5px';
    ctx.globalAlpha = 0.85 * clamp((t - sc.start) / 0.1) * (1 - exitK);
    ctx.shadowColor = 'rgba(0,0,0,0.8)'; ctx.shadowBlur = 10;
    ctx.fillStyle = COL.white; ctx.fillText(sc.label, W / 2, y - 18);
    ctx.restore();
  }
  if (sc.counter) {
    const c = sc.counter, k = clamp((t - sc.start) / (c.dur * sc.beat));
    const v = Math.round(c.to * easeOut(k)).toLocaleString('de-DE');
    y = cineLine(v, y - 180, 170, 'gradient', t - sc.start, exitK);
    y = cineLine(c.unit, y - 10, 40, COL.crimson, t - sc.start, exitK) + 20;
  }
  if (sc.lines) {
    // each line appears on its own beat (absolute time), stacked like the reference
    for (const ln of sc.lines) {
      const fill = ln.color === 'crimson' ? COL.crimson : ln.color === 'gradient' ? 'gradient' : COL.white;
      const yy = cineLine(ln.text, y, ln.size || 60, fill, t - ln.at, exitK, sc.lines.indexOf(ln) + sc.i);
      y = t >= ln.at || ln.reserve ? yy : y + (ln.size || 60) * 1.18;
    }
    TEXT_FADE = 1 - exitK;
    (sc.tags || []).forEach(g => tag(g, t - (g.t !== undefined ? g.t : sc.start + g.at * sc.beat)));
    return;
  }
  if (sc.big) y = cineLine(sc.big, y - 40, sc.bigSize ? sc.bigSize * 0.62 : 130, 'gradient', t - sc.l1t, exitK) + 10;
  if (sc.l1) y = cineLine(sc.l1, y, sc.l1Size || 60, COL.white, t - sc.l1t, exitK);
  if (sc.l2) cineLine(sc.l2, y, sc.l2Size || 60, COL.crimson, t - sc.l2t, exitK);
  TEXT_FADE = 1 - exitK;
  (sc.tags || []).forEach(g => tag(g, t - (sc.start + g.at * sc.beat)));
}

// Explosion in the reference look: stacked orange circles turning into dark smoke, crimson ring.
function blast(x, y, dt, seed, s = 1) {
  if (dt < 0 || dt > 2.2) return;
  const r = rng(seed);
  const smoke = clamp((dt - 0.2) / 0.7);
  // dark smoke behind, fireballs with hot cores in front
  for (let pass = 0; pass < 2; pass++) {
    for (let i = 0; i < 11; i++) {
      const ox = (r() - 0.5) * 260 * s, oy = (r() - 0.5) * 180 * s, rad = (55 + r() * 95) * s;
      const grow = easeOut(dt / 0.35), rise = dt * (pass ? 50 : 90) * s;
      const cx = x + ox * grow * (pass ? 1 : 1.25), cy = y + oy * grow - rise;
      const R = rad * (0.4 + 0.8 * grow) * (pass ? 1 : 1.2);
      ctx.globalAlpha = clamp(1 - (dt - 1.3) / 0.9) * (pass ? 1 - smoke * 0.85 : 0.7 * smoke + 0.1);
      if (pass === 0) ctx.fillStyle = '#231c1a';
      else {
        const g = ctx.createRadialGradient(cx - R * 0.2, cy - R * 0.25, R * 0.05, cx, cy, R);
        g.addColorStop(0, `rgba(255,246,214,1)`); g.addColorStop(0.35, '#ffb24a'); g.addColorStop(0.8, '#e0582a'); g.addColorStop(1, 'rgba(160,40,20,0.9)');
        ctx.fillStyle = g;
      }
      ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.fill();
    }
  }
  ctx.globalAlpha = 1;
  particles(x, y, dt, seed + 7, { color: '#ffd27a', n: 34, v0: 500, v1: 1400, s0: 3, s1: 7, life: 0.9, a0: -Math.PI, a1: Math.PI, gravity: 900 });
  if (dt < 0.5) ring(x, y, 80 * s + dt * 900 * s, COL.crimson, 10 * (1 - dt / 0.5), 0.9 * (1 - dt / 0.5));
}

// Beat layer: every beat of the track produces a visible hit (zoom punch, light pulse,
// motion surge); bar downbeats hit harder. Strength follows the track's onset envelope.
function beatState(t) {
  const st = TL.story;
  if (!st.beatFx) return { on: false };
  const off = st.offset || 0, b = (t - off) / TL.beat;
  if (b < 0) return { on: false };
  const idx = Math.floor(b), frac = b - idx, dt = frac * TL.beat;
  const down = ((idx - (st.barPhase || 0)) % 4 + 4) % 4 === 0;
  const amp = 0.45 + 0.55 * clamp(onsetAt(off + idx * TL.beat + 0.02) * 1.2);
  // time remap: inside each beat the clock runs fast right after the hit, then slows
  const tw = off + (idx + 0.45 * frac + 0.55 * (1 - Math.pow(1 - frac, 3))) * TL.beat;
  return { on: true, idx, dt, down, amp, k: Math.exp(-dt * 11), tw: speedRamp(tw) };
}

function beatPulse(BT) {
  const k = BT.k * BT.amp;
  // exposure pop
  ctx.fillStyle = `rgba(255,248,240,${(BT.down ? 0.16 : 0.08) * k})`; ctx.fillRect(0, 0, W, H);
  // crimson edge glow
  const g = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H * 0.72);
  g.addColorStop(0, 'rgba(224,36,94,0)'); g.addColorStop(1, `rgba(224,36,94,${(BT.down ? 0.45 : 0.25) * k})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // RGB split on bar downbeats
  if (BT.down && BT.dt < 0.12) {
    const o = 10 * (1 - BT.dt / 0.12) * BT.amp;
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = 0.22;
    ctx.drawImage(canvas, o, 0); ctx.drawImage(canvas, -o, 0); ctx.restore();
  }
}

// Music envelope (from the analysed track), sampled at story.react.fps.
function onsetAt(t) {
  const r = TL.story.react; if (!r) return 0;
  const i = Math.floor(t * r.fps); return r.onset[i] || 0;
}

// Blasts at reference hit times inside the scene, drawn at the scene's focus point.
function sceneBlasts(sc, t) {
  if (!sc.blastAt) return;
  sc.blastAt.forEach((bt, k) => blast(sc.focus ? sc.focus[0] : 540, sc.focus ? sc.focus[1] : 1200, t - bt, 500 + sc.i * 10 + k, sc.blastScale || 1));
}

function v8Post(t, BT) {
  lightLeaks(t, BT.on ? BT.k * BT.amp : 0);
  // impact frame: 2 inverted high-contrast frames on every blast
  for (const h of TL.hits) {
    if (h.ring && t - h.t >= 0 && t - h.t < 2 / 30) {
      ctx.save(); ctx.filter = 'grayscale(1) invert(1) contrast(2.2)'; ctx.drawImage(canvas, 0, 0); ctx.restore();
      break;
    }
  }
  // letterbox bars slam in on blasts and ease out
  let lb = 0;
  for (const h of TL.hits) { const d = t - h.t; if (h.ring && d >= 0 && d < 1.8) lb = Math.max(lb, d < 0.08 ? d / 0.08 : 1 - easeInOut((d - 0.08) / 1.7)); }
  if (lb > 0) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, W, 150 * lb); ctx.fillRect(0, H - 150 * lb, W, 150 * lb); }
}

// Speed ramp: the 0.45 s before every big hit run in slow motion, then snap back.
function speedRamp(tw) {
  for (const h of TL.ramps || []) {
    const a = h - 0.45;
    if (tw >= a && tw < h) return a + (tw - a) * 0.3;
  }
  return tw;
}

// Moving light leaks, brighter on the beat.
function lightLeaks(t, k) {
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  [[0.3, 0.7, '255,150,90'], [0.8, 0.3, '224,36,94']].forEach(([fx, fy, c], i) => {
    const x = W * (fx + 0.25 * Math.sin(t * 0.4 + i * 2)), y = H * (fy + 0.15 * Math.cos(t * 0.3 + i));
    const g = ctx.createRadialGradient(x, y, 10, x, y, 700);
    g.addColorStop(0, `rgba(${c},${0.12 + 0.12 * k})`); g.addColorStop(1, `rgba(${c},0)`);
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  });
  ctx.restore();
}

function sceneText(sc, t) {
  const ex = sc.i < TL.scenes.length - 1 ? clamp(1 - (sc.end - t) / 0.18) : 0;
  TEXT_FADE = 1 - ex;
  if (ex > 0) { ctx.globalAlpha = TEXT_FADE; ctx.translate(0, -90 * easeOut(ex)); }
  label(sc.label, t - sc.start);
  let y = sc.textY || 400;
  if (sc.big) {
    y = textBlock(sc.big, W / 2, y - 20, sc.bigSize || 210, COL.white, t - sc.l1t, { slam: true }) + 10;
  }
  if (sc.counter) {
    const c = sc.counter, k = clamp((t - sc.start) / (c.dur * sc.beat));
    const v = Math.round(c.to * easeOut(k));
    const pop = t - (sc.start + c.dur * sc.beat);
    const s = pop > 0 ? 1 + 0.18 * Math.exp(-pop * 10) : 1;
    ctx.save(); ctx.translate(W / 2, y + 110); ctx.scale(s, s);
    ctx.font = "230px 'Anton'"; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.shadowColor = 'rgba(0,0,0,0.7)'; ctx.shadowBlur = 20;
    ctx.fillStyle = COL.white; ctx.fillText(v.toLocaleString('de-DE'), 0, 0);
    ctx.restore();
    ctx.font = "44px 'Oswald'"; ctx.textAlign = 'center'; ctx.fillStyle = COL.red;
    ctx.shadowColor = 'rgba(0,0,0,0.9)'; ctx.shadowBlur = 12;
    ctx.fillText(c.unit, W / 2, y + 250); ctx.shadowBlur = 0;
    y += 300;
  }
  if (sc.l1) y = wordBlock(sc.l1, W / 2, y, sc.l1Size || 78, COL.white, t - sc.l1t) + 14;
  if (sc.l2) textBlock(sc.l2, W / 2, y, sc.l2Size || 78, COL[sc.l2Color || 'yellow'], t - sc.l2t, { slam: true });
  (sc.tags || []).forEach(g => tag(g, t - (sc.start + g.at * sc.beat)));
}

// ---------- scene art ----------
function nightSky(t, seed = 1) {
  sky([[0, '#060918'], [0.45, '#141b3d'], [0.75, '#3a2c4c'], [1, '#5b3a45']]);
  stars(seed, 140, 0.8, 1200, t);
}

const ART = {
  hook(sc, t, lt, p) {
    nightSky(t, 3);
    moon(820, 760, 46);
    hills(1420, 90, '#1a1d33', 11, 0.8);
    const a = Math.sin(lt * 2.2) * 0.45 - 2.2;
    searchlight(860, 1080, a, 1400, 130, 0.22);
    searchlight(860, 1080, a - 0.7 + Math.sin(lt * 1.7) * 0.3, 1400, 110, 0.16);
    const by = lerp(1300, 900, easeOut(p));
    const fl = lt > 1.5 ? 0.7 + 0.3 * Math.sin(lt * 23) : 0.15;
    balloon(380, by, 150, { flame: fl, people: 6 });
    watchtower(860, 1500, 1);
    fence(1520);
    ground(1515);
  },

  border(sc, t, lt, p) {
    nightSky(t, 5);
    hills(1400, 80, '#1a1d33', 21);
    const a1 = -2.4 + Math.sin(lt * 2.6) * 0.55, a2 = -0.8 + Math.sin(lt * 2.2 + 1) * 0.55;
    searchlight(250, 1080, a2, 1300, 120, 0.2);
    searchlight(830, 1080, a1, 1300, 120, 0.2);
    watchtower(250, 1500, 1); watchtower(830, 1500, 1);
    fence(1520);
    ground(1515);
    // warning sign
    ctx.fillStyle = COL.ink; ctx.fillRect(536, 1560, 8, 120);
    ctx.fillStyle = '#d9cfb8'; ctx.fillRect(470, 1540, 140, 70);
    ctx.fillStyle = COL.red; ctx.font = "40px 'Anton'"; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('HALT!', 540, 1576);
  },

  house(sc, t, lt, p) {
    nightSky(t, 7);
    moon(220, 820, 40);
    hills(1430, 120, '#1a1d33', 31);
    trees(1500, 41, 9, '#0e1020', 120, 260);
    house(560, 1510, 440, 300);
    ground(1505);
    // sketch of the idea
    const k = easeInOut((lt - sc.beat * 2) / (sc.beat * 2.5));
    if (k > 0) {
      ctx.save();
      ctx.strokeStyle = COL.yellow; ctx.lineWidth = 6; ctx.setLineDash([22, 14]);
      ctx.globalAlpha = 0.9;
      const R = 120, cx = 560, cy = 920;
      ctx.beginPath(); ctx.arc(cx, cy, R, Math.PI, Math.PI + Math.PI * Math.min(1, k * 1.6)); ctx.stroke();
      if (k > 0.5) {
        const kk = (k - 0.5) * 2;
        ctx.beginPath(); ctx.moveTo(cx - R, cy);
        ctx.bezierCurveTo(cx - R * 1.05, cy + R * 0.6 * kk, cx - R * 0.6, cy + R * 1.1 * kk, cx - R * 0.3, cy + R * 1.35 * kk); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(cx + R, cy);
        ctx.bezierCurveTo(cx + R * 1.05, cy + R * 0.6 * kk, cx + R * 0.6, cy + R * 1.1 * kk, cx + R * 0.3, cy + R * 1.35 * kk); ctx.stroke();
      }
      ctx.restore();
    }
  },

  sewing(sc, t, lt, p) {
    sky([[0, '#1c120d'], [1, '#3a2618']]);
    // lamp cone
    const g = ctx.createRadialGradient(560, 1150, 40, 560, 1150, 700);
    g.addColorStop(0, 'rgba(255,200,120,0.35)'); g.addColorStop(1, 'rgba(255,200,120,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 500, W, 1400);
    // fabric stripes running across table
    const colors = ['#b8433a', '#d9a441', '#3f6f8f', '#e8e0cc', '#6b8f4e'];
    const off = (lt * 160) % 120;
    ctx.save(); ctx.beginPath(); ctx.rect(0, 1340, W, 120); ctx.clip();
    for (let x = -120; x < W + 120; x += 120) {
      ctx.fillStyle = colors[Math.abs(Math.floor((x - off) / 120)) % colors.length];
      ctx.fillRect(x + off, 1340, 120, 120);
    }
    ctx.restore();
    ctx.fillStyle = '#120b07'; ctx.fillRect(0, 1460, W, 460);
    // sewing machine
    ctx.fillStyle = COL.ink;
    ctx.fillRect(600, 1300, 330, 46);
    ctx.fillRect(860, 1080, 70, 230);
    ctx.beginPath(); ctx.moveTo(620, 1080); ctx.lineTo(930, 1080); ctx.lineTo(930, 1160); ctx.lineTo(680, 1160); ctx.quadraticCurveTo(620, 1160, 620, 1120); ctx.closePath(); ctx.fill();
    const ny = 1200 + Math.abs(Math.sin(lt * 18)) * 70;
    ctx.fillRect(648, 1160, 18, ny - 1160);
    ctx.beginPath(); ctx.arc(900, 1120, 50, 0, 7); ctx.fill();
    // receipt
    paper(290, 1050, 330, 430, -0.09, (w, h) => {
      ctx.font = "28px 'Special Elite'"; ctx.textAlign = 'center';
      ctx.fillText('KAUFHAUS', 0, -h / 2 + 60);
      ctx.fillText('LEIPZIG', 0, -h / 2 + 94);
      ctx.textAlign = 'left'; ctx.font = "24px 'Special Elite'";
      for (let i = 0; i < 4; i++) ctx.fillText('Taft, Meterware ......', -w / 2 + 30, -h / 2 + 160 + i * 42);
      ctx.fillText('SUMME ...............', -w / 2 + 30, -h / 2 + 350);
    });
  },

  stasi(sc, t, lt, p) {
    sky([[0, '#16171a'], [1, '#2a2b2e']]);
    const g = ctx.createRadialGradient(540, 1200, 60, 540, 1200, 800);
    g.addColorStop(0, 'rgba(255,235,190,0.22)'); g.addColorStop(1, 'rgba(255,235,190,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 400, W, 1520);
    ctx.fillStyle = '#3b2a1e'; ctx.fillRect(0, 1650, W, 270);
    // folder
    ctx.save(); ctx.translate(540, 1240); ctx.rotate(0.04);
    ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(-330, -380, 680, 800);
    ctx.fillStyle = '#c9b48a'; ctx.fillRect(-340, -400, 680, 800);
    ctx.fillRect(-340, -440, 240, 50);
    ctx.fillStyle = '#2b2620'; ctx.font = "34px 'Special Elite'"; ctx.textAlign = 'left';
    ctx.fillText('AKTE', -300, -320);
    ctx.font = "28px 'Special Elite'";
    ctx.fillText('Vorgang: Ballon', -300, -250);
    ctx.fillText('Fundort: Grenzgebiet', -300, -205);
    ctx.fillText('Datum:   Juli 1979', -300, -160);
    ctx.fillText('Status:  Täter flüchtig', -300, -115);
    ctx.strokeStyle = 'rgba(40,35,30,0.35)'; ctx.lineWidth = 2;
    for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.moveTo(-300, -40 + i * 50); ctx.lineTo(300, -40 + i * 50); ctx.stroke(); }
    ctx.restore();
    stamp('FAHNDUNG', 560, 1420, -0.14, COL.red, lt - sc.beat * 3.5, 76);
  },

  size(sc, t, lt, p) {
    sky([[0, '#0b0e1c'], [1, '#1d2236']]);
    burst(540, 1250, '#283152', lt * 0.15, 0.55);
    ring(540, 1250, 520, COL.red, 6, 0.6);
    const k = easeOut(lt / (sc.counter.dur * sc.beat));
    const R = lerp(60, 230, k);
    const groundY = 1680;
    balloon(560, groundY - R * 1.85 - 30, R, { flame: 0.5 + 0.2 * Math.sin(lt * 20), color: '#0d0b10' });
    // size comparison: house + person
    house(220, groundY, 140, 100, false);
    person(330, groundY, 70);
    ground(groundY);
    // scale bar
    ctx.fillStyle = COL.yellow;
    const top = groundY - (R * 1.85 + 30 + R);
    ctx.fillRect(900, top, 8, groundY - top);
    for (let y = groundY; y > top; y -= 40) ctx.fillRect(900, y, 26, 4);
  },

  launch(sc, t, lt, p) {
    nightSky(t, 9);
    hills(1380, 70, '#181b30', 51);
    trees(1520, 61, 14, '#0c0e1a', 160, 320);
    const lift = easeInOut((lt - sc.beat * 1) / (sc.beat * 4));
    const by = lerp(1150, 990, lift);
    const fl = 0.75 + 0.25 * Math.sin(lt * 25);
    balloon(540, by, 190, { flame: fl, people: 8 });
    ground(1515);
  },

  altitude(sc, t, lt, p) {
    sky([[0, '#03040c'], [0.6, '#0d1430'], [1, '#26305a']]);
    stars(13, 220, 0.9, 1500, t);
    clouds(5, 1450, 1800, 12, 0.18, t, '#8f9bc0');
    const bob = Math.sin(lt * 1.5) * 12;
    balloon(520, 1020 + bob, 170, { flame: 0.4 + 0.2 * Math.sin(lt * 18), people: 8 });
    // altimeter
    const v = Math.round(2600 * easeOut(lt / (sc.beat * 3)));
    ctx.save(); ctx.translate(880, 1640);
    ctx.fillStyle = 'rgba(10,12,22,0.85)'; ctx.beginPath(); ctx.arc(0, 0, 110, 0, 7); ctx.fill();
    ring(0, 0, 110, COL.white, 4, 0.8);
    ctx.rotate(-2.4 + 4.8 * (v / 3000));
    ctx.fillStyle = COL.red; ctx.fillRect(-4, -95, 8, 100);
    ctx.restore();
    ctx.font = "34px 'Oswald'"; ctx.fillStyle = COL.white; ctx.textAlign = 'center';
    ctx.fillText(`${v.toLocaleString('de-DE')} m`, 880, 1690);
  },

  gasout(sc, t, lt, p) {
    sky([[0, '#05060d'], [1, '#1a1f3a']]);
    stars(17, 160, 0.7, 1500, t);
    const k = easeInOut(lt / sc.dur);
    const fl = lt < sc.beat * 2 ? 0.5 + 0.3 * Math.sin(lt * 30) : Math.max(0, 0.3 - (lt - sc.beat * 2) * 0.4) * (Math.sin(lt * 50) > 0 ? 1 : 0.3);
    balloon(540, lerp(980, 1180, k), 170, { flame: fl, people: 8 });
    hills(1650, 60, '#0b0d18', 71);
    // timer
    const m = Math.round(28 * easeOut(lt / (sc.beat * 2)));
    ctx.font = "90px 'Black Ops One'"; ctx.textAlign = 'center'; ctx.fillStyle = m >= 28 ? COL.red : COL.white;
    ctx.fillText(`${String(m).padStart(2, '0')}:00`, 540, 1780);
  },

  field(sc, t, lt, p) {
    sky([[0, '#0a0d1e'], [0.7, '#2a3050'], [1, '#4b4a5e']]);
    stars(19, 90, 0.5, 900, t);
    hills(1400, 60, '#171a2c', 81);
    trees(1430, 91, 10, '#0f1220', 120, 240);
    ground(1440, '#0c0e16');
    // collapsed balloon
    ctx.fillStyle = '#15121a';
    ctx.beginPath(); ctx.moveTo(380, 1450);
    ctx.bezierCurveTo(450, 1330, 700, 1310, 960, 1450); ctx.closePath(); ctx.fill();
    ctx.fillRect(250, 1430, 120, 20);
    for (let k = 0; k < 4; k++) person(110 + k * 80, 1470, k > 1 ? 110 : 160);
    // flowers + hidden bee
    const r = rng(101);
    for (let i = 0; i < 40; i++) {
      const x = r() * W, y = 1700 + r() * 200;
      ctx.strokeStyle = '#1c2a1c'; ctx.lineWidth = 4;
      ctx.beginPath(); ctx.moveTo(x, y + 60); ctx.lineTo(x, y); ctx.stroke();
      ctx.fillStyle = ['#3a3550', '#4a4060', '#2f3d55'][i % 3];
      ctx.beginPath(); ctx.arc(x, y, 12, 0, 7); ctx.fill();
    }
    if (TL.story.beeScene === sc.art) bee(150 + lt * 40, 1690 + Math.sin(lt * 4) * 14, 1.1, lt);
  },

  police(sc, t, lt, p) {
    sky([[0, '#0a0d1e'], [1, '#2c3150']]);
    hills(1400, 50, '#171a2c', 111);
    ground(1500, '#0c0e16');
    // police car with blue light
    const on = Math.floor(lt * 4) % 2 === 0;
    const cx = 780, cy = 1500;
    const g = ctx.createRadialGradient(cx, cy - 150, 10, cx, cy - 150, 520);
    g.addColorStop(0, `rgba(70,130,255,${on ? 0.4 : 0.12})`); g.addColorStop(1, 'rgba(70,130,255,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 600, W, 1300);
    ctx.fillStyle = COL.ink;
    ctx.beginPath(); ctx.moveTo(cx - 210, cy - 30); ctx.lineTo(cx - 200, cy - 95); ctx.lineTo(cx - 110, cy - 105);
    ctx.lineTo(cx - 60, cy - 170); ctx.lineTo(cx + 90, cy - 170); ctx.lineTo(cx + 150, cy - 105); ctx.lineTo(cx + 220, cy - 95); ctx.lineTo(cx + 225, cy - 30); ctx.closePath(); ctx.fill();
    ctx.beginPath(); ctx.arc(cx - 120, cy - 25, 38, 0, 7); ctx.arc(cx + 130, cy - 25, 38, 0, 7); ctx.fill();
    ctx.fillStyle = on ? '#4c8dff' : '#1d3a7a'; ctx.fillRect(cx - 10, cy - 196, 40, 26);
    // two officers, two refugees
    person(560, 1505, 330, { cap: true });
    person(670, 1505, 340, { cap: true });
    person(170, 1505, 320, { arm: -0.25 });
    person(300, 1505, 300);
  },

  map(sc, t, lt, p) {
    sky([[0, '#1b1a17'], [1, '#2a2722']]);
    // map paper
    ctx.save(); ctx.translate(540, 1300); ctx.rotate(-0.025);
    ctx.fillStyle = 'rgba(0,0,0,0.5)'; ctx.fillRect(-400, -440, 820, 900);
    ctx.fillStyle = '#d8ccb0'; ctx.fillRect(-410, -460, 820, 900);
    ctx.font = "40px 'Special Elite'"; ctx.fillStyle = 'rgba(60,50,40,0.75)'; ctx.textAlign = 'center';
    ctx.fillText('DDR · THÜRINGEN', 0, -390);
    ctx.fillText('BRD · BAYERN', 0, 410);
    // border
    ctx.strokeStyle = COL.red; ctx.lineWidth = 7; ctx.setLineDash([26, 16]);
    ctx.beginPath(); ctx.moveTo(-410, 10);
    for (let x = -410; x <= 410; x += 20) ctx.lineTo(x, 10 + Math.sin(x * 0.012) * 40 + Math.sin(x * 0.031) * 14);
    ctx.stroke(); ctx.setLineDash([]);
    ctx.font = "26px 'Oswald'"; ctx.fillStyle = COL.red; ctx.fillText('GRENZE', 300, -30);
    // towns
    const A = [-130, -250], B = [90, 250];
    ctx.fillStyle = '#2b2620';
    ctx.beginPath(); ctx.arc(A[0], A[1], 14, 0, 7); ctx.arc(B[0], B[1], 14, 0, 7); ctx.fill();
    ctx.font = "30px 'Special Elite'";
    ctx.fillText('Oberlemnitz', A[0], A[1] - 34);
    ctx.fillText('Naila', B[0] + 4, B[1] + 52);
    // route
    const k = easeInOut(lt / (sc.beat * 3));
    ctx.strokeStyle = '#2b2620'; ctx.lineWidth = 5; ctx.setLineDash([4, 14]); ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(A[0], A[1]);
    const N = 40;
    let px = A[0], py = A[1];
    for (let i = 1; i <= Math.floor(N * k); i++) {
      const u = i / N;
      px = lerp(A[0], B[0], u) - Math.sin(u * Math.PI) * 90; py = lerp(A[1], B[1], u);
      ctx.lineTo(px, py);
    }
    ctx.stroke(); ctx.setLineDash([]);
    balloon(px, py - 70, 32, { color: '#2b2620' });
    ctx.restore();
    stamp('IM WESTEN', 330, 1520, -0.12, '#2f7a3a', lt - sc.beat * 3, 58);
  },

  recap(sc, t, lt, p) {
    sky([[0, '#2b2340'], [0.45, '#8a4a4a'], [0.75, '#e08a4a'], [1, '#f2c27a']]);
    const sunY = lerp(1500, 1380, p);
    const g = ctx.createRadialGradient(540, sunY, 30, 540, sunY, 600);
    g.addColorStop(0, 'rgba(255,230,160,0.9)'); g.addColorStop(0.15, 'rgba(255,210,130,0.5)'); g.addColorStop(1, 'rgba(255,210,130,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 700, W, 1220);
    hills(1500, 100, '#5a3540', 121);
    hills(1600, 80, '#2a1c26', 131);
    balloon(lerp(380, 640, p), 1050 + Math.sin(lt * 1.2) * 10, 150, { people: 8, color: '#1c1420' });
    ground(1650, '#140e14');
  },

  calendar(sc, t, lt, p) {
    sky([[0, '#1a1410'], [1, '#2e2219']]);
    const g = ctx.createRadialGradient(540, 1150, 60, 540, 1150, 750);
    g.addColorStop(0, 'rgba(255,215,150,0.25)'); g.addColorStop(1, 'rgba(255,215,150,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 400, W, 1520);
    const months = ['JULI', 'AUGUST', 'SEPTEMBER'];
    const step = sc.beat * 2;
    const m = Math.min(2, Math.floor(lt / step));
    const flip = clamp((lt - m * step) / 0.18);
    paper(540, 1200, 560, 640, 0.02, (w, h) => {
      ctx.fillStyle = COL.red; ctx.fillRect(-w / 2, -h / 2, w, 130);
      ctx.fillStyle = COL.white; ctx.font = "70px Anton"; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText('1979', 0, -h / 2 + 66);
      ctx.save(); ctx.scale(1, m > 0 ? easeOut(flip) : 1);
      ctx.fillStyle = '#2b2620'; ctx.font = "96px Anton";
      ctx.fillText(months[m], 0, 0);
      ctx.restore();
      ctx.font = "34px 'Special Elite'"; ctx.fillStyle = 'rgba(43,38,32,0.7)';
      ctx.fillText(m === 2 ? '16.' : '', 0, 120);
    });
    if (m === 2) {
      ctx.save(); ctx.strokeStyle = COL.red; ctx.lineWidth = 8;
      const k = easeOut((lt - 2 * step - 0.1) / 0.3);
      ctx.beginPath(); ctx.ellipse(552, 1314, 90, 60, 0.1, 0, Math.PI * 2 * k); ctx.stroke(); ctx.restore();
    }
    // needle stitching along the bottom
    ctx.fillStyle = COL.ink; ctx.fillRect(0, 1640, W, 280);
    ctx.strokeStyle = COL.yellow; ctx.lineWidth = 5; ctx.setLineDash([24, 18]);
    ctx.beginPath(); ctx.moveTo(0, 1700); ctx.lineTo(W * clamp(lt / sc.dur), 1700); ctx.stroke(); ctx.setLineDash([]);
  },

  cinema(sc, t, lt, p) {
    sky([[0, '#050507'], [1, '#100c0c']]);
    // screen
    ctx.fillStyle = grad(820, 1320, [[0, '#2b2340'], [0.6, '#c0644a'], [1, '#f2c27a']]);
    ctx.fillRect(140, 820, 800, 500);
    balloon(lerp(420, 660, p), 1040, 110, { people: 8, color: '#140e14' });
    ctx.strokeStyle = '#2a2a2a'; ctx.lineWidth = 16; ctx.strokeRect(140, 820, 800, 500);
    // projector beam
    const fl = 0.16 + 0.04 * Math.sin(lt * 40);
    const bg = ctx.createLinearGradient(540, 1900, 540, 820);
    bg.addColorStop(0, `rgba(255,245,220,${fl * 2})`); bg.addColorStop(1, 'rgba(255,245,220,0)');
    ctx.fillStyle = bg;
    ctx.beginPath(); ctx.moveTo(520, 1900); ctx.lineTo(140, 820); ctx.lineTo(940, 820); ctx.lineTo(560, 1900); ctx.closePath(); ctx.fill();
    // seats
    ctx.fillStyle = COL.ink;
    for (let row = 0; row < 3; row++) {
      for (let x = -40 + row * 30; x < W + 60; x += 110) {
        const y = 1500 + row * 120;
        ctx.beginPath(); ctx.arc(x, y, 34, 0, 7); ctx.fill();
        ctx.fillRect(x - 46, y + 20, 92, 120);
      }
    }
    // film strip frame
    ctx.fillStyle = '#0c0c0c'; ctx.fillRect(0, 700, 70, 760); ctx.fillRect(W - 70, 700, 70, 760);
    ctx.fillStyle = '#3a3a3a';
    const off = (lt * 300) % 60;
    for (let y = 700 - 60 + off; y < 1460; y += 60) { ctx.fillRect(18, y, 34, 30); ctx.fillRect(W - 52, y, 34, 30); }
  },

  museum(sc, t, lt, p) {
    sky([[0, '#151619'], [1, '#2a2b30']]);
    ctx.fillStyle = '#1d1e22'; ctx.fillRect(0, 1560, W, 360);
    // spotlights
    [[300, 0.0], [780, 1.3]].forEach(([x, ph]) => {
      const a = 0.18 + 0.03 * Math.sin(lt * 3 + ph);
      const g = ctx.createLinearGradient(0, 700, 0, 1560);
      g.addColorStop(0, `rgba(255,240,210,${a})`); g.addColorStop(1, 'rgba(255,240,210,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(x - 30, 700); ctx.lineTo(540 - 320, 1560); ctx.lineTo(540 + 320, 1560); ctx.lineTo(x + 30, 700); ctx.closePath(); ctx.fill();
    });
    // hanging balloon with cables
    ctx.strokeStyle = '#555'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(400, 700); ctx.lineTo(450, 900); ctx.moveTo(680, 700); ctx.lineTo(630, 900); ctx.stroke();
    balloon(540, 1060 + Math.sin(lt * 1.5) * 6, 170, { people: 0 });
    // plaque
    paper(540, 1640, 420, 110, 0, (w, h) => {
      ctx.font = "30px 'Special Elite'"; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText('Fluchtballon · Naila 1979', 0, 0);
    });
    for (let k = 0; k < 4; k++) person(150 + k * 270 + Math.sin(lt + k) * 10, 1600, k % 2 ? 260 : 240, { color: '#0b0b0e' });
  },

  title(sc, t, lt, p) {
    sky([[0, '#05060d'], [1, '#1b1630']]);
    burst(540, 1250, '#2a2346', lt * 0.4, 0.7);
    // black-red-gold glow from below
    const g = ctx.createLinearGradient(0, 1500, 0, H);
    g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.5, 'rgba(221,0,0,0.25)'); g.addColorStop(1, 'rgba(255,206,0,0.3)');
    ctx.fillStyle = g; ctx.fillRect(0, 1500, W, 420);
    ring(540, 1250, 470, COL.red, 6, 0.7);
    balloon(540, lerp(1250, 1150, easeOut(p)), 260, { flame: 0.8 + 0.2 * Math.sin(lt * 25), people: 8 });
  },

  reveal(sc, t, lt, p) {
    sky([[0, '#0a0f0a'], [1, '#18301c']]);
    burst(540, 1100, '#2f6b3a', lt * 0.6, 0.55);
    ring(540, 1100, 380 + lt * 60, COL.yellow, 8, 0.6);
    hills(1650, 70, '#0b140d', 141);
    for (let k = 0; k < 8; k++) person(260 + k * 80, 1660, k % 4 > 1 ? 120 : 175, { color: '#050806', arm: k % 2 ? -0.9 - 0.3 * Math.sin(lt * 8 + k) : undefined });
    ground(1655, '#050806');
  },

  end(sc, t, lt, p) {
    sky([[0, '#06070c'], [1, '#121420']]);
    ring(540, 820, 430, COL.red, 4, 0.35 + 0.15 * Math.sin(lt * 2));
    // emblem
    const cx = 540, cy = 820, r = 300;
    ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.clip();
    EMBLEM[TL.story.emblem || 'balloon'](cx, cy, r, lt);
    ctx.restore();
    const cine = TL.story.textStyle === 'cinematic';
    const accent = cine ? COL.crimson : COL.yellow;
    ring(cx, cy, r, accent, 10);
    if (cine) cineLine(sc.name, 1180, 76, 'gradient', lt, 0);
    else textBlock(sc.name, W / 2, 1180, 104, COL.white, lt);
    ctx.font = "34px 'Oswald'"; ctx.textAlign = 'center'; ctx.fillStyle = 'rgba(244,239,230,0.8)';
    ctx.fillText(sc.sub, W / 2, 1340);
    ctx.fillStyle = accent; ctx.font = "40px 'Oswald'";
    ctx.fillText(sc.tag, W / 2, 1400);
    const d = lt - sc.beat * 3;
    if (d > 0) {
      if (cine) cineLine(sc.quote, 1460, 52, COL.crimson, d, 0);
      else textBlock(sc.quote, W / 2, 1460, 64, COL.yellow, d);
      ctx.globalAlpha = clamp((d - 0.4) / 0.3);
      ctx.font = "30px 'Oswald'"; ctx.fillStyle = 'rgba(244,239,230,0.9)';
      ctx.fillText('WENN DU BIS HIER GESCHAUT HAST…', W / 2, 1580);
      ctx.fillText(`FOLGEN · LIKEN · TEILEN  ${TL.story.handle}`, W / 2, 1622);
      ctx.fillText('UND SCHREIB, WELCHE GESCHICHTE ALS NÄCHSTES KOMMT', W / 2, 1664);
      ctx.fillStyle = accent; ctx.font = cine ? "34px Cinzel" : "38px 'Anton'";
      ctx.fillText('HAST DU DIE BIENE GESEHEN?', W / 2, 1720);
      ctx.globalAlpha = 1;
    }
  },
};

// ---------- v4: characters, particles, Schwebebahn ----------
const EL = { body: '#8d92a3', shade: '#6f7486', ear: '#c99aa0', dark: '#2a2830' };

// Animated elephant. (x, y) = ground point under the body; facing 1 = right.
// o.walk: leg phase, o.trunk: -1 (down) … 1 (up), o.ear: flap phase, o.shake: jitter
function elephant(x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y);
  if (o.rot) ctx.rotate(o.rot);
  ctx.scale(s * (o.facing || 1), s);
  if (o.shake) ctx.translate(Math.sin(o.shake * 60) * 6, Math.cos(o.shake * 47) * 3);
  const leg = (lx, ph, col) => {
    ctx.save(); ctx.translate(lx, -80); ctx.rotate(o.walk !== undefined ? Math.sin(o.walk + ph) * 0.3 : 0);
    ctx.fillStyle = col; ctx.beginPath(); ctx.roundRect(-17, 0, 34, 84, 10); ctx.fill(); ctx.restore();
  };
  leg(-62, Math.PI, EL.shade); leg(48, 0, EL.shade);
  // tail
  ctx.strokeStyle = EL.shade; ctx.lineWidth = 7; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(-105, -150); ctx.quadraticCurveTo(-130 + Math.sin((o.walk || 0) * 2) * 8, -120, -122, -90); ctx.stroke();
  // body
  ctx.fillStyle = EL.body; ctx.beginPath(); ctx.ellipse(0, -140, 112, 80, 0, 0, 7); ctx.fill();
  leg(-88, 0, EL.body); leg(26, Math.PI, EL.body);
  if (o.bandage) {
    ctx.save(); ctx.translate(-95, -150); ctx.rotate(0.3); ctx.fillStyle = '#f1d9b5';
    ctx.fillRect(-34, -10, 68, 20); ctx.rotate(Math.PI / 2); ctx.fillRect(-34, -10, 68, 20); ctx.restore();
  }
  // head + ear
  ctx.beginPath(); ctx.arc(100, -175, 64, 0, 7); ctx.fill();
  const flap = 0.85 + 0.15 * Math.sin(o.ear || 0);
  ctx.save(); ctx.translate(72, -172); ctx.scale(flap, 1);
  ctx.fillStyle = EL.shade; ctx.beginPath(); ctx.ellipse(0, 0, 50, 62, 0.15, 0, 7); ctx.fill();
  ctx.fillStyle = EL.ear; ctx.beginPath(); ctx.ellipse(4, 2, 32, 44, 0.15, 0, 7); ctx.fill();
  ctx.restore();
  // trunk
  const a = o.trunk || 0;
  ctx.strokeStyle = EL.body; ctx.lineWidth = 30; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(150, -160);
  ctx.quadraticCurveTo(200, lerp(-110, -230, (a + 1) / 2), lerp(175, 235, (a + 1) / 2), lerp(-50, -300, (a + 1) / 2));
  ctx.stroke();
  // eye
  ctx.fillStyle = EL.dark; ctx.beginPath(); ctx.arc(118, -190, 9, 0, 7); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(121, -193, 3, 0, 7); ctx.fill();
  ctx.restore();
}

// Particle burst under gravity. dt = seconds since burst.
function particles(x, y, dt, seed, o = {}) {
  if (dt < 0 || dt > (o.life || 1.3)) return;
  const r = rng(seed), g = o.gravity ?? 1800, n = o.n || 40;
  for (let i = 0; i < n; i++) {
    const ang = lerp(o.a0 ?? -Math.PI * 0.95, o.a1 ?? -Math.PI * 0.05, r());
    const sp = lerp(o.v0 || 400, o.v1 || 1200, r());
    const px = x + Math.cos(ang) * sp * dt, py = y + Math.sin(ang) * sp * dt + 0.5 * g * dt * dt;
    const sz = lerp(o.s0 || 6, o.s1 || 18, r()) * (1 - dt / (o.life || 1.3) * 0.5);
    ctx.globalAlpha = clamp(1 - dt / (o.life || 1.3));
    ctx.fillStyle = o.color || '#d4edf5';
    if (o.rect) { ctx.save(); ctx.translate(px, py); ctx.rotate(dt * 8 * (r() - 0.5) * 4); ctx.fillRect(-sz, -sz / 3, sz * 2, sz * 0.7); ctx.restore(); }
    else { ctx.beginPath(); ctx.arc(px, py, sz, 0, 7); ctx.fill(); }
  }
  ctx.globalAlpha = 1;
}

function speedLines(t, alpha = 0.35, up = true) {
  const r = rng(909);
  ctx.strokeStyle = '#fff'; ctx.lineCap = 'round';
  for (let i = 0; i < 26; i++) {
    const x = r() * W, len = 120 + r() * 280, sp = 2200 + r() * 1800;
    let y = (r() * H + t * sp) % (H + len);
    if (up) y = H - y;
    ctx.globalAlpha = alpha * (0.4 + 0.6 * r()); ctx.lineWidth = 2 + r() * 4;
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x, y + len); ctx.stroke();
  }
  ctx.globalAlpha = 1;
}

// Press-camera flashes popping at random spots.
function camFlashes(t, seed, region) {
  const slot = Math.floor(t / 0.35), r = rng(seed + slot);
  const dt = t - slot * 0.35;
  if (r() < 0.75) {
    const x = lerp(region[0], region[2], r()), y = lerp(region[1], region[3], r());
    const a = Math.exp(-dt * 14);
    const g = ctx.createRadialGradient(x, y, 2, x, y, 160);
    g.addColorStop(0, `rgba(255,255,255,${a})`); g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g; ctx.fillRect(x - 160, y - 160, 320, 320);
  }
}

function river(y, t, deep = '#163a45') {
  ctx.fillStyle = grad(y, H, [[0, '#2f6672'], [1, deep]]); ctx.fillRect(0, y, W, H - y);
  ctx.strokeStyle = 'rgba(220,240,245,0.25)'; ctx.lineWidth = 3;
  for (let k = 0; k < 7; k++) {
    const yy = y + 30 + k * 45, off = (t * (40 + k * 10)) % 120;
    ctx.beginPath();
    for (let x = -120 + off; x < W + 120; x += 120) { ctx.moveTo(x, yy); ctx.quadraticCurveTo(x + 30, yy - 8, x + 60, yy); }
    ctx.stroke();
  }
}

function ripples(x, y, dt) {
  for (let k = 0; k < 3; k++) {
    const d = dt - k * 0.25;
    if (d < 0 || d > 1.6) continue;
    ctx.strokeStyle = `rgba(230,245,250,${0.6 * (1 - d / 1.6)})`; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.ellipse(x, y, 60 + d * 260, 14 + d * 50, 0, 0, 7); ctx.stroke();
  }
}

// Schwebebahn track: beam plus A-frame supports; offset scrolls the supports.
function rail(y, offset = 0, groundY = 1600) {
  ctx.fillStyle = COL.ink;
  const step = 420;
  for (let x = -step + ((offset % step) + step) % step; x < W + step; x += step) {
    ctx.beginPath(); ctx.moveTo(x - 20, y); ctx.lineTo(x - 140, groundY); ctx.lineTo(x - 110, groundY); ctx.lineTo(x, y + 30);
    ctx.lineTo(x + 110, groundY); ctx.lineTo(x + 140, groundY); ctx.lineTo(x + 20, y); ctx.closePath(); ctx.fill();
  }
  ctx.fillRect(0, y - 14, W, 34);
}

// Hanging car. o.elephant draws Tuffi behind the windows, o.hole breaks the side open.
function swCar(x, yRail, o = {}) {
  ctx.save();
  if (o.swing) { ctx.translate(x, yRail); ctx.rotate(o.swing); ctx.translate(-x, -yRail); }
  ctx.fillStyle = COL.ink;
  ctx.fillRect(x - 70, yRail - 26, 140, 30);
  ctx.fillRect(x - 9, yRail, 18, 70);
  const bx = x - 190, by = yRail + 70, bw = 380, bh = 180;
  ctx.fillStyle = '#2f5560'; ctx.beginPath(); ctx.roundRect(bx, by, bw, bh, 34); ctx.fill();
  ctx.fillStyle = '#e8d9b0'; ctx.fillRect(bx, by + bh - 40, bw, 12);
  ctx.save(); ctx.beginPath();
  for (let k = 0; k < 5; k++) ctx.rect(bx + 22 + k * 70, by + 26, 56, 76);
  ctx.clip();
  ctx.fillStyle = '#f2e3bc'; ctx.fillRect(bx, by, bw, bh);
  if (o.elephant) elephant(x + (o.ex || 0), by + 175, 0.55, o.elephant);
  ctx.restore();
  if (o.hole) {
    ctx.fillStyle = COL.ink;
    ctx.beginPath(); ctx.moveTo(bx + bw - 10, by + 20); ctx.lineTo(bx + bw - 90, by + 50); ctx.lineTo(bx + bw - 60, by + 95);
    ctx.lineTo(bx + bw - 110, by + 140); ctx.lineTo(bx + bw - 15, by + 165); ctx.closePath(); ctx.fill();
  }
  ctx.restore();
}

function cityline(y, color, seed) {
  const r = rng(seed); ctx.fillStyle = color;
  for (let x = -20; x < W; ) {
    const w = 60 + r() * 90, h = 80 + r() * 200;
    ctx.fillRect(x, y - h, w, h);
    if (r() < 0.3) { ctx.beginPath(); ctx.moveTo(x, y - h); ctx.lineTo(x + w / 2, y - h - 60); ctx.lineTo(x + w, y - h); ctx.fill(); }
    x += w + 4;
  }
}

function duskSky() { sky([[0, '#1d2a4a'], [0.45, '#5a4a6e'], [0.75, '#d9825a'], [1, '#f2c27a']]); }

function circusTent(x, y, s, t) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  for (let k = 0; k < 8; k++) {
    ctx.fillStyle = k % 2 ? '#e9dcc0' : COL.red;
    ctx.beginPath(); ctx.moveTo(0, -330); ctx.lineTo(-260 + k * 65, 0); ctx.lineTo(-260 + (k + 1) * 65, 0); ctx.closePath(); ctx.fill();
  }
  ctx.fillStyle = COL.ink; ctx.fillRect(-4, -400, 8, 80);
  ctx.fillStyle = COL.yellow;
  ctx.beginPath(); ctx.moveTo(4, -400); ctx.lineTo(70 + Math.sin(t * 6) * 10, -385); ctx.lineTo(4, -365); ctx.fill();
  ctx.restore();
}

function polaroid(x, y, rot, draw, caption) {
  paper(x, y, 460, 540, rot, (w, h) => {
    ctx.save(); ctx.beginPath(); ctx.rect(-w / 2 + 30, -h / 2 + 30, w - 60, w - 60); ctx.clip();
    draw(w, h); ctx.restore();
    ctx.font = "30px 'Special Elite'"; ctx.textAlign = 'center'; ctx.fillStyle = '#2b2620';
    ctx.fillText(caption || '', 0, h / 2 - 40);
  });
}

Object.assign(ART, {
  tHook(sc, t, lt, p) {
    duskSky();
    cityline(1450, '#3a2c3c', 7);
    river(1560, t);
    rail(1000, -lt * 60);
    const jumpAt = sc.beat * 3.5;
    const cx = lerp(240, 560, clamp(lt / jumpAt));
    swCar(cx, 1000, { swing: Math.sin(lt * 5) * 0.04, hole: lt > jumpAt, elephant: lt < jumpAt ? { trunk: Math.sin(lt * 4) * 0.6, ear: lt * 6, shake: lt > jumpAt - 1 ? lt : 0 } : null });
    if (lt > jumpAt) {
      const d = lt - jumpAt, fall = Math.min(d, 0.55);
      const ex = cx + 200 + fall * 260, ey = 1220 + 900 * fall * fall * 2.2;
      if (d < 0.55) elephant(ex, ey, 0.6, { rot: fall * 1.2, trunk: 1, ear: lt * 20 });
      particles(cx + 170, 1200, d, 3, { rect: true, color: '#2f5560', n: 18, v0: 200, v1: 700 });
      particles(ex, 1580, d - 0.55, 5, { n: 50 });
      ripples(ex, 1600, d - 0.55);
    }
  },

  tTitle(sc, t, lt, p) {
    sky([[0, '#0c1424'], [1, '#2a2440']]);
    burst(540, 1250, '#2d3550', lt * 0.4, 0.7);
    ring(540, 1250, 470, COL.red, 6, 0.7);
    elephant(470, 1600, 1.5, { trunk: 0.6 + 0.4 * Math.sin(lt * 3), ear: lt * 5, walk: undefined });
  },

  tCity(sc, t, lt, p) {
    duskSky();
    cityline(1350, '#4a3446', 21);
    rail(1000, 0, 1500);
    circusTent(540, 1560, 1.1, t);
    ground(1550, '#1a1218');
    for (let k = 0; k < 6; k++) {
      ctx.fillStyle = [COL.red, COL.yellow, '#3f6f8f'][k % 3];
      const x = 120 + k * 170, yy = 1180 + Math.sin(k) * 20;
      ctx.beginPath(); ctx.moveTo(x, yy); ctx.lineTo(x + 40, yy + 60 + Math.sin(t * 5 + k) * 6); ctx.lineTo(x + 80, yy); ctx.fill();
    }
  },

  tPoster(sc, t, lt, p) {
    sky([[0, '#241a14'], [1, '#3b2a1e']]);
    ctx.fillStyle = '#4b3527'; for (let y = 600; y < H; y += 90) ctx.fillRect(0, y, W, 4);
    paper(540, 1200, 640, 820, -0.03, (w, h) => {
      ctx.fillStyle = COL.red; ctx.fillRect(-w / 2, -h / 2, w, 170);
      ctx.fillStyle = COL.yellow; ctx.font = "80px Anton"; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillText('ZIRKUS ALTHOFF', 0, -h / 2 + 88);
      ctx.fillStyle = '#2b2620'; ctx.font = "44px 'Special Elite'";
      ctx.fillText('Sensation!', 0, -h / 2 + 230);
      ctx.fillText('Ein Elefant fährt', 0, h / 2 - 150);
      ctx.fillText('Schwebebahn!', 0, h / 2 - 95);
    });
    elephant(470, 1280, 0.9, { trunk: Math.sin(lt * 3) * 0.5 + 0.3, ear: lt * 5 });
    stamp('WERBE-COUP', 700, 900, 0.12, COL.red, lt - sc.beat * 3, 56);
  },

  tBoard(sc, t, lt, p) {
    duskSky();
    cityline(1300, '#4a3446', 31);
    // station platform
    ctx.fillStyle = '#1b1419'; ctx.fillRect(0, 1380, W, 540);
    ctx.fillStyle = COL.ink; ctx.fillRect(0, 760, W, 40); ctx.fillRect(80, 760, 30, 620); ctx.fillRect(W - 110, 760, 30, 620);
    swCar(700, 900, {});
    const k = clamp(lt / (sc.beat * 4));
    elephant(lerp(-150, 430, k), 1400, 0.9, { walk: lt * 9, trunk: Math.sin(lt * 4) * 0.4, ear: lt * 7 });
    for (let i = 0; i < 4; i++) person(560 + i * 120, 1400, 230 + (i % 2) * 20, { arm: -0.6 });
    camFlashes(t, 41, [560, 1150, 960, 1250]);
  },

  tRide(sc, t, lt, p) {
    duskSky();
    ctx.save(); ctx.translate(-((lt * 40) % 400), 0); cityline(1450, '#3a2c3c', 51); ctx.translate(400, 0); cityline(1450, '#3a2c3c', 51); ctx.restore();
    river(1560, t);
    rail(1000, -lt * 900);
    const nerv = lt > sc.beat * 2;
    swCar(540, 1000, { swing: Math.sin(lt * (nerv ? 14 : 4)) * (nerv ? 0.07 : 0.03), elephant: { trunk: nerv ? Math.sin(lt * 20) : 0, ear: lt * (nerv ? 30 : 6), shake: nerv ? lt : 0 } });
    if (nerv) {
      ctx.fillStyle = '#9fd3ff';
      for (let k = 0; k < 3; k++) { const d = (lt * 2 + k / 3) % 1; ctx.globalAlpha = 1 - d; ctx.beginPath(); ctx.arc(470 + k * 30, 1110 - d * 80, 9, 0, 7); ctx.fill(); }
      ctx.globalAlpha = 1;
    }
  },

  tCrash(sc, t, lt, p) {
    duskSky();
    cityline(1450, '#3a2c3c', 61);
    river(1560, t);
    rail(1000, 0);
    const brk = sc.beat * 2;
    swCar(540, 1000, { swing: lt > brk ? 0.12 * Math.exp(-(lt - brk) * 3) * Math.sin(lt * 18) : Math.sin(lt * 16) * 0.06, hole: lt > brk,
      elephant: lt < brk ? { shake: lt, trunk: 1, ear: lt * 30 } : null });
    if (lt > brk) {
      const d = lt - brk;
      elephant(700 + d * 80, 1280 + Math.min(d, 1) * 60, 0.62, { trunk: 1, ear: lt * 25, rot: 0.2 });
      particles(700, 1180, d, 7, { rect: true, color: '#2f5560', n: 26, v0: 300, v1: 900, a0: -Math.PI * 0.6, a1: Math.PI * 0.1 });
      particles(700, 1180, d, 8, { color: '#f2e3bc', n: 20, s0: 4, s1: 9 });
    }
  },

  tFall(sc, t, lt, p) {
    sky([[0, '#d9825a'], [1, '#2f6672']]);
    speedLines(t, 0.4, true);
    const k = clamp(lt / (sc.counter.dur * sc.beat));
    rail(lerp(300, -200, k), 0, lerp(1100, 600, k));
    elephant(560 + Math.sin(lt * 9) * 20, lerp(1250, 1500, k), 0.95, { rot: Math.sin(lt * 3) * 0.4 + 0.5, trunk: 1, ear: lt * 40 });
    if (k >= 1) {
      river(1560, t);
      particles(560, 1580, lt - sc.counter.dur * sc.beat, 9, { n: 70, v0: 500, v1: 1500, s0: 8, s1: 22 });
    }
  },

  tSplash(sc, t, lt, p) {
    duskSky();
    cityline(1300, '#3a2c3c', 71);
    river(1380, t);
    particles(540, 1440, lt, 11, { n: 80, v0: 600, v1: 1600, s0: 8, s1: 24, life: 1.6 });
    ripples(540, 1470, lt);
    elephant(470, 1560, 0.9, { trunk: Math.sin(lt * 2) * 0.3, ear: lt * 4 });
    ctx.fillStyle = 'rgba(47,102,114,0.9)'; ctx.fillRect(0, 1480, W, 440);
    river(1480, t);
  },

  tWatch(sc, t, lt, p) {
    sky([[0, '#1d2a4a'], [1, '#6b5a6e']]);
    river(1300, t, '#0e2a33');
    ripples(640, 1420, (lt % 1.8));
    ctx.fillStyle = 'rgba(220,240,245,0.5)';
    for (let k = 0; k < 6; k++) { const d = (lt * 0.8 + k / 6) % 1; ctx.beginPath(); ctx.arc(640 + Math.sin(k * 3) * 30, 1460 - d * 120, 6 + k % 3 * 3, 0, 7); ctx.fill(); }
    // bridge with onlookers
    ctx.fillStyle = COL.ink; ctx.fillRect(0, 1050, 520, 40);
    for (let x = 0; x < 520; x += 60) ctx.fillRect(x, 980, 8, 80);
    ctx.fillRect(0, 980, 520, 10);
    for (let k = 0; k < 6; k++) person(40 + k * 80, 1050, 210 + (k % 3) * 15, { arm: k % 2 ? 0.6 : undefined });
  },

  tReveal(sc, t, lt, p) {
    sky([[0, '#0a1a14'], [1, '#1d4a3a']]);
    burst(540, 1150, '#2f6b4a', lt * 0.6, 0.55);
    ring(540, 1150, 380 + lt * 60, COL.yellow, 8, 0.6);
    river(1560, t);
    elephant(470, 1640, 1.1, { trunk: 1, ear: lt * 8 });
    // water fountain from the trunk
    for (let k = 0; k < 6; k++) particles(700, 1100, (lt + k * 0.2) % 1.2, 20 + k, { n: 10, v0: 300, v1: 700, a0: -Math.PI * 0.7, a1: -Math.PI * 0.3, s0: 6, s1: 12, life: 1.2 });
  },

  tScratch(sc, t, lt, p) {
    sky([[0, '#2a2440'], [1, '#5a4a6e']]);
    river(1500, t);
    elephant(600, 1700, 2.3, { facing: -1, bandage: lt > sc.beat * 2, ear: lt * 4, trunk: -0.3, walk: undefined });
  },

  tDrink(sc, t, lt, p) {
    duskSky();
    cityline(1250, '#4a3446', 81);
    river(1360, t);
    elephant(520, 1540, 1.0, { trunk: -1 + 0.15 * Math.sin(lt * 3), ear: lt * 4 });
    ripples(760, 1520, lt % 1.6);
    // flowers on the near bank + hidden bee
    ctx.fillStyle = '#1b2a1b'; ctx.fillRect(0, 1700, W, 220);
    const r = rng(303);
    for (let i = 0; i < 30; i++) {
      const x = r() * W, y = 1690 + r() * 120;
      ctx.strokeStyle = '#25402a'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(x, y + 50); ctx.lineTo(x, y); ctx.stroke();
      ctx.fillStyle = ['#c86a8a', '#e8c25a', '#9a7ac8'][i % 3]; ctx.beginPath(); ctx.arc(x, y, 10, 0, 7); ctx.fill();
    }
    if (TL.story.beeScene === sc.art) bee(880 - lt * 30, 1680 + Math.sin(lt * 5) * 12, 1.0, lt);
  },

  tPhoto(sc, t, lt, p) {
    sky([[0, '#151418'], [1, '#2a2730']]);
    // press camera
    ctx.save(); ctx.translate(540, 1200);
    ctx.fillStyle = COL.ink; ctx.beginPath(); ctx.roundRect(-220, -150, 440, 300, 24); ctx.fill();
    ctx.fillStyle = '#2a2a2e'; ctx.beginPath(); ctx.arc(0, 0, 110, 0, 7); ctx.fill();
    ctx.fillStyle = '#0e0e10'; ctx.beginPath(); ctx.arc(0, 0, 70, 0, 7); ctx.fill();
    ctx.fillStyle = COL.ink; ctx.fillRect(160, -330, 24, 190);
    ctx.fillStyle = '#c9c9cc'; ctx.beginPath(); ctx.arc(172, -360, 60, Math.PI, 0); ctx.fill();
    ctx.restore();
    const f = lt * 1.0 % 1;
    if (lt < sc.beat * 2) { const a = Math.exp(-f * 10); ctx.fillStyle = `rgba(255,255,255,${a * 0.8})`; ctx.beginPath(); ctx.arc(712, 840, 200 * (1 + f), 0, 7); ctx.fill(); }
    stamp('KEIN FOTO', 540, 1560, -0.1, COL.red, lt - sc.beat * 2, 70);
  },

  tMontage(sc, t, lt, p) {
    sky([[0, '#1d1a16'], [1, '#2e2a24']]);
    polaroid(540, 1180, 0.04, (w, h) => {
      ctx.fillStyle = grad(-h / 2, h / 2, [[0, '#b9b2a2'], [1, '#6f6a60']]); ctx.fillRect(-w / 2, -h / 2, w, h);
      ctx.save(); ctx.filter = 'grayscale(1)';
      ctx.fillStyle = '#3d3a36'; ctx.fillRect(-w / 2, -120, w, 18);
      const k = easeOut((lt - sc.beat) / (sc.beat * 2));
      elephant(lerp(-40, 10, k), lerp(-40, 60, k), 0.55, { trunk: 1, rot: 0.4 });
      ctx.restore();
      ctx.strokeStyle = COL.red; ctx.setLineDash([12, 10]); ctx.lineWidth = 4;
      ctx.strokeRect(-110 + lerp(-40, 10, k) * 0, -150, 200, 210); ctx.setLineDash([]);
    }, 'Wuppertal 1950 (?)');
    // scissors
    ctx.fillStyle = '#c9c9cc'; ctx.save(); ctx.translate(820, 1520); ctx.rotate(-0.6 + Math.sin(lt * 10) * 0.1);
    ctx.fillRect(-90, -6, 120, 12); ctx.rotate(0.3 * Math.sin(lt * 10)); ctx.fillRect(-90, -6, 120, 12);
    ctx.strokeStyle = '#c9c9cc'; ctx.lineWidth = 8; ctx.beginPath(); ctx.arc(-110, -20, 20, 0, 7); ctx.arc(-110, 20, 20, 0, 7); ctx.stroke(); ctx.restore();
    stamp('MONTAGE', 540, 1580, -0.1, COL.red, lt - sc.beat * 3, 76);
  },

  tParis(sc, t, lt, p) {
    sky([[0, '#060918'], [1, '#2a2348']]);
    stars(61, 160, 0.8, 1300, t);
    // Eiffel tower
    ctx.fillStyle = COL.ink; ctx.save(); ctx.translate(780, 1550);
    ctx.beginPath(); ctx.moveTo(-170, 0); ctx.quadraticCurveTo(-60, -260, -18, -720); ctx.lineTo(18, -720); ctx.quadraticCurveTo(60, -260, 170, 0);
    ctx.lineTo(110, 0); ctx.quadraticCurveTo(0, -160, -110, 0); ctx.closePath(); ctx.fill();
    ctx.fillRect(-120, -260, 240, 22); ctx.fillRect(-70, -470, 140, 16); ctx.fillRect(-3, -800, 6, 90);
    ctx.restore();
    circusTent(300, 1560, 0.8, t);
    ground(1550);
    elephant(300, 1700, 0.5, { trunk: Math.sin(lt * 2) * 0.3, ear: lt * 3, walk: lt * 4 });
  },

  tLegacy(sc, t, lt, p) {
    sky([[0, '#2a1d17'], [1, '#4a3324']]);
    ctx.fillStyle = '#2a1a12';
    [1080, 1380].forEach(y => ctx.fillRect(60, y, 960, 26));
    for (let k = 0; k < 5; k++) {
      const pop = easeBack((lt - k * 0.25) / 0.3);
      if (pop <= 0) continue;
      ctx.save(); ctx.translate(150 + k * 190, 1080); ctx.scale(pop, pop);
      elephant(0, 0, 0.42, { trunk: 0.5 * Math.sin(lt * 3 + k), ear: lt * 5 + k });
      ctx.restore();
    }
    paper(380, 1560, 380, 240, -0.08, (w, h) => {
      ctx.font = "34px 'Special Elite'"; ctx.textAlign = 'center';
      ctx.fillText('Gruß aus', 0, -30); ctx.fillText('Wuppertal', 0, 20);
    });
    paper(720, 1590, 300, 200, 0.07, (w, h) => {
      ctx.fillStyle = '#3f6f8f'; ctx.fillRect(-w / 2 + 20, -h / 2 + 20, w - 40, h - 40);
      elephant(-20, 70, 0.38, { trunk: 1 });
    });
  },

  tRecap(sc, t, lt, p) {
    duskSky();
    cityline(1450, '#3a2c3c', 91);
    river(1560, t);
    rail(1000, -lt * 120);
    elephant(560, 1640, 0.8, { trunk: 0.8 + 0.2 * Math.sin(lt * 4), ear: lt * 6 });
    particles(720, 1260, lt % 1.1, 77, { n: 10, v0: 200, v1: 500, a0: -Math.PI * 0.7, a1: -Math.PI * 0.3, s0: 5, s1: 10, life: 1.1 });
  },
});

const EMBLEM = {
  balloon(cx, cy, r) {
    ctx.fillStyle = grad(cy - r, cy + r, [[0, '#2b2340'], [0.55, '#c0644a'], [1, '#f2c27a']]); ctx.fillRect(cx - r, cy - r, 2 * r, 2 * r);
    ctx.fillStyle = '#000'; ctx.fillRect(cx - r, cy + 150, 2 * r, 50);
    ctx.fillStyle = '#DD0000'; ctx.fillRect(cx - r, cy + 200, 2 * r, 50);
    ctx.fillStyle = '#FFCE00'; ctx.fillRect(cx - r, cy + 250, 2 * r, 60);
    balloon(cx, cy - 70, 110, { people: 8, color: '#120e14' });
  },
  elephant(cx, cy, r, lt) {
    ctx.fillStyle = grad(cy - r, cy + r, [[0, '#1d2a4a'], [0.55, '#d9825a'], [1, '#2f6672']]); ctx.fillRect(cx - r, cy - r, 2 * r, 2 * r);
    ctx.fillStyle = COL.ink; ctx.fillRect(cx - r, cy - 150, 2 * r, 22);
    elephant(cx - 60, cy + 210, 0.95, { trunk: 0.7 + 0.3 * Math.sin(lt * 3), ear: lt * 5 });
  },
};

// ---------- v5: human lead, storm light, depth of field, infographics ----------
// Girl silhouette with ponytail. o.walk: leg/arm phase, o.wade: hide legs below this y.
function girl(x, y, h, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(o.facing || 1, 1);
  const c = o.color || COL.ink;
  ctx.fillStyle = c; ctx.strokeStyle = c; ctx.lineCap = 'round';
  const w = o.walk;
  const sw = w !== undefined ? Math.sin(w) : 0;
  // legs
  ctx.lineWidth = h * 0.075;
  [[-1, sw], [1, -sw]].forEach(([side, a]) => {
    ctx.save(); ctx.translate(side * h * 0.03, -h * 0.45); ctx.rotate(a * 0.35);
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, h * 0.45); ctx.stroke(); ctx.restore();
  });
  // dress / torso
  ctx.beginPath(); ctx.moveTo(-h * 0.1, -h * 0.78); ctx.lineTo(h * 0.1, -h * 0.78);
  ctx.lineTo(h * 0.15, -h * 0.4); ctx.lineTo(-h * 0.15, -h * 0.4); ctx.closePath(); ctx.fill();
  // arms
  ctx.lineWidth = h * 0.055;
  [[-1, -sw], [1, sw]].forEach(([side, a]) => {
    ctx.save(); ctx.translate(side * h * 0.1, -h * 0.75); ctx.rotate(a * 0.4 + side * 0.15 + (o.arm && side > 0 ? o.arm : 0));
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, h * 0.32); ctx.stroke(); ctx.restore();
  });
  // head + ponytail
  ctx.beginPath(); ctx.arc(0, -h * 0.88, h * 0.09, 0, 7); ctx.fill();
  ctx.lineWidth = h * 0.05;
  ctx.beginPath(); ctx.moveTo(-h * 0.06, -h * 0.92);
  ctx.quadraticCurveTo(-h * 0.2, -h * 0.85 + sw * h * 0.02, -h * 0.16 - Math.abs(sw) * h * 0.04, -h * 0.72); ctx.stroke();
  ctx.restore();
}

function lightning(x, y0, y1, seed, a) {
  if (a <= 0.02) return;
  const r = rng(seed);
  ctx.save(); ctx.strokeStyle = `rgba(235,240,255,${a})`; ctx.lineWidth = 7; ctx.shadowColor = '#cfe0ff'; ctx.shadowBlur = 30;
  ctx.beginPath(); ctx.moveTo(x, y0);
  let px = x;
  for (let y = y0; y < y1; y += 60) { px += (r() - 0.5) * 120; ctx.lineTo(px, y); }
  ctx.stroke(); ctx.restore();
}

// Brightness of storm flashes at time lt for the given strike times.
function strikes(lt, times) {
  let a = 0;
  for (const s of times) { const d = lt - s; if (d >= 0 && d < 0.5) a = Math.max(a, Math.exp(-d * 9) * (d < 0.08 || d > 0.14 ? 1 : 0.3)); }
  return a;
}

function rain(t, alpha = 0.35, n = 90) {
  const r = rng(4242);
  ctx.strokeStyle = `rgba(200,215,235,${alpha})`; ctx.lineWidth = 2;
  ctx.beginPath();
  for (let i = 0; i < n; i++) {
    const x = (r() * (W + 400) - t * 300) % (W + 400), sp = 1600 + r() * 800;
    const y = (r() * H + t * sp) % H;
    const xx = (x + W + 400) % (W + 400) - 200;
    ctx.moveTo(xx, y); ctx.lineTo(xx - 18, y + 60);
  }
  ctx.stroke();
}

// Turboprop airliner side view. o.split: gap between the two halves, o.fire.
function plane(x, y, s, o = {}, t = 0) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); if (o.rot) ctx.rotate(o.rot);
  const half = (dx, part) => {
    ctx.save(); ctx.translate(dx, part === 'back' ? (o.split || 0) * 0.6 : 0); if (part === 'back' && o.split) ctx.rotate(o.split * 0.002);
    ctx.fillStyle = o.color || '#1a1c26';
    if (part === 'front') {
      ctx.beginPath(); ctx.moveTo(-20, -40); ctx.lineTo(260, -40); ctx.quadraticCurveTo(330, -30, 340, 0); ctx.quadraticCurveTo(330, 30, 260, 40); ctx.lineTo(-20, 40); ctx.closePath(); ctx.fill();
      ctx.beginPath(); ctx.moveTo(40, 10); ctx.lineTo(-60, 120); ctx.lineTo(10, 120); ctx.lineTo(140, 10); ctx.closePath(); ctx.fill();
      ctx.fillStyle = '#f2dfa8'; for (let k = 0; k < 6; k++) ctx.fillRect(0 + k * 40, -16, 18, 16);
      ctx.fillStyle = '#2a2c38'; for (const ex of [-10, 70]) { ctx.fillRect(ex, 50, 60, 22); ctx.fillStyle = 'rgba(220,220,230,0.5)'; ctx.fillRect(ex + 58, 26 + Math.sin(t * 90) * 30, 4, 50); ctx.fillStyle = '#2a2c38'; }
    } else {
      ctx.beginPath(); ctx.moveTo(-20, -40); ctx.lineTo(-300, -30); ctx.lineTo(-360, -120); ctx.lineTo(-310, -120); ctx.lineTo(-250, -40); ctx.lineTo(-300, 20); ctx.lineTo(-20, 40); ctx.closePath(); ctx.fill();
      ctx.fillStyle = '#f2dfa8'; for (let k = 0; k < 5; k++) ctx.fillRect(-60 - k * 40, -16, 18, 16);
    }
    ctx.restore();
  };
  half(o.split || 0, 'front'); half(-(o.split || 0), 'back');
  ctx.restore();
  if (o.fire) particles(x - (o.split || 0) * s, y, (t * 3) % 0.6, Math.floor(t * 5), { color: '#ff9a3a', n: 18, v0: 60, v1: 260, gravity: -200, life: 0.6, s0: 8, s1: 22 });
}

// Jungle layer; blur > 0 gives a depth-of-field look for far layers.
// Static layers are drawn once to an offscreen canvas and reused (blur is expensive).
const LAYER_CACHE = {};
function jungle(baseY, color, seed, blur = 0, scale = 1) {
  const key = [baseY, color, seed, blur, scale].join('|');
  if (!LAYER_CACHE[key]) {
    const c = document.createElement('canvas'); c.width = W; c.height = H;
    const main = ctx; ctx = c.getContext('2d');
    jungleRaw(baseY, color, seed, blur, scale);
    ctx = main; LAYER_CACHE[key] = c;
  }
  ctx.drawImage(LAYER_CACHE[key], 0, 0);
}

function jungleRaw(baseY, color, seed, blur, scale) {
  if (blur) ctx.filter = `blur(${blur}px)`;
  const r = rng(seed); ctx.fillStyle = color;
  ctx.fillRect(0, baseY, W, H - baseY);
  for (let i = 0; i < 16; i++) {
    const x = r() * W, h = (180 + r() * 260) * scale, rad = (70 + r() * 70) * scale;
    ctx.fillRect(x - 8 * scale, baseY - h, 16 * scale, h);
    ctx.beginPath(); ctx.arc(x, baseY - h, rad, 0, 7); ctx.arc(x - rad * 0.7, baseY - h + rad * 0.4, rad * 0.75, 0, 7); ctx.arc(x + rad * 0.7, baseY - h + rad * 0.4, rad * 0.75, 0, 7); ctx.fill();
  }
  ctx.filter = 'none';
}

function palmFront(x, y, s, t, color = '#06100a') {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = color; ctx.strokeStyle = color;
  ctx.lineWidth = 26; ctx.beginPath(); ctx.moveTo(0, 0); ctx.quadraticCurveTo(30, -300, 10, -600); ctx.stroke();
  for (let k = 0; k < 7; k++) {
    ctx.save(); ctx.translate(10, -600); ctx.rotate(-Math.PI + k * Math.PI / 6 + Math.sin(t * 1.5 + k) * 0.05);
    ctx.beginPath(); ctx.ellipse(170, 0, 180, 30, 0.2, 0, 7); ctx.fill(); ctx.restore();
  }
  ctx.restore();
}

function jungleScene(t, lt, o = {}) {
  sky([[0, o.top || '#0e1a14'], [1, o.bottom || '#2a4a34']]);
  jungle(1100, '#1d3a28', 11, 6, 0.8);
  jungle(1350, '#12281b', 21, 2.5, 1);
}

function river2(y, t) { river(y, t, '#0f2a24'); }

// Outline body for the injuries scene (like the shrapnel scene in the originals).
function bodyOutline(cx, top, h, color) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = 4; ctx.globalAlpha = 0.9;
  ctx.beginPath(); ctx.arc(cx, top + h * 0.08, h * 0.08, 0, 7); ctx.stroke();
  ctx.beginPath(); ctx.roundRect(cx - h * 0.14, top + h * 0.18, h * 0.28, h * 0.36, 30); ctx.stroke();
  ctx.beginPath(); ctx.roundRect(cx - h * 0.25, top + h * 0.19, h * 0.08, h * 0.32, 20); ctx.roundRect(cx + h * 0.17, top + h * 0.19, h * 0.08, h * 0.32, 20); ctx.stroke();
  ctx.beginPath(); ctx.roundRect(cx - h * 0.12, top + h * 0.55, h * 0.1, h * 0.43, 20); ctx.roundRect(cx + h * 0.02, top + h * 0.55, h * 0.1, h * 0.43, 20); ctx.stroke();
  for (let y = top + h * 0.22; y < top + h * 0.5; y += 18) { ctx.globalAlpha = 0.25; ctx.beginPath(); ctx.moveTo(cx - h * 0.1, y); ctx.lineTo(cx + h * 0.1, y); ctx.stroke(); }
  ctx.restore();
}

function hotspot(x, y, dt) {
  if (dt < 0) return;
  const pulse = 1 + 0.3 * Math.sin(dt * 10);
  const g = ctx.createRadialGradient(x, y, 2, x, y, 70 * pulse);
  g.addColorStop(0, 'rgba(255,80,60,0.9)'); g.addColorStop(1, 'rgba(255,80,60,0)');
  ctx.fillStyle = g; ctx.fillRect(x - 80, y - 80, 160, 160);
  ctx.fillStyle = "#ff5a40"; ctx.beginPath(); ctx.arc(x, y, Math.max(0, 10 * easeBack(dt / 0.2)), 0, 7); ctx.fill();
}

Object.assign(ART, {
  jHook(sc, t, lt, p) {
    sky([[0, '#0b0f1c'], [0.6, '#2a3348'], [1, '#4a5a4a']]);
    clouds(31, 300, 1500, 14, 0.25, t * 6, '#8a94a8');
    const fl = strikes(lt, [0.3, sc.beat * 3.5]);
    if (fl) { ctx.fillStyle = `rgba(220,230,255,${fl * 0.5})`; ctx.fillRect(0, 0, W, H); }
    lightning(760, 0, 1000, 5, fl);
    const k = clamp((lt - sc.beat * 3.5) / (sc.beat * 4));
    const seatY = lerp(900, 1700, k * k);
    speedLines(t, 0.15 + 0.3 * k, true);
    ctx.save(); ctx.translate(540, seatY); ctx.rotate(Math.sin(lt * 2) * 0.5 * k); ctx.scale(1.8, 1.8);
    ctx.shadowColor = `rgba(200,220,255,${0.5 + fl * 0.5})`; ctx.shadowBlur = 25;
    ctx.fillStyle = '#1a1c26';
    for (let s = -1; s <= 1; s++) { ctx.fillRect(s * 80 - 35, -40, 70, 70); ctx.fillRect(s * 80 - 35, -120, 18, 90); }
    girl(0, 30, 150, { color: '#0a0b10', arm: -1.8 });
    ctx.restore();
    rain(t, 0.25);
  },

  jTitle(sc, t, lt, p) {
    sky([[0, '#08120c'], [1, '#1c3826']]);
    burst(540, 1250, '#22402c', lt * 0.4, 0.7);
    ring(540, 1250, 470, COL.red, 6, 0.7);
    jungle(1500, '#0b1a10', 41, 3, 0.9);
    girl(540, 1640, 520, { color: '#05080a', walk: undefined });
  },

  jBoard(sc, t, lt, p) {
    sky([[0, '#2a4a7a'], [0.7, '#9ab8d8'], [1, '#e8dcc0']]);
    clouds(51, 1300, 1800, 12, 0.6, t * 30, '#f4f2ee');
    plane(560, 1050 + Math.sin(lt * 2) * 10, 1.4, {}, t);
    // two passengers seen through a window bubble
    ctx.save(); ctx.beginPath(); ctx.arc(300, 1500, 170, 0, 7); ctx.fillStyle = '#e9e2d0'; ctx.fill(); ctx.clip();
    ctx.fillStyle = grad(1330, 1670, [[0, '#7aa6d0'], [1, '#d8e6f0']]); ctx.fillRect(130, 1330, 340, 340);
    girl(250, 1700, 300, { color: '#2a2a33' }); person(350, 1700, 330, { color: '#2a2a33' });
    ctx.restore();
    ring(300, 1500, 170, '#1a1c26', 14);
  },

  jStorm(sc, t, lt, p) {
    sky([[0, '#05070e'], [1, '#22283a']]);
    const fl = strikes(lt, [sc.beat * 1, sc.beat * 2, sc.beat * 2.3, sc.beat * 4]);
    clouds(61, 200, 1700, 16, 0.3 + fl * 0.4, t * 10, '#5a647a');
    if (fl) { ctx.fillStyle = `rgba(220,230,255,${fl * 0.55})`; ctx.fillRect(0, 0, W, H); }
    lightning(640, 0, 1100, 9 + Math.floor(lt * 3), fl);
    const shake = lt > sc.beat * 2 ? lt : 0;
    plane(540 + Math.sin(shake * 40) * 12, 1150 + Math.cos(shake * 33) * 10, 1.3, { color: fl > 0.3 ? '#3a3e52' : '#14161f', fire: lt > sc.beat * 2.2, rot: Math.sin(lt * 3) * 0.04 }, t);
    rain(t, 0.4, 140);
  },

  jBreak(sc, t, lt, p) {
    sky([[0, '#0a0608'], [1, '#3a1a14']]);
    clouds(71, 300, 1700, 14, 0.25, t * 10, '#6a4a44');
    const k = easeOut(lt / (sc.beat * 3));
    plane(540, 1150 + k * 120, 1.25, { split: lerp(0, 160, k), fire: true, rot: k * 0.3 }, t);
    particles(540, 1150, lt, 31, { rect: true, color: '#1a1c26', n: 30, v0: 200, v1: 900, life: 2 });
    particles(540, 1150, lt - 0.3, 32, { color: '#ff9a3a', n: 30, v0: 100, v1: 600, life: 1.2 });
    rain(t, 0.3);
  },

  jFall(sc, t, lt, p) {
    sky([[0, '#1a2230'], [1, '#2a4a34']]);
    const k = clamp(lt / (sc.counter.dur * sc.beat));
    clouds(81, 0, H, 18, 0.35, -t * 400, '#8a94a8');
    speedLines(t, 0.5, true);
    if (k > 0.6) jungle(lerp(2400, 1500, (k - 0.6) / 0.4), '#12281b', 91, 0, 1.2);
    ctx.save(); ctx.translate(540, 1250); ctx.rotate(lt * 2.4);
    ctx.fillStyle = '#1a1c26';
    for (let s = -1; s <= 1; s++) { ctx.fillRect(s * 80 - 35, -40, 70, 70); ctx.fillRect(s * 80 - 35, -120, 18, 90); }
    girl(0, 30, 150, { color: '#0a0b10', arm: -2 });
    ctx.restore();
  },

  jWake(sc, t, lt, p) {
    jungleScene(t, lt);
    // sun rays through the canopy
    ctx.fillStyle = 'rgba(255,240,190,0.08)';
    for (let k = 0; k < 4; k++) { ctx.beginPath(); ctx.moveTo(200 + k * 220, 600); ctx.lineTo(120 + k * 220, 1700); ctx.lineTo(220 + k * 220, 1700); ctx.lineTo(260 + k * 220, 600); ctx.fill(); }
    ctx.fillStyle = '#0a140d'; ctx.fillRect(0, 1600, W, 320);
    ctx.save(); ctx.translate(560, 1600); ctx.rotate(-0.3);
    ctx.fillStyle = '#1a1c26'; for (let s = -1; s <= 1; s++) ctx.fillRect(s * 80 - 35, -40, 70, 70);
    ctx.restore();
    const up = easeInOut((lt - sc.beat * 2) / (sc.beat * 2));
    ctx.save(); ctx.translate(380, 1660); ctx.rotate(lerp(-1.4, 0, up)); girl(0, 0, 400, { color: '#05080a' }); ctx.restore();
    palmFront(60, 1920, 1.2, t); palmFront(1040, 1920, 1.0, t + 2);
  },

  jCount(sc, t, lt, p) {
    sky([[0, '#06080c'], [1, '#141820']]);
    const fade = clamp((lt - sc.beat * 2.5) / (sc.beat * 2));
    const cols = 12, s = 64, x0 = 540 - (cols - 1) * s / 2, y0 = 1000;
    for (let i = 0; i < 92; i++) {
      const cx = x0 + (i % cols) * s, cy = y0 + Math.floor(i / cols) * (s + 14);
      const me = i === 57;
      const appear = clamp((lt - i * 0.012) / 0.15);
      if (appear <= 0) continue;
      const col = me ? COL.yellow : `rgba(244,239,230,${0.85 - 0.72 * fade})`;
      ctx.save(); ctx.translate(cx, cy); ctx.scale(appear, appear);
      if (me && fade > 0) { const g = ctx.createRadialGradient(0, 0, 4, 0, 0, 80); g.addColorStop(0, `rgba(242,194,48,${0.6 * fade})`); g.addColorStop(1, 'rgba(242,194,48,0)'); ctx.fillStyle = g; ctx.fillRect(-80, -80, 160, 160); }
      ctx.fillStyle = col; ctx.beginPath(); ctx.arc(0, -18, 10, 0, 7); ctx.fill();
      ctx.beginPath(); ctx.roundRect(-13, -6, 26, 32, 8); ctx.fill();
      ctx.restore();
    }
  },

  jInjury(sc, t, lt, p) {
    sky([[0, '#0a0e1c'], [1, '#141c30']]);
    ring(540, 1300, 420, 'rgba(120,150,220,0.3)', 3);
    bodyOutline(540, 900, 820, '#7aa0e0');
    const sp = sc.spots || [[500, 1080, sc.start + sc.beat * 0.5], [680, 1250, sc.start + sc.beat * 2], [520, 960, sc.start + sc.beat * 3.5]];
    sp.forEach(([x, y, at]) => hotspot(x, y, t - at));
  },

  jMother(sc, t, lt, p) {
    jungleScene(t, lt, { top: '#0a120e', bottom: '#1a2a20' });
    ctx.fillStyle = '#081009'; ctx.fillRect(0, 1600, W, 320);
    // wreckage pieces
    ctx.fillStyle = '#1a1c26';
    ctx.save(); ctx.translate(760, 1600); ctx.rotate(-0.2); ctx.fillRect(-160, -60, 320, 70); ctx.restore();
    ctx.save(); ctx.translate(250, 1610); ctx.rotate(0.4); ctx.fillRect(-60, -40, 120, 40); ctx.restore();
    girl(lerp(260, 600, easeInOut(p)), 1660, 420, { color: '#05080a', walk: lt * 4, facing: 1 });
    rain(t, 0.15, 50);
    palmFront(1000, 1920, 1.1, t);
  },

  jFather(sc, t, lt, p) {
    sky([[0, '#14100c'], [1, '#2a2218']]);
    paper(540, 1250, 620, 760, -0.03, (w, h) => {
      ctx.fillStyle = grad(-h / 2 + 40, h / 2 - 120, [[0, '#9a8e70'], [1, '#5a5240']]); ctx.fillRect(-w / 2 + 40, -h / 2 + 40, w - 80, h - 200);
      person(0, h / 2 - 160, 420, { color: '#2a2418' });
      ctx.font = "34px 'Special Elite'"; ctx.textAlign = 'center'; ctx.fillStyle = '#2b2620';
      ctx.fillText('Papa · Forschungsstation', 0, h / 2 - 70);
    });
    // animated stream line hinting the advice
    ctx.strokeStyle = '#6ab0d0'; ctx.lineWidth = 10; ctx.lineCap = 'round';
    const k = easeInOut((lt - sc.beat * 2) / (sc.beat * 3));
    ctx.beginPath();
    for (let i = 0; i <= 40 * k; i++) { const u = i / 40; const x = 120 + u * 840, y = 1720 + Math.sin(u * 12) * 30; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
    ctx.stroke();
    if (k > 0) { ctx.fillStyle = '#6ab0d0'; const u = k, x = 120 + u * 840, y = 1720 + Math.sin(u * 12) * 30; ctx.beginPath(); ctx.moveTo(x + 30, y); ctx.lineTo(x - 10, y - 24); ctx.lineTo(x - 10, y + 24); ctx.fill(); }
  },

  jWade(sc, t, lt, p) {
    jungleScene(t, lt);
    ctx.save(); ctx.translate(-((lt * 60) % 300), 0); jungle(1450, '#0b1a10', 101, 0, 1.1); ctx.restore();
    river2(1540, t);
    girl(520, 1760, 460, { color: '#05080a', walk: lt * 5 });
    ctx.fillStyle = 'rgba(28,70,64,0.92)'; ctx.fillRect(0, 1620, W, 300);
    ripples(520, 1630, lt % 1.2);
    rain(t, 0.2, 60);
    palmFront(-40, 1920, 1.3, t); palmFront(1100, 1920, 1.2, t + 1);
    // day counter
    const day = 1 + Math.floor(clamp(lt / sc.dur) * 8.99);
    ctx.font = "60px 'Black Ops One'"; ctx.textAlign = 'center'; ctx.fillStyle = COL.yellow;
    ctx.fillText(`TAG ${day}`, 540, TL.story.textStyle === 'cinematic' ? 1290 : 900);
  },

  jMaggot(sc, t, lt, p) {
    sky([[0, '#0c0a08'], [1, '#22180f']]);
    // close-up arm with wound
    ctx.fillStyle = '#5a4436'; ctx.beginPath(); ctx.roundRect(120, 1150, 840, 260, 120); ctx.fill();
    ctx.fillStyle = '#7a2a22'; ctx.beginPath(); ctx.ellipse(560, 1270, 170, 50, 0.05, 0, 7); ctx.fill();
    const r = rng(77);
    ctx.fillStyle = '#efe6cf';
    for (let i = 0; i < 16; i++) {
      const bx = 430 + r() * 260, by = 1250 + r() * 40, ph = r() * 6;
      ctx.save(); ctx.translate(bx + Math.sin(lt * 4 + ph) * 8, by); ctx.rotate(Math.sin(lt * 3 + ph) * 0.6);
      ctx.beginPath(); ctx.ellipse(0, 0, 11, 4, 0, 0, 7); ctx.fill(); ctx.restore();
    }
  },

  jBoat(sc, t, lt, p) {
    jungleScene(t, lt, { top: '#121a12', bottom: '#2a3a28' });
    river2(1500, t);
    // hut
    ctx.fillStyle = '#0a0d08';
    ctx.fillRect(560, 1180, 360, 260);
    ctx.beginPath(); ctx.moveTo(520, 1190); ctx.lineTo(740, 1020); ctx.lineTo(960, 1190); ctx.fill();
    for (const px of [580, 880]) ctx.fillRect(px, 1430, 20, 120);
    // boat
    ctx.beginPath(); ctx.moveTo(140, 1540); ctx.lineTo(560, 1540); ctx.lineTo(500, 1600); ctx.lineTo(200, 1600); ctx.closePath(); ctx.fill();
    // canister + pour
    ctx.fillStyle = COL.red; ctx.fillRect(380, 1470, 70, 80);
    girl(300, 1560, 260, { color: '#05080a', arm: -1.2 });
    if (lt > sc.beat * 2) particles(330, 1420, (lt - sc.beat * 2) % 0.6, 61, { color: '#d8c070', n: 12, v0: 60, v1: 160, a0: Math.PI * 0.3, a1: Math.PI * 0.7, life: 0.6, s0: 3, s1: 6 });
    if (TL.story.beeScene === sc.art) bee(880 - lt * 25, 1340 + Math.sin(lt * 5) * 12, 0.9, lt);
  },

  jRescue(sc, t, lt, p) {
    jungleScene(t, lt, { top: '#1a2418', bottom: '#4a5a3a' });
    ctx.fillStyle = '#0a0d08'; ctx.fillRect(0, 1580, W, 340);
    ctx.fillStyle = '#0a0d08'; ctx.fillRect(620, 1260, 320, 320);
    ctx.beginPath(); ctx.moveTo(580, 1270); ctx.lineTo(780, 1110); ctx.lineTo(980, 1270); ctx.fill();
    const k = easeOut(lt / (sc.beat * 3));
    for (let i = 0; i < 3; i++) person(lerp(1200, 560 + i * 110, k), 1600, 300 + i * 10, { color: '#05080a', arm: i === 0 ? -0.5 : undefined });
    girl(260, 1600, 330, { color: '#05080a' });
    const g = ctx.createRadialGradient(260, 1450, 20, 260, 1450, 400);
    g.addColorStop(0, 'rgba(255,220,150,0.25)'); g.addColorStop(1, 'rgba(255,220,150,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 1000, W, 900);
  },

  jReveal(sc, t, lt, p) {
    sky([[0, '#0a1a10'], [1, '#2a5a34']]);
    burst(540, 1150, '#2f6b3a', lt * 0.6, 0.55);
    ring(540, 1150, 380 + lt * 60, COL.yellow, 8, 0.6);
    jungle(1600, '#0b1a10', 111, 2, 1);
    girl(540, 1720, 380, { color: '#05080a', arm: -2.6 });
  },

  jLater(sc, t, lt, p) {
    sky([[0, '#0e1a14'], [0.6, '#3a5a3a'], [1, '#c8b070']]);
    jungle(1250, '#1d3a28', 121, 5, 0.8);
    jungle(1500, '#12281b', 131, 1.5, 1);
    girl(540, 1700, 330, { color: '#05080a', walk: lt * 3 });
    // research notebook
    paper(840, 1560, 220, 260, 0.1, (w, h) => {
      ctx.strokeStyle = 'rgba(43,38,32,0.4)'; ctx.lineWidth = 2;
      for (let i = 0; i < 6; i++) { ctx.beginPath(); ctx.moveTo(-80, -90 + i * 34); ctx.lineTo(80, -90 + i * 34); ctx.stroke(); }
    });
    palmFront(60, 1920, 1.2, t);
  },

  jRecap(sc, t, lt, p) {
    sky([[0, '#1a2a4a'], [0.5, '#c06a4a'], [1, '#f2c27a']]);
    jungle(1400, '#3a2a24', 141, 4, 0.8);
    jungle(1600, '#140e0c', 151, 0, 1);
    girl(540, 1700, 360, { color: '#05080a' });
  },
});

// Reference-style blasts layered onto the crash scenes in cinematic mode.
['jHook', 'jStorm', 'jBreak'].forEach(name => {
  const base = ART[name];
  ART[name] = function (sc, t, lt, p) {
    base(sc, t, lt, p);
    if (TL.story.textStyle !== 'cinematic' || sc.blastAt || TL.story.hits) return;
    if (name === 'jHook') blast(560, 620, lt - sc.beat * 3.5, 401, 1.1);
    if (name === 'jStorm') blast(600, 1150, lt - sc.beat * 2, 402, 1.0);
    if (name === 'jBreak') { blast(540, 1150, lt, 403, 1.3); blast(420, 1260, lt - sc.beat * 2, 404, 0.9); }
  };
});

EMBLEM.jungle = function (cx, cy, r, lt) {
  ctx.fillStyle = grad(cy - r, cy + r, [[0, '#1a2a4a'], [0.5, '#c06a4a'], [1, '#2a4a34']]); ctx.fillRect(cx - r, cy - r, 2 * r, 2 * r);
  jungle(cy + 120, '#0b1a10', 161, 0, 0.7);
  girl(cx, cy + 240, 300, { color: '#05080a' });
  plane(cx + 140, cy - 160, 0.35, {}, lt);
};

// ---------- post ----------
let grain = null;
function makeGrain() {
  grain = document.createElement('canvas'); grain.width = 512; grain.height = 512;
  const g = grain.getContext('2d'), img = g.createImageData(512, 512);
  const r = rng(77);
  for (let i = 0; i < img.data.length; i += 4) { const v = r() * 255; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 18; }
  g.putImageData(img, 0, 0);
}

function motes(t) {
  const r = rng(555);
  ctx.fillStyle = '#fff';
  for (let i = 0; i < 46; i++) {
    const x0 = r() * W, sp = 20 + r() * 50, sz = 1.5 + r() * 3.5, ph = r() * 100;
    const y = H - ((t * sp + ph * 30) % (H + 100));
    const x = x0 + Math.sin(t * 0.8 + ph) * 30;
    ctx.globalAlpha = 0.12 + 0.18 * (0.5 + 0.5 * Math.sin(t * 2 + ph));
    ctx.beginPath(); ctx.arc(x, y, sz, 0, 7); ctx.fill();
  }
  ctx.globalAlpha = 1;
}

function post(t) {
  const v = ctx.createRadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.75);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.55)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, W, H);
  if (!grain) makeGrain();
  const step = TL && TL.story.v8 ? Math.floor(t / TL.beat) : 0;
  const ox = -(step * 137) % 512, oy = -(step * 251) % 512;
  ctx.globalAlpha = 1;
  for (let x = ox; x < W; x += 512) for (let y = oy; y < H; y += 512) ctx.drawImage(grain, x, y);
}

// ---------- frame ----------
function renderFrame(t) {
  const sc = t < TL.scenes[0].start ? TL.scenes[0] : (TL.scenes.find(s => t >= s.start && t < s.end) || TL.scenes[TL.scenes.length - 1]);
  const lt = Math.max(0, t - sc.start), p = clamp(lt / sc.dur);
  const BT = beatState(t);
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.clearRect(0, 0, W, H);
  // camera shake from recent impacts
  let shake = 0, flash = 0;
  const rings = [];
  for (const h of TL.hits) {
    const d = t - h.t;
    if (d < 0 || d > 1.2) continue;
    shake += h.amp * Math.exp(-d * 9);
    flash = Math.max(flash, h.flash * Math.exp(-d * 16));
    if (h.ring && d < 0.6) rings.push(d);
  }
  const CINE = TL.story.textStyle === 'cinematic';
  shake += BT.on ? (BT.down ? 9 : 3.5) * BT.k * BT.amp : 0;
  const sx = Math.sin(t * 91) * shake, sy = Math.cos(t * 77) * shake;
  ctx.translate(sx, sy);
  // punch-in on every cut, then slow push-in
  const dir = sc.i % 2 ? 1 : -1;
  const WHIP = CINE ? 0.15 : 0.1;
  const kOut = clamp(1 - (sc.end - t) / WHIP), kIn = clamp(1 - lt / WHIP);
  const whip = sc.i < TL.scenes.length - 1 ? kOut : 0;
  if (CINE) ctx.translate(dir * lerp(-12, 12, p), 0);
  else ctx.translate(dir * lerp(-30, 30, p) + dir * whip * 140 - dir * kIn * 140 * (sc.i > 0), 0);
  const blur = (whip + (sc.i > 0 ? kIn : 0)) * 16;
  if (blur > 0.5) ctx.filter = `blur(${blur.toFixed(1)}px)`;
  const pulse = !CINE && (sc.music === 'drive' || sc.music === 'reveal') ? 0.014 * Math.exp(-((t % TL.beat) / TL.beat) * 7) : 0;
  let ladder = 0, roll = 0;
  if (TL.story.v8) {
    const bar = 4 * TL.beat, nb = Math.floor(lt / bar + 1e-6), snap = easeOut(clamp((lt - nb * bar) / 0.12));
    ladder = 0.045 * (Math.max(0, nb - 1) + (nb > 0 ? snap : 0));
    const ang = n => (n === 0 ? 0 : (n % 2 ? 1 : -1) * 0.022);
    roll = lerp(ang(Math.max(0, nb - 1)), ang(nb), nb > 0 ? snap : 1);
    ctx.translate(W / 2, 1100); ctx.rotate(roll); ctx.translate(-W / 2, -1100);
  }
  const zt = TL.story.v8 ? 0.32 * whip - 0.1 * (sc.i > 0 ? kIn : 0) : 0;
  const z = CINE ? 1.05 + ladder + zt + 0.05 * p + 0.04 * (whip + (sc.i > 0 ? kIn : 0)) + 0.012 * onsetAt(t) + (BT.on ? (BT.down ? 0.05 : 0.03) * BT.k * BT.amp : 0)
    : 1.07 + 0.06 * p + 0.12 * (1 - easeOut(lt / 0.25)) + pulse + 0.3 * (whip + (sc.i > 0 ? kIn : 0));
  ctx.translate(W / 2, 1300); ctx.scale(z, z); ctx.translate(-W / 2, -1300);
  ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; ctx.setLineDash([]); ctx.lineCap = 'butt';
  // motion surges on every beat: animation time jumps forward on the hit, then eases
  const ltw = BT.on ? Math.max(0, BT.tw - sc.start) : lt;
  (ART[sc.art] || (() => {}))(sc, sc.start + ltw, ltw, clamp(ltw / sc.dur));
  sceneBlasts(sc, t);
  motes(t);
  ctx.filter = 'none';
  ctx.restore();
  post(t);
  if (CINE) {
    // muted, filmic grade + dip to dark during blur transitions
    ctx.save(); ctx.globalCompositeOperation = 'saturation'; ctx.fillStyle = 'rgba(128,128,128,0.3)'; ctx.fillRect(0, 0, W, H); ctx.restore();
    const dip = (whip + (sc.i > 0 ? kIn : 0)) * 0.35;
    if (dip > 0) { ctx.fillStyle = `rgba(0,0,0,${dip})`; ctx.fillRect(0, 0, W, H); }
  }
  for (const d of rings) ring(W / 2, 900, 80 + d * 2200, CINE ? COL.crimson : '#fff', 14 * (1 - d / 0.6), 0.7 * (1 - d / 0.6));
  ctx.save();
  ctx.translate(sx * 0.5, sy * 0.5);
  if (BT.on) { const ts = 1 + 0.02 * BT.k * BT.amp; ctx.translate(W / 2, 1000); ctx.scale(ts, ts); ctx.translate(-W / 2, -1000); }
  (CINE ? cineText : sceneText)(sc, t);
  ctx.restore();
  if (flash > 0.01) { ctx.fillStyle = `rgba(255,250,240,${flash})`; ctx.fillRect(0, 0, W, H); }
  if (BT.on) beatPulse(BT);
  if (TL.story.v8) v8Post(t, BT);
  // fade out at the very end
  const fo = clamp((t - (TL.duration - 0.6)) / 0.6);
  if (fo > 0) { ctx.fillStyle = `rgba(0,0,0,${fo})`; ctx.fillRect(0, 0, W, H); }
}

window.buildTimeline = buildTimeline;
window.renderFrame = renderFrame;
