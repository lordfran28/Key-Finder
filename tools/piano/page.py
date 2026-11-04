"""The voice-and-piano page: bars in playing order with keyboard diagrams, the shapes, and what to know."""
import json, html

CSS = r"""
:root{--bg:#F4EEE2;--surface:#FBF8F1;--sunk:#EFE7D8;--ink:#221B15;--muted:#6B5E50;--faint:#8D7F6C;--line:#D8CCB6;--accent:#2D4A7F;--accent-soft:#DFE5EF;--brass:#8C6414;--brass-soft:#F2E8D2;--voice:#8A3A1F;--voice-soft:#F3E2D8;--now:#EFE2C0;
--key-white:#FBF8F1;--key-edge:#C9BA9E;--key-black:#1E1915;--display:Georgia,serif;--body:Georgia,serif;--mono:ui-monospace,Menlo,monospace;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#13110E;--surface:#1B1814;--sunk:#221E19;--ink:#EDE4D2;--muted:#B0A38D;--faint:#857A68;--line:#3A3229;--accent:#A9BCE4;--accent-soft:#1F2738;--brass:#E2BD6B;--brass-soft:#2A2316;--voice:#E39A72;--voice-soft:#3A251B;--now:#3A3220;--key-white:#BDB29D;--key-edge:#7E7462;--key-black:#0B0A08;color-scheme:dark}}
*{box-sizing:border-box}
html{background:var(--bg)}
body{margin:0;color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.5;-webkit-text-size-adjust:100%}
.wrap{max-width:952px;margin:0 auto;padding:8px 16px 64px}
header.song{padding:18px 0 6px}
.eyebrow{font:italic 400 1rem var(--display);color:var(--muted)}
h1{font:400 clamp(2rem,6vw,3rem)/1.05 var(--display);margin:4px 0 8px}
h2{font:400 1.6rem/1.15 var(--display);margin:34px 0 6px}
h3{font:400 1.2rem/1.2 var(--display);margin:0}
.lede{max-width:44em;margin:8px 0 0;color:var(--ink)}
.facts{display:flex;flex-wrap:wrap;gap:6px 22px;list-style:none;padding:0;margin:14px 0 0}
.facts li{display:flex;flex-direction:column}.facts span{font-size:.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}.facts b{font-weight:600}
.player{position:sticky;top:0;z-index:5;background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:10px 12px;margin:18px 0 8px;display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.player audio{width:100%;height:38px}
.sw{display:flex;flex-wrap:wrap;gap:6px}
.sw button{font:inherit;font-size:.95rem;border:1px solid var(--line);background:var(--surface);color:var(--ink);border-radius:999px;padding:4px 12px;cursor:pointer}
.sw button[aria-pressed=true]{background:var(--accent);border-color:var(--accent);color:var(--surface)}
.follow{font-size:.95rem;color:var(--muted);display:flex;gap:6px;align-items:center}
.nowline{font-size:.95rem;color:var(--muted);min-height:1.4em;flex:1 1 100%}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:.9rem;color:var(--muted);margin:6px 0 0}
.legend i{display:inline-block;width:12px;height:12px;border-radius:50%;vertical-align:-1px;margin-right:5px}
.lh{background:var(--accent)}.rh{background:var(--brass)}.fl{background:var(--voice)}
.part-h{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 12px;border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:34px}
.part-h h2{margin:0}.part-h span{color:var(--muted);font-size:.95rem}
.bars{display:grid;grid-template-columns:1fr;gap:12px;margin-top:12px}
.bar{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:8px 10px 10px;scroll-margin-top:120px}
.bar.now{background:var(--now);border-color:var(--brass)}
.bh{display:flex;align-items:center;gap:8px;font-size:.9rem;color:var(--muted)}
.seek{font:600 .95rem var(--body);color:var(--ink);background:none;border:1px solid var(--line);border-radius:999px;padding:1px 10px;cursor:pointer}
.voc{display:flex;gap:2px;margin:6px 0 2px}.voc i{flex:1;height:5px;border-radius:2px;background:var(--line)}.voc i.s{background:var(--voice)}
.words{font-style:italic;color:var(--muted);font-size:.95rem;margin:2px 0}
.segs{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px}
.seg{flex:1 1 260px;min-width:0;display:flex;flex-direction:column;align-items:center;text-align:center}
.seg+.seg{border-left:1px dashed var(--line);padding-left:8px}
@media (max-width:620px){.seg+.seg{border-left:0;padding-left:0;border-top:1px dashed var(--line);padding-top:6px}}
.cn{font-weight:700;font-size:1.05rem;color:var(--accent);line-height:1.2}
.form{font-size:.78rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}
.kb{max-width:100%;height:auto;display:block;margin:4px auto 0}
.kb .w{fill:var(--key-white);stroke:var(--key-edge);stroke-width:.8}.kb .b{fill:var(--key-black)}
.kb .mc{fill:var(--muted)}
.kb circle.L{fill:var(--accent)}.kb circle.R{fill:var(--brass)}.kb circle.F{fill:var(--voice)}
.kb text.t{font:700 6.2px var(--body);fill:#fff;text-anchor:middle;dominant-baseline:central;pointer-events:none}
.kb circle.on{fill:#E3A008!important;stroke:#4A3000;stroke-width:1.2;transform-box:fill-box;transform-origin:center;transform:scale(1.25)}
@media (prefers-color-scheme:dark){.kb text.t{fill:#13110E}.kb circle.on{fill:#FFCB4D!important}}
.names{font-size:.8rem;color:var(--muted);margin-top:2px}
.back{font:400 1.5rem/1.15 var(--display);color:var(--accent);padding:18px 0}
.cont{font:italic 400 1rem/1.3 var(--display);color:var(--muted);padding:10px 0}
.tip{font-size:.88rem;font-style:italic;color:var(--ink);background:var(--brass-soft);border-radius:4px;padding:4px 7px;margin-top:6px;text-align:left}
.fill{margin-top:8px;border-top:1px dashed var(--line);padding-top:6px;text-align:center}
.fill .fh{font-size:.88rem;color:var(--voice)}
.below{margin-top:46px;border-top:2px solid var(--line);padding-top:6px}
.shapes{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-top:10px}
.shape{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:8px;text-align:center}
.shape .u{font-size:.8rem;color:var(--muted)}
.know p,.know li{max-width:46em}.know table{border-collapse:collapse;font-size:.95rem;margin:8px 0}.know td,.know th{border-bottom:1px solid var(--line);padding:4px 10px 4px 0;text-align:left}
.credits{font-size:.85rem;color:var(--muted);margin-top:30px}
@media (max-width:420px){.bars{grid-template-columns:1fr}}
"""

