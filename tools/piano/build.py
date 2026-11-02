"""Build one voice-and-piano song: arrangement, piano track, the singer over the piano, the page.
    python3 build.py SLUG [--no-audio]"""
import sys, os, json, re, html, subprocess
import numpy as np, scipy.io.wavfile as w
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charts, arrange, page, piano

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
 ('Major chords', 'maj7, maj9, 6/9', '3 · 5 · 7 · 9', '7 · 9 · 3 · 5', 'On the home chord the 7 becomes a 6 (3 · 5 · 6 · 9): the sixth never fights a sung root.'),
 ('Minor chords', 'm7, m9, m6', '♭3 · 5 · ♭7 · 9', '♭7 · 9 · ♭3 · 5', 'For a minor 6 chord the ♭7 becomes a 6.'),
 ('Dominant chords', '7, 9, 13', '3 · 13 · ♭7 · 9', '♭7 · 9 · 3 · 13', 'When the chord leads to a minor chord, the 9 and 13 drop a half step (♭9, ♭13): darker, and it pulls harder.'),
]

HELD = {
    'love-me-tender': {'V2.4', 'C1.4', 'V3.4', 'End 2'},
    'are-you-lonesome-tonight': {'k17', 'k23', 'E2'},
}

def know_html(A, ar, meta):
    fams = set()
    for b in A['bars']:
        for s in b['segs']:
            f = s['form']
            fams.add('dim' if 'diminished' in f else s['c'])
    rows = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d, e in FAMS)
    notes = ''.join(f'<li>{e}</li>' for a, b, c, d, e in FAMS)
    fills = [(b['n'], b['fill']) for b in A['bars'] if b['fill']]
    fl = ''.join(f"<li>Bar {html.escape(n)}: {html.escape(f['scale'])}, {len(f['notes'])} notes into {html.escape(f['into'])}.</li>" for n, f in fills)
    nA = sum(1 for b in A['bars'] for s in b['segs'] if 'A form' in s['form'] and not s['same'])
    nB = sum(1 for b in A['bars'] for s in b['segs'] if 'B form' in s['form'] and not s['same'])
    return f"""<h2>How the hands work</h2>
<p><b>Left hand:</b> the bass note of each chord, low, held with the pedal. On long chords in slow passages it adds the fifth above. On a slash chord (D/F♯) it plays the note after the slash.</p>
<p><b>Right hand:</b> four notes without the root, because the left hand already has it. Every chord type has two shapes. The A shape has the 3rd at the bottom, the B shape has the 7th at the bottom. Going from one chord to the next you usually switch between them, and then most fingers stay where they are or move one key. This song uses the A shape {nA} times and the B shape {nB} times.</p>
<table><tr><th>Chord</th><th>Written</th><th>A shape, bottom to top</th><th>B shape</th></tr>{rows}</table>
<ul>{notes}</ul>
<h2>The fills</h2>
<p>Only where you rest at the end of a bar. Each one walks the scale of the chord it's on and stops a step away from the top note of the next chord, so that note feels like an arrival.</p>
<ul>{fl or '<li>None in this song.</li>'}</ul>
<h2>Practice order</h2>
<ol><li>Learn the shapes at the bottom of the page one chord type at a time: say the numbers as you play them.</li>
<li>Take one part. Left hand alone with the track, then right hand alone, then together slowly.</li>
<li>Sing over it before the fills; add the fills last, when the chords are in your hands.</li></ol>"""

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
    ar = arrange.Arranger(C); A = ar.run(); limit_tips(A)
    for b in A['bars']:
        if b['n'] in held: b['voc'] = ''
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', slug); os.makedirs(out, exist_ok=True)
    tracks = [('Piano', f'{slug}-piano.mp3', False)]
    length = max(e['off'] for e in A['events']) + 2.5
    if audio:
        x = piano.render(A['events'], length)
        piano.write_mp3(x, os.path.join(out, f'{slug}-piano.mp3'))
        if C.get('voice'):
            v, kind = voice_stem(C['voice'], C.get('guitar'))
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
    elif C.get('voice'):
        tracks.append(('With the singer' if C.get('guitar') else 'The record', f'{slug}-voice.mp3.locked', True))
    key = C.get('key') or ''
    kd = key.replace('b ', '♭ ').replace('# ', '♯ ')
    kd = re.sub(r'^([A-G])b', r'\1♭', kd); kd = re.sub(r'^([A-G])#', r'\1♯', kd)
    nfill = sum(1 for b in A['bars'] if b['fill'])
    meta = dict(title=C['title'], key_disp=kd,
                lede=f"For your voice and piano, in {kd or 'the key of the guitar arrangement'}, on the same bars and timing as the guitar arrangement. The left hand plays the bass; the right hand plays four-note shapes without the root that move as little as possible from chord to chord.",
                facts=[('Key', kd), ('Tempo', f"about {int(round(C['bpm']))} a minute" if C.get('bpm') else 'free'), ('Bars', str(len(A['bars']))), ('Fills', str(nfill))],
                credits='Piano sound: Salamander Grand Piano by Alexander Holm (CC BY 3.0). Voicings after Mark Levine, <i>The Jazz Piano Book</i>, and Phil DeGreg, <i>Jazz Keyboard Harmony</i>. Chords from the guitar arrangement.')
    page.build(meta, A, know_html(A, ar, meta), tracks, os.path.join(out, 'index.html'))
    json.dump(dict(slug=slug, title=C['title'], key=kd, source=C.get('source'), tracks=tracks), open(os.path.join(out, 'meta.json'), 'w'), ensure_ascii=False)
    print(slug, 'bars', len(A['bars']), 'fills', nfill, 'tracks', [t[0] for t in tracks])

if __name__ == '__main__':
    for s in [a for a in sys.argv[1:] if not a.startswith('--')]:
        run(s, audio='--no-audio' not in sys.argv)
