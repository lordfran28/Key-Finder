"""Build one voice-and-piano song: arrangement, piano track, the singer over the piano, the page.
    python3 build.py SLUG [--no-audio]"""
import sys, os, json, re, html, subprocess
import numpy as np, scipy.io.wavfile as w
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charts, arrange, page, piano, beginner, voices

def decode(path):
    tmp = path + '.tmp.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', path, '-ar', str(piano.SR), '-ac', '2', tmp], check=True)
    sr, x = w.read(tmp); os.remove(tmp)
    return x.astype(np.float32) / 32768

def voice_stem(mix_path, gtr_path):
    m = decode(mix_path)
    if not gtr_path: return m, 'record'
    g = decode(gtr_path); n = min(len(m), len(g)); m, g = m[:n], g[:n]
    k = float(np.sum(m * g) / max(1e-9, np.sum(g * g)))
    return m - k * g, 'stem'

def limit_tips(A):
    last = -9; count = 0
    for i, b in enumerate(A['bars']):
        keep = None
        for s in b['segs']:
            if s['tip'] and keep is None and i - last >= 2 and count < 14: keep = s; last = i; count += 1
            elif s['tip']: s['tip'] = None
        if keep is None:
            for s in b['segs']: s['tip'] = None

FAMS = [
 ('Major 7th', 'root and 7th', '3 · 5 · 7'),
 ('Major 6th', 'root and 5th', '3 · 5 · 6'),
 ('Major or minor chord', 'root and 5th', 'the chord itself'),
 ('Minor 7th', 'root and ♭7', '♭3 · 5 · ♭7'),
 ('Minor 6th', 'root and 5th', '♭3 · 5 · 6'),
 ('Dominant 7th', 'root and ♭7', '3 · 5 · ♭7'),
 ('Half-diminished (m7♭5)', 'root and ♭7', '♭3 · ♭5 · ♭7'),
 ('Diminished 7th', 'root and 𝄫7', '♭3 · ♭5 · 𝄫7'),
]

HELD = {
    'love-me-tender': {'V2.4', 'C1.4', 'V3.4', 'End 2'},
    'are-you-lonesome-tonight': {'k17', 'k23', 'E2'},
}

def know_html(A, ar, meta):
    used = {seg['form'].split(' + ')[0] for b in A['bars'] for seg in b['segs']}
    rows = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in FAMS)
    fills = [(b['n'], b['fill']) for b in A['bars'] if b['fill']]
    fl = ''.join(f"<li>Bar {html.escape(n)}: {html.escape(f['scale'])}, {len(f['notes'])} notes into {html.escape(f['into'])}.</li>" for n, f in fills)
    return f"""<h2>How the hands work</h2>
<p>Each chord has one shape for the whole song. When a chord comes back, your hands go back to the same keys.</p>
<p><b>Left hand:</b> a shell, the root with the 7th (or the 5th) above it, low and held with the pedal.</p>
<p><b>Right hand:</b> three notes close together. On 7th and 6th chords the root is left out, because the left hand has it.</p>
<p>The chords are the song’s own, played plainly. The guitar arrangement’s passing chords and colours are left out.</p>
<table><tr><th>Chord</th><th>Left hand</th><th>Right hand, bottom to top</th></tr>{rows}</table>
<h2>The fills</h2>
<p>Only where you rest at the end of a bar, and no more than one in eight bars.</p>
<ul>{fl or '<li>None in this song.</li>'}</ul>
<h2>Practice order</h2>
<ol><li>The {meta['nshapes']} shapes on their own, one hand and then both, until you can find each without looking.</li>
<li>Left hand alone with the track, then right hand alone, then together, slowly.</li>
<li>Sing over it before the fills; add the fills last.</li></ol>"""