JS = r"""
const D = JSON.parse(document.getElementById('kf-data').textContent);
const EV = D.events;
const $ = id => document.getElementById(id);
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const BLK = [1,3,6,8,10];
function kb(lh, rh, fill, tones, id) {
  const all = lh.concat(rh).concat(fill || []);
  let lo = Math.min(...all), hi = Math.max(...all);
  lo -= 1; hi += 1;
  while (BLK.includes(lo % 12)) lo--; while (BLK.includes(hi % 12)) hi++;
  if (lo % 12 !== 0 && lo % 12 !== 5) { while (lo % 12 !== 0 && lo % 12 !== 5) lo--; }
  if (hi % 12 !== 4 && hi % 12 !== 11) { while (hi % 12 !== 4 && hi % 12 !== 11) hi++; }
  const whites = m0 => { let n = 0; for (let m = lo; m <= hi; m++) if (!BLK.includes(m % 12)) n++; return n; };
  while (whites() < 10) { lo--; while (BLK.includes(lo % 12)) lo--; if (whites() < 10) { hi++; while (BLK.includes(hi % 12)) hi++; } }
  const W = 9, H = 44, BW = 5.6, BH = 27;
  const xs = {}; let x = 0;
  for (let m = lo; m <= hi; m++) { if (!BLK.includes(m % 12)) { xs[m] = x; x += W; } }
  for (let m = lo; m <= hi; m++) { if (BLK.includes(m % 12)) xs[m] = xs[m - 1] + W - BW / 2; }
  const TW = x;
  let s = `<svg class="kb" id="${id}" viewBox="-1 -1 ${TW + 2} ${H + 2}" style="width:${Math.round((TW + 2) * 1.6)}px" role="img" aria-label="keyboard">`;
  for (let m = lo; m <= hi; m++) if (!BLK.includes(m % 12)) s += `<rect class="w" x="${xs[m]}" y="0" width="${W}" height="${H}" rx="1"/>`;
  for (let m = lo; m <= hi; m++) if (BLK.includes(m % 12)) s += `<rect class="b" x="${xs[m]}" y="0" width="${BW}" height="${BH}" rx=".8"/>`;
  if (xs[60] !== undefined) s += `<rect class="mc" x="${xs[60] + W / 2 - 2}" y="${H - 3}" width="4" height="1.4" rx=".7"><title>middle C</title></rect>`;
  const dot = (m, cls, lab) => { const b = BLK.includes(m % 12); const cx = b ? xs[m] + BW / 2 : xs[m] + W / 2; const cy = b ? BH - 6 : H - 9;
    return `<circle class="${cls}" data-m="${m}" data-h="${cls}" cx="${cx}" cy="${cy}" r="4.1"/><text class="t" x="${cx}" y="${cy + .2}">${esc(lab)}</text>`; };
  lh.forEach(m => s += dot(m, 'L', tones[m] || ''));
  rh.forEach(m => s += dot(m, 'R', tones[m] || ''));
  (fill || []).forEach((m, i) => s += dot(m, 'F', String(i + 1)));
  return s + '</svg>';
}
const nm = n => n.replace(/(\d)$/, '<sub>$1</sub>');
// ---------- bars
const body = $('arr'); let html = ''; let part = null; const barEls = []; let prevDiag = null;
const segDiag = {}; let lastDrawn = null;
D.bars.forEach((b, i) => {
  if (b.sec !== part) { if (part !== null) html += '</div>'; part = b.sec; const n1 = b.n; const last = D.bars.slice(i).findIndex(x => x.sec !== part); const nb = last < 0 ? D.bars.length - i : last;
    html += `<div class="part-h"><h2>${esc(part ? part[0].toUpperCase() + part.slice(1) : 'Song')}</h2><span>${nb} bar${nb > 1 ? 's' : ''}</span></div><div class="bars">`; }
  let segs = b.segs.map(s => {
    const dk = s.same || s.id, held = dk === prevDiag; prevDiag = dk;
    if (held) { segDiag[s.id] = lastDrawn; return `<div class="seg"><div class="cn">${esc(s.c)}</div><div class="cont">continues</div>${s.tip ? `<div class="tip">${esc(s.tip)}</div>` : ''}</div>`; }
    segDiag[s.id] = lastDrawn = 'k-' + s.id;
    const lhN = s.names.slice(0, s.lh.length), rhN = s.names.slice(s.lh.length);
    return `<div class="seg" style="flex-grow:${s.beats}"><div class="cn">${esc(s.c)}</div><div class="form">${esc(s.form)}</div>${kb(s.lh, s.rh, null, s.tones, 'k-' + s.id)}<div class="names">L ${lhN.map(x => x.replace(/\d+$/, '')).join(' ')} · R ${rhN.map(x => x.replace(/\d+$/, '')).join(' ')}</div>${s.tip ? `<div class="tip">${esc(s.tip)}</div>` : ''}</div>`;
  }).join('');
  const voc = b.voc ? `<div class="voc" aria-label="where you sing">${[...b.voc].map(c => `<i class="${c === '█' ? 's' : ''}"></i>`).join('')}</div>` : '';
  const words = b.words ? `<div class="words">${esc(b.words)}</div>` : '';
  const fill = b.fill ? `<div class="fill"><div class="fh">Fill into ${esc(b.fill.into)} · ${esc(b.fill.scale)}</div>${kb([], [], b.fill.notes, {}, 'k-' + b.fill.id)}<div class="names">${b.fill.names.map(x => x.replace(/\d+$/, '')).join(' ')}</div></div>` : '';
  html += `<article class="bar" id="bar-${i}"><div class="bh"><button class="seek" data-i="${i}">▶ Bar ${esc(b.n)}</button><span>${Math.floor(b.start / 60)}:${String(Math.floor(b.start % 60)).padStart(2, '0')}</span></div>${voc}${words}<div class="segs">${segs}</div>${fill}</article>`;
});
html += '</div>'; body.innerHTML = html;
document.querySelectorAll('article.bar').forEach(el => barEls.push(el));
// ---------- shapes
const seen = new Set(); let sh = '';
D.bars.forEach(b => b.segs.forEach(s => { if (s.same) return; const k = s.c + '|' + s.rh.join(','); if (seen.has(k)) return; seen.add(k);
  const uses = D.bars.filter(x => x.segs.some(y => y.c === s.c && y.rh.join(',') === s.rh.join(','))).map(x => x.n);
  sh += `<div class="shape"><div class="cn">${esc(s.c)}</div><div class="form">${esc(s.form)}</div>${kb(s.lh.slice(0, 1), s.rh, null, s.tones, 'sh-' + s.id)}<div class="u">bars ${uses.slice(0, 6).join(', ')}${uses.length > 6 ? '…' : ''}</div></div>`; }));
$('shapes').innerHTML = sh;
// ---------- player
const audio = $('audio');
document.querySelectorAll('.sw').forEach(sw => sw.addEventListener('click', e => {
  const b = e.target.closest('[data-src]'); if (!b) return;
  sw.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
  const t = audio.currentTime, playing = !audio.paused; audio.src = b.dataset.src;
  audio.addEventListener('loadedmetadata', () => { try { audio.currentTime = t; } catch (err) {} if (playing) { const p = audio.play(); if (p && p.catch) p.catch(() => {}); } }, { once: true });
}));
body.addEventListener('click', e => { const b = e.target.closest('.seek'); if (!b) return; audio.currentTime = Math.max(0, D.bars[+b.dataset.i].start - 0.1); const p = audio.play(); if (p && p.catch) p.catch(() => {}); });
let follow = true; $('follow').addEventListener('change', e => follow = e.target.checked);
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
let cur = -1, lit = [], raf = 0;
D.bars.forEach(b => { if (b.fill) segDiag[b.fill.id] = 'k-' + b.fill.id; });
function frame() {
  const t = audio.currentTime;
  let k = -1; for (let i = 0; i < D.bars.length; i++) { if (D.bars[i].start <= t + 0.03) k = i; else break; }
  if (k !== cur) { if (cur >= 0 && barEls[cur]) barEls[cur].classList.remove('now'); cur = k;
    if (k >= 0) { barEls[k].classList.add('now'); const b = D.bars[k]; $('nowline').innerHTML = `Bar <b>${esc(b.n)}</b> · ${b.segs.map(s => esc(s.c)).join(', ')}`;
      if (follow && !audio.paused) barEls[k].scrollIntoView({ block: 'center', behavior: reduce ? 'auto' : 'smooth' }); } }
  lit.forEach(c => c.classList.remove('on')); lit = [];
  for (const e of EV) { if (e[0] > t + 0.02) break; if (e[0] <= t && t < Math.min(e[3], e[0] + 0.9)) {
      const svg = document.getElementById(segDiag[e[4]]); if (!svg) continue;
      const c = svg.querySelector(`circle[data-m="${e[1]}"][data-h="${e[2]}"]`); if (c) { c.classList.add('on'); lit.push(c); } } }
  if (!audio.paused) raf = requestAnimationFrame(frame);
}
audio.addEventListener('play', () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(frame); });
audio.addEventListener('seeked', frame); audio.addEventListener('pause', () => cancelAnimationFrame(raf));
window.addEventListener('wheel', () => { if (!audio.paused && follow) { follow = false; $('follow').checked = false; } }, { passive: true });
window.addEventListener('touchmove', () => { if (!audio.paused && follow) { follow = false; $('follow').checked = false; } }, { passive: true });
"""

