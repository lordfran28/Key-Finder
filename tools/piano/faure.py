"""Après un rêve (Fauré, Op. 7 No. 1) for baritone and piano, from the OpenScore Lieder score (CC0).
The piano part is Fauré's own, in A minor (the low-voice key, a minor third down); the voice line is
the A minor line an octave lower, where a baritone sings it. Each bar shows the piano's chords as
keyboard diagrams, one per change; the words (Romain Bussine's poem) sit on top."""
import sys, os, json, re, xml.etree.ElementTree as ET
sys.path.insert(0, '/home/claude/keys')
import arrange, page, piano
import numpy as np

PIANO_SHIFT, VOICE_SHIFT, BPM = -3, -15, 54
STEP = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
root = ET.parse(os.path.join(os.path.dirname(__file__), 'score.xml')).getroot()

def read(part):
    notes = []; lyr = {}; div = 1; mstart = 0.0; mlen = 3.0; starts = []
    for m in part.findall('measure'):
        n = int(re.sub(r'\D', '', m.get('number')) or 0)
        starts.append((n, mstart)); pos = 0.0; last_on = 0.0; mx = 0.0
        for el in m:
            if el.tag == 'attributes':
                d = el.findtext('divisions')
                if d: div = int(d)
                b = el.find('time')
                if b is not None: mlen = int(b.findtext('beats')) * 4 / int(b.findtext('beat-type'))
            elif el.tag == 'backup': pos -= int(el.findtext('duration')) / div
            elif el.tag == 'forward': pos += int(el.findtext('duration')) / div
            elif el.tag == 'note':
                dur = int(el.findtext('duration') or 0) / div
                if el.find('grace') is not None: continue
                chord = el.find('chord') is not None
                on = last_on if chord else pos
                if not chord: last_on = pos; pos += dur
                mx = max(mx, pos)
                p = el.find('pitch')
                if p is None: continue
                midi = 12 * (int(p.findtext('octave')) + 1) + STEP[p.findtext('step')] + int(float(p.findtext('alter') or 0))
                tie = [t.get('type') for t in el.findall('tie')]
                staff = int(el.findtext('staff') or 1)
                notes.append(dict(m=n, t=mstart + on, d=dur, midi=midi, staff=staff, tie=tie))
                for ly in [l for l in el.findall('lyric') if l.get('number', '1') == '1']:
                    tx = ly.findtext('text') or ''; sy = ly.findtext('syllabic') or 'single'
                    lyr.setdefault(n, []).append((tx, sy))
        mstart += mlen
    # join ties
    out = []; open_ = {}
    for x in sorted(notes, key=lambda x: (x['t'], x['midi'])):
        k = (x['midi'], x['staff'])
        if 'stop' in x['tie'] and k in open_:
            open_[k]['d'] = x['t'] + x['d'] - open_[k]['t']
            if 'start' not in x['tie']: del open_[k]
            continue
        out.append(x)
        if 'start' in x['tie']: open_[k] = x
    return out, lyr, starts, mstart

parts = root.findall('part')
voice, lyr, starts, total = read(parts[0])
pno, _, _, _ = read(parts[1])
spq = 60.0 / BPM
def words(n):
    s = ''; items = [(tx.replace('\xa0', ' ').strip().lstrip('–- ').strip(), sy) for tx, sy in lyr.get(n, [])]
    items = [(tx, sy) for tx, sy in items if tx and tx not in ('–', '-', '_')]
    for i, (tx, sy) in enumerate(items):
        s += tx + ('' if sy in ('begin', 'middle') else ' ')
    if items and items[-1][1] in ('begin', 'middle'): s = s.rstrip() + '-'
    if items and items[0][1] in ('middle', 'end'): s = '-' + s
    return s.strip()

ar = arrange.Arranger(dict(key='A minor', bpm=BPM, meter=3, bars=[])); ar.N = ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'B♭', 'B']; ar.flats = False
SECS = [(1, 'Introduction and first verse'), (16, 'Second verse'), (29, 'Third verse'), (41, 'Last lines')]
def sec_of(n): return [s for a, s in SECS if n >= a][-1]