def run(slug, audio=True):
    C = charts.chart(slug)
    if slug == 'barquito-de-papel': C['bpm'] = C['bpm'] or 112
    if not C.get('meter'): C['meter'] = 4
    # Songs whose chart has no voice line (the Elvis records): the bars where the singer holds the end
    # of a line, so a short fill can go there.
    held = HELD.get(slug, set())
    for b in C['bars']:
        if b['label'] in held and not b.get('voc'):
            b['voc'] = '█' * (C['meter'] * 2 - 4) + '····'
    vp = voices.pitch(slug)
    log = []
    S = beginner.reduce(C, vp, log=log); beginner.override(slug, S, C)
    C = beginner.to_chart(C, S)
    sung = beginner.Sung(vp) if vp is not None else None
    ar = arrange.Arranger(C)
    seq = []
    for b in C['bars']:
        st, en = b['start'], b['end']; beats = b['beats'] or ar.meter; spb = (en - st) / beats if beats else 60.0 / ar.bpm
        for c in b['chords']:
            seq.append((arrange.simplify(c['c']), st + c['at'] * spb, st + (c['at'] + c['beats']) * spb))
    ar.fixed = ar.fixed_shapes(seq, sung)
    gp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shapes.json')
    if os.path.exists(gp):                      # the shelf's own shape for each chord, the same in every song
        import global_shapes
        G = json.load(open(gp))
        def rubsec(notes, n):
            if sung is None: return 0.0
            c = 0.0
            for m_, t0, t1 in seq:
                if m_ != n: continue
                for v_, sec in sung.notes(t0, t1).items():
                    if any((p_ - v_) in (1, -1, 11, 13, -13) for p_ in notes): c += sec
            return c
        for n in list(ar.fixed):
            g = G.get(global_shapes.key_of(n))
            if not g: continue
            own = ar.fixed[n]
            # the shelf's shape, unless in this song it sits a half step from the singer where the song's own doesn't
            if rubsec(g['lh'] + g['rh'], n) - rubsec(list(own[0]) + list(own[1]), n) > 1.5: continue
            ar.fixed[n] = (g['lh'], g['rh'], g['form'])
    A = ar.run(); limit_tips(A)
    for b in A['bars']:
        if b['n'] in held: b['voc'] = ''
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', slug); os.makedirs(out, exist_ok=True)
    tracks = [('Piano', f'{slug}-piano.mp3', False)]
    length = max(e['off'] for e in A['events']) + 2.5
    if audio:
        x = piano.render(A['events'], length)
        piano.write_mp3(x, os.path.join(out, f'{slug}-piano.mp3'))
        v, kind = voices.stem(slug)
        if v is not None:
            if kind == 'record':
                piano.write_mp3(v, os.path.join(out, f'{slug}-voice.mp3'), peak=0.89, fade=0.5)
                tracks.append(('The record', f'{slug}-voice.mp3.locked', True))
            else:
                n = max(len(v), len(x)); vv = np.zeros((n, 2), np.float32); xx = np.zeros((n, 2), np.float32)
                vv[:len(v)] = v; xx[:len(x)] = x
                r = lambda a: np.sqrt(np.mean(a[np.abs(a[:, 0]) > 1e-3] ** 2)) if np.any(np.abs(a[:, 0]) > 1e-3) else 1
                mix = xx * 0.8 / r(xx) * 0.12 + vv / r(vv) * 0.12
                piano.write_mp3(mix, os.path.join(out, f'{slug}-voice.mp3'))
                tracks.append(('With the singer', f'{slug}-voice.mp3.locked', True))
    elif voices.pair(slug) is not None:
        tracks.append(('With the singer' if voices.pair(slug)[1] else 'The record', f'{slug}-voice.mp3.locked', True))
    if voices.pair(slug) is None and C.get('keep_locked'):
        prev = open(os.path.join('/home/claude/key-finder/songs', slug, 'index.html'), encoding='utf-8').read()
        lab = re.search(r'data-src="' + re.escape(C['keep_locked']) + r'"[^>]*>([^<]*)<', prev)
        tracks.append((html.unescape(lab.group(1)) if lab else 'With the singer', C['keep_locked'], 'keep'))
    key = C.get('key') or ''
    kd = key.replace('b ', '♭ ').replace('# ', '♯ ')
    kd = re.sub(r'^([A-G])b', r'\1♭', kd); kd = re.sub(r'^([A-G])#', r'\1♯', kd)
    nfill = sum(1 for b in A['bars'] if b['fill'])
    nsh = len({(s['c'], tuple(s['lh']), tuple(s['rh'])) for b in A['bars'] for s in b['segs']})
    meta = dict(title=C['title'], key_disp=kd, nshapes=nsh,
                lede=f"For your voice and piano, in {kd or 'the key of the guitar arrangement'}, on the same bars and timing as the guitar arrangement. {nsh} chords, each with one shape that stays the same every time it comes back. The left hand plays the root with the 7th or 5th; the right hand plays three notes close together.",
                facts=[('Key', kd), ('Tempo', f"about {int(round(C['bpm']))} a minute" if C.get('bpm') else 'free'), ('Bars', str(len(A['bars']))), ('Shapes', str(nsh)), ('Fills', str(nfill))],
                credits='Piano sound: Salamander Grand Piano by Alexander Holm (CC BY 3.0). Shells and rootless voicings after Mark Levine, <i>The Jazz Piano Book</i>. Chords from the guitar arrangement.')
    page.build(meta, A, know_html(A, ar, meta), tracks, os.path.join(out, 'index.html'))
    json.dump(dict(slug=slug, title=C['title'], key=kd, source=C.get('source'), tracks=tracks), open(os.path.join(out, 'meta.json'), 'w'), ensure_ascii=False)
    print(slug, 'bars', len(A['bars']), 'shapes', nsh, 'fills', nfill, 'tracks', [t[0] for t in tracks])
    return A

if __name__ == '__main__':
    for s in [a for a in sys.argv[1:] if not a.startswith('--')]:
        run(s, audio='--no-audio' not in sys.argv)