def build(meta, arr, know_html, tracks, out_path):
    """meta: title, key, bpm, meter, lede, credit; arr: Arranger output; tracks: [(label, file, locked)]."""
    ev = sorted(([round(e['t'], 3), e['midi'], e['hand'], round(e['off'], 3), e['seg']] for e in arr['events']), key=lambda x: x[0])
    data = dict(bars=arr['bars'], events=ev)
    js = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    t = html.escape
    btns = ''.join(f'<button type="button" data-src="{t(f)}"{" data-locked" if lk else ""} aria-pressed="{str(i == 0).lower()}">{t(l)}</button>' for i, (l, f, lk) in enumerate(tracks))
    facts = ''.join(f'<li><span>{t(a)}</span><b>{t(b)}</b></li>' for a, b in meta['facts'])
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{t(meta['title'])} · Piano</title><style>{CSS}</style></head><body>
<main class="wrap">
<header class="song"><div class="eyebrow">Voice and piano · {t(meta['key_disp'])}</div><h1>{t(meta['title'])}</h1>
<p class="lede">{t(meta['lede'])}</p><ul class="facts">{facts}</ul></header>
<div class="player"><audio id="audio" controls preload="metadata" src="{t(tracks[0][1])}"></audio>
<div class="sw" role="group" aria-label="Which track">{btns}</div>
<label class="follow"><input type="checkbox" id="follow" checked> Follow along</label><div class="nowline" id="nowline"></div></div>
<div class="legend"><span><i class="lh"></i>left hand</span><span><i class="rh"></i>right hand</span><span><i class="fl"></i>fill, in order</span><span>R root · 3, ♭3 thirds · 5 fifth · 6 · ♭7, 7 sevenths · 9, 11, 13 colour notes</span></div>
<section id="arr"></section>
<section class="below"><h2>The shapes in this song</h2><p>Every right-hand shape, once, with the bass under it and the bars that use it.</p><div class="shapes" id="shapes"></div></section>
<section class="know">{know_html}</section>
<p class="credits">{meta['credits']}</p>
</main>
<script id="kf-data" type="application/json">{js}</script>
<script>{JS}</script>
</body></html>"""
    open(out_path, 'w', encoding='utf-8').write(page)