TEMPL = [('', [0, 4, 7]), ('m', [0, 3, 7]), ('7', [0, 4, 7, 10]), ('m7', [0, 3, 7, 10]), ('maj7', [0, 4, 7, 11]), ('dim7', [0, 3, 6, 9]),
         ('m7b5', [0, 3, 6, 10]), ('aug', [0, 4, 8]), ('dim', [0, 3, 6]), ('7b9', [0, 4, 7, 10, 1]), ('m(maj7)', [0, 3, 7, 11]), ('9', [0, 4, 7, 10, 2]), ('7sus4', [0, 5, 7, 10]), ('9sus4', [0, 5, 10, 2]), ('7sus4b9', [0, 5, 7, 10, 1])]
def name_for(pcs, bass):
    best = None
    for r in range(12):
        for q, iv in TEMPL:
            s = {(r + i) % 12 for i in iv}
            sc = len(s & pcs) * 2 - len(s - pcs) * 1.5 - len(pcs - s) * 2 + (0.6 if r == bass else 0) + (0.2 if len(iv) == 3 else 0)
            if best is None or sc > best[0]: best = (sc, r, q)
    _, r, q = best
    nm = ar.N[r].replace('♭', 'b').replace('♯', '#') + q
    if bass != r: nm += '/' + ar.N[bass].replace('♭', 'b').replace('♯', '#')
    return nm

bars = []; events = []; uid = 0
mst = dict(starts)
for n, st in starts:
    beats = []
    for b in range(3):
        a, z = st + b, st + b + 1
        on = [x for x in pno if a - 1e-6 <= x['t'] < z - 1e-6]
        snd = [x for x in pno if x['t'] < z - 1e-6 and x['t'] + x['d'] > a + 1e-6]
        L = sorted({x['midi'] + PIANO_SHIFT for x in snd if x['staff'] == 2})
        R = sorted({x['midi'] + PIANO_SHIFT for x in (on if any(y['staff'] == 1 for y in on) else snd) if x['staff'] == 1})
        beats.append((tuple(L), tuple(R)))
    segs = []; at = 0
    for i, bt in enumerate(beats):
        if segs and segs[-1]['_k'] == bt: segs[-1]['beats'] += 1
        else: segs.append(dict(_k=bt, beats=1, at=i))
    out = []
    for s in segs:
        L, R = map(list, s['_k'])
        if not L and not R: continue
        allp = L + R; bass = (min(L) if L else min(R)) % 12
        nm = name_for({p % 12 for p in allp}, bass)
        try: ch = arrange.Chord(nm)
        except Exception: ch = arrange.Chord(ar.N[bass].replace('♭', 'b').replace('♯', '#'))
        uid += 1
        out.append(dict(id=f's{uid}', c=arrange.disp(nm), beats=s['beats'], at=s['at'], lh=L, rh=R, form='Fauré’s chord',
                        tones={str(m): arrange.tone_label(ch, m) for m in allp}, same=None, tip=None, names=[ar.nn(m) for m in L + R]))
    bars.append(dict(n=str(n), sec=sec_of(n), start=round(st * spq + 0.5, 3), end=round((st + 3) * spq + 0.5, 3), voc='', words=words(n), segs=out, fill=None))
# one diagram per change: a chord already drawn in this part is named
seen = {}; part = None
for b in bars:
    if b['sec'] != part: part = b['sec']; seen = {}
    for s in b['segs']:
        k = (tuple(s['lh']), tuple(s['rh']))
        if k in seen: s['same'] = seen[k]
        else: seen[k] = s['id']
# events: every piano note as Fauré wrote it, on its diagram
for b in bars:
    for x in pno:
        pass
seg_at = []
for b in bars:
    st = float(b['start'])
    for s in b['segs']:
        seg_at.append((st + s['at'] * spq, st + (s['at'] + s['beats']) * spq, s))
