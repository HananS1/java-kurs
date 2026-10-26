// Renders a story to MP4.
//   node render.js stories/ballonflucht.json            -> out/<id>.mp4
//   node render.js stories/ballonflucht.json --preview  -> out/<id>_preview.jpg (contact sheet)
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30;
const storyPath = process.argv[2];
const preview = process.argv.includes('--preview');
if (!storyPath) { console.error('usage: node render.js <story.json> [--preview]'); process.exit(1); }

const story = JSON.parse(fs.readFileSync(storyPath, 'utf8'));
const outDir = path.join(__dirname, 'out');
fs.mkdirSync(outDir, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'engine.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => {
    for (const f of ["76px 'Anton'", "34px 'Oswald'", "30px 'Special Elite'", "60px 'Black Ops One'"]) await document.fonts.load(f);
  });
  const tl = await page.evaluate(s => window.buildTimeline(s), story);

  const grab = t => page.evaluate(t => {
    window.renderFrame(t);
    return document.getElementById('c').toDataURL('image/jpeg', 0.93);
  }, t).then(u => Buffer.from(u.split(',')[1], 'base64'));

  if (preview) {
    const dir = path.join(outDir, 'frames');
    fs.mkdirSync(dir, { recursive: true });
    const shots = tl.scenes.map(s => s.start + (s.end - s.start) * 0.8);
    for (let i = 0; i < shots.length; i++) fs.writeFileSync(path.join(dir, `p${String(i).padStart(2, '0')}.jpg`), await grab(shots[i]));
    await browser.close();
    const cols = 7, rows = Math.ceil(shots.length / cols);
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', path.join(dir, 'p%02d.jpg'),
      '-vf', `scale=270:-1,tile=${cols}x${rows}`, '-frames:v', '1', path.join(outDir, `${story.id}_preview.jpg`)]);
    console.log('preview written');
    return;
  }

  const tlPath = path.join(outDir, `${story.id}_timeline.json`);
  const wavPath = path.join(outDir, `${story.id}.wav`);
  fs.writeFileSync(tlPath, JSON.stringify(tl));
  execFileSync('python3', [path.join(__dirname, 'audio.py'), tlPath, wavPath], { stdio: 'inherit' });

  const mp4 = path.join(outDir, `${story.id}.mp4`);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y',
    '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', wavPath,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-af', 'loudnorm=I=-13:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-shortest', '-movflags', '+faststart', mp4], { stdio: ['pipe', 'inherit', 'inherit'] });

  const frames = Math.round(tl.duration * FPS);
  for (let f = 0; f < frames; f++) {
    const buf = await grab(f / FPS);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`frame ${f}/${frames}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('written', mp4, `${tl.duration.toFixed(1)}s`);
})();
