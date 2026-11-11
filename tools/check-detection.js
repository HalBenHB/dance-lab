// Checks Where's the One's detection against the counts saved in Your songs.
//
//   node tools/check-detection.js [library folder]      (default: library/ next to server.py)
//
// Needs Node 18 or newer and ffmpeg. It runs the page's own detection code on every song in the
// folder's library.json. Songs with a saved count (from Save this count, or from fixing the 1 or the
// tempo) are scored against it; the others are listed with what detection finds, so you can check them.
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm'), { execFileSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const folder = path.resolve(process.argv[2] || path.join(ROOT, 'library'));

// The page's own code: dance table, analysis, and the tempo and dance rules.
function loadPage() {
  const script = fs.readFileSync(path.join(ROOT, 'wheres-the-one', 'index.html'), 'utf8').match(/<script>([\s\S]*)<\/script>/)[1];
  const part = (from, to) => {
    const a = script.indexOf(from), b = script.indexOf(to, a);
    if (a < 0 || b < 0) throw new Error(`The page no longer has "${from}". Update tools/check-detection.js.`);
    return script.slice(a, b);
  };
  const page = { S: { feats: null, beats: [], ibi: 0.5, k: 0 }, Math, Object, Array, Float32Array, Float64Array, Int8Array, Int32Array, Promise, setTimeout, console };
  vm.createContext(page);
  vm.runInContext([
    part('const JIVE_BASIC', 'const S = {'),
    part('/* ---------- analysis ---------- */', '/* ---------- example groove'),
    part('/* ---------- tempo and dance ---------- */', '/* ---------- UI ---------- */'),
    'this.api = { DANCES, AN_SR, spectralFeatures, onsetEnvelope, estimatePeriod, trackBeats, trimSilent, bassBetweenBeats, midpoints, guessDownbeat, oneAgreement, tempoFit, titleDances, soundDances };'
  ].join('\n'), page);
  return page;
}

function decode(file) {
  const raw = execFileSync('ffmpeg', ['-v', 'error', '-i', file, '-ac', '1', '-ar', '11025', '-f', 'f32le', '-'], { maxBuffer: 1 << 30 });
  return new Float32Array(raw.buffer, raw.byteOffset, raw.length >> 2);
}

// What the page does when a song loads: detect, then count it at the speed of the dance.
async function detect(page, file, title, dance) {
  const A = page.api, S = page.S;
  const f = await A.spectralFeatures(decode(file), A.AN_SR, () => {});
  f.O = A.onsetEnvelope(f.flux, f.fps);
  S.feats = f;
  const track = P => {
    const beats = Array.from(A.trimSilent(A.trackBeats(f.O, P), f), i => i / f.fps + f.t0);
    S.beats = A.bassBetweenBeats(beats) ? Array.from(A.midpoints(beats)) : beats;
    S.ibi = (S.beats[S.beats.length - 1] - S.beats[0]) / (S.beats.length - 1);
    S.k = A.guessDownbeat(S.beats);
  };
  const P = A.estimatePeriod(f.O, f.fps);
  track(P);
  const detectedBpm = 60 / S.ibi;
  const titleHints = Array.from(A.titleDances(title, detectedBpm)), soundHints = Array.from(A.soundDances());
  const d = A.DANCES[dance];
  if (d) {
    const group = d.group || dance, hint = titleHints.find(h => h.id === group);
    const fit = (hint && hint.mpm && A.tempoFit(d, detectedBpm, hint.mpm)) || A.tempoFit(d, detectedBpm);
    if (fit === 2 || fit === 0.5) track(P / fit);
  }
  return {
    beats: S.beats, k: S.k, bpm: 60 / S.ibi, detectedBpm,
    suggested: [...new Set([...titleHints.map(h => h.id), ...soundHints])],
    unsure: A.oneAgreement(S.beats, S.k) < 0.7
  };
}

function score(got, saved, DANCES) {
  const out = {};
  const ratio = got.bpm / saved.bpm, near = x => Math.abs(ratio / x - 1) < 0.04;
  out.tempo = near(1) ? 'right' : near(2) ? 'double' : near(0.5) ? 'half' : `wrong (${got.bpm.toFixed(1)})`;
  if (out.tempo === 'right' && saved.one != null) {
    let i = 0;
    for (let j = 1; j < got.beats.length; j++) if (Math.abs(got.beats[j] - saved.one) < Math.abs(got.beats[i] - saved.one)) i = j;
    const step = ((i - got.k) % 4 + 4) % 4, ibi = 60 / got.bpm;
    out.one = Math.abs(got.beats[i] - saved.one) > ibi / 4 ? 'half a beat off'
      : step === 0 ? 'right' : step === 2 ? 'on the 3' : step === 1 ? '1 beat early' : '1 beat late';
  } else out.one = saved.one == null ? 'not saved' : 'not checked';
  const group = DANCES[saved.dance] ? DANCES[saved.dance].group || saved.dance : null;
  out.dance = !group ? 'not saved' : got.suggested.includes(group) ? 'suggested' : got.suggested.length ? `suggested ${got.suggested.join(', ')}` : 'no suggestion';
  return out;
}

(async () => {
  let songs;
  try { songs = JSON.parse(fs.readFileSync(path.join(folder, 'library.json'), 'utf8')); }
  catch (e) { console.error(`No library.json in ${folder}. Give the folder your songs are in.`); process.exit(1); }
  const page = loadPage(), D = page.api.DANCES;
  const saved = songs.filter(s => s.count), others = songs.filter(s => !s.count);
  const tally = { tempo: 0, one: 0, checked: 0, oneChecked: 0 };
  console.log(`Checking detection in ${folder}: ${saved.length} songs with a saved count, ${others.length} without.\n`);
  for (const s of saved) {
    const file = path.join(folder, s.file);
    if (!fs.existsSync(file)) { console.log(`  missing file: ${s.file}`); continue; }
    const got = await detect(page, file, s.title, s.count.dance), r = score(got, s.count, D);
    const oneChecked = r.one !== 'not saved' && r.one !== 'not checked';
    tally.checked++;
    if (r.tempo === 'right') tally.tempo++;
    if (oneChecked) tally.oneChecked++;
    if (r.one === 'right') tally.one++;
    const ok = r.tempo === 'right' && (r.one === 'right' || r.one === 'not saved');
    const name = D[s.count.dance] ? D[s.count.dance].name : '?';
    console.log(`${ok ? 'ok  ' : 'MISS'} ${s.title.slice(0, 48).padEnd(48)} ${name.padEnd(8)} ${String(s.count.bpm).padStart(6)} BPM | tempo ${r.tempo}, the 1 ${r.one}, dance ${r.dance}${got.unsure ? ', warned not sure' : ''}`);
  }
  if (saved.length) console.log(`\nTempo right on ${tally.tempo} of ${tally.checked}. The 1 right on ${tally.one} of ${tally.oneChecked} checked.\n`);
  for (const s of others) {
    const file = path.join(folder, s.file);
    if (!fs.existsSync(file)) continue;
    const got = await detect(page, file, s.title, null);
    console.log(`  -   ${s.title.slice(0, 48).padEnd(48)} detected ${got.detectedBpm.toFixed(1).padStart(6)} BPM${got.suggested.length ? `, suggests ${got.suggested.map(id => D[id].name).join(', ')}` : ''}${got.unsure ? ', not sure where the 1 is' : ''}  (no saved count)`);
  }
})().catch(e => { console.error(e.message); process.exit(1); });