for x in pno:
    t = x['t'] * spq + 0.5; m = x['midi'] + PIANO_SHIFT
    sg = next((s for a, z, s in seg_at if a - 1e-3 <= t < z - 1e-3), None)
    events.append(dict(t=t, midi=m, vel=0.5 if x['staff'] == 1 else 0.58, off=t + x['d'] * spq, hand='R' if x['staff'] == 1 else 'L', seg=sg['id'] if sg else ''))
tune = [dict(t=x['t'] * spq + 0.5, midi=x['midi'] + VOICE_SHIFT, vel=0.72, off=(x['t'] + x['d']) * spq + 0.5) for x in voice]
A = dict(bars=bars, events=events)
out = '/home/claude/keys/out/apres-un-reve'; os.makedirs(out, exist_ok=True)
length = total * spq + 4
if '--no-audio' not in sys.argv:
    x = piano.render(events, length); piano.write_mp3(x, f'{out}/apres-un-reve-piano.mp3')
    y = piano.render(tune, length)
    n = min(len(x), len(y)); mix = x[:n] * 0.75 + y[:n] * 1.15
    piano.write_mp3(mix, f'{out}/apres-un-reve-tune.mp3')
know = """<h2>About this song</h2>
<p>Gabriel Fauré wrote <i>Après un rêve</i> around 1877 to a poem by Romain Bussine, after an anonymous Tuscan poem. It is the first of his Three Songs, Op. 7, published in 1878. The words: a sleeper dreams of the one he loves, they fly toward the light together, and he wakes and begs the night to give the dream back.</p>
<h2>How the piano part works</h2>
<p>The right hand repeats each chord in three even notes to the beat (triplets), soft and steady, while the left hand holds the bass, often walking down by step. The singer floats over it in long, slow phrases. Keep the right hand light and even, and let the left hand carry the line.</p>
<p>The page shows Fauré's notes exactly, moved down a minor third from his C minor into A minor, the key of the low-voice editions. Each diagram is a chord as it sounds for one or more beats; play its right-hand notes as the three repeated notes of each beat.</p>
<h2>What to listen for</h2>
<ul><li>The bass falls by half steps under the first lines: each new chord is only one key away from the last.</li>
<li>Many chords are seventh chords that lean on the next one (dominant sevenths and their relatives): that's what gives the song its endless, dreaming pull.</li>
<li>At the climax, the voice reaches its highest note while the piano grows; then everything falls back to the quiet opening chord.</li></ul>
<h2>Practice order</h2>
<ol><li>Left hand alone with the track, one part at a time.</li><li>Right hand alone, slowly, as plain chords on the beat; then in triplets.</li><li>Together, then sing over it with the "Piano and the tune" track until you know the line.</li></ol>"""
meta = dict(title='Après un rêve', key_disp='A minor',
            lede='Fauré’s own piano part, a minor third down in A minor, the key of the low-voice editions; you sing the line an octave below what is written there. Every chord is shown as it sits under the hands, with Romain Bussine’s words above.',
            facts=[('Key', 'A minor'), ('Tempo', f'Andantino, about {BPM} a minute'), ('Bars', str(len(bars))), ('Words', 'Romain Bussine')],
            credits='Score: OpenScore Lieder (CC0), from the first edition. Piano sound: Salamander Grand Piano by Alexander Holm (CC BY 3.0).')
page.build(meta, A, know, [('Piano', 'apres-un-reve-piano.mp3', False), ('Piano and the tune', 'apres-un-reve-tune.mp3', False)], f'{out}/index.html')
json.dump(dict(slug='apres-un-reve', title='Fauré – Après un rêve', key='A minor', source='https://musescore.com/openscore-lieder-corpus/scores/6810863', tracks=[]), open(f'{out}/meta.json', 'w'), ensure_ascii=False)
print('bars', len(bars), 'segs', sum(len(b['segs']) for b in bars), 'named', sum(1 for b in bars for s in b['segs'] if s['same']), 'voice range', min(x['midi'] for x in tune), max(x['midi'] for x in tune))
print([ (b['n'], [s['c'] for s in b['segs']], b['words']) for b in bars[:8]])
