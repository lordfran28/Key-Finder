"""One shape per chord for every song on the shelf: E7 is the same keys in every song, so a shape learned
in one song is already known in the next.  python3 global_shapes.py  (writes shapes.json, which
build.py and faure_beginner.py use).
The shape for each chord is the one that, over all the songs together, moves least from the chords
around it, sits in the middle of the keyboard, and keeps off a half step from what is sung."""
import os, sys, json, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import charts, beginner, voices, arrange

def key_of(name):
    ch = arrange.Chord(name)
    m = re.match(r'^[A-G][#b]?(.*?)(/[A-G][#b]?)?$', name)
    return f"{ch.root}:{m.group(1)}:{ch.bass}"

def song_seq(slug):
    C = charts.chart(slug)
    if slug == 'barquito-de-papel': C['bpm'] = C['bpm'] or 112
    if not C.get('meter'): C['meter'] = 4
    vp = voices.pitch(slug)
    S = beginner.reduce(C, vp); beginner.override(slug, S, C)
    R = beginner.to_chart(C, S)
    sung = beginner.Sung(vp) if vp is not None else None
    meter = R.get('meter') or 4; bpm = R.get('bpm') or 80
    seq = []
    for b in R['bars']:
        st, en = b['start'], b['end']; beats = b['beats'] or meter; spb = (en - st) / beats if beats else 60.0 / bpm
        for c in b['chords']: seq.append((arrange.simplify(c['c']), st + c['at'] * spb, st + (c['at'] + c['beats']) * spb))
    return seq, sung

def apres_seq():
    import faure_beginner
    F = faure_beginner.score()
    C = dict(key='A minor', bpm=F['BPM'], meter=3, bars=[])
    for b in F['bars']:
        ch = [dict(c=s['c'].replace('♭', 'b').replace('♯', '#').replace('°', 'dim'), beats=float(s['beats']), at=float(s['at'])) for s in b['segs']]
        C['bars'].append(dict(label=b['n'], sec=b['sec'], start=b['start'], end=b['end'], chords=ch, beats=3, voc='', mel=[], words=b['words']))
    R = beginner.to_chart(C, beginner.reduce(C, None))
    seq = []
    for b in R['bars']:
        st, en = b['start'], b['end']; spb = (en - st) / 3
        for c in b['chords']: seq.append((arrange.simplify(c['c']), st + c['at'] * spb, st + (c['at'] + c['beats']) * spb))
    return seq, None

def main():
    songs = {s: song_seq(s) for s in charts.SONGS}
    songs['apres-un-reve'] = apres_seq()
    ar = arrange.Arranger(dict(key='C major', bars=[]))
    info = {}
    for slug, (seq, sung) in songs.items():
        for n, _, _ in seq:
            k = key_of(n)
            if k not in info:
                opts, form = ar.shape_options(arrange.Chord(n))
                info[k] = dict(name=n, opts=opts, form=form, own=[0.0] * len(opts), occ=0)
    def rub(notes, sung, t0, t1):
        if sung is None: return 0.0
        c = 0.0
        for m, sec in sung.notes(t0, t1).items():
            for p in notes:
                if (p - m) in (1, -1, 11, 13, -13): c += sec; break
        return c
    pairs = {}
    for slug, (seq, sung) in songs.items():
        for n, t0, t1 in seq:
            I = info[key_of(n)]; I['occ'] += 1
            for i, (lh, v, pen) in enumerate(I['opts']): I['own'][i] += 6.0 * rub(lh + v, sung, t0, t1)
        for (a, _, _), (b, _, _) in zip(seq, seq[1:]):
            ka, kb = key_of(a), key_of(b)
            if ka != kb: pairs[(ka, kb)] = pairs.get((ka, kb), 0) + 1
    for k, I in info.items():
        for i, (lh, v, pen) in enumerate(I['opts']):
            I['own'][i] += (0.6 * abs(sum(v) / len(v) - 63) + 1.5 * max(0, v[-1] - 72) + 1.0 * max(0, 58 - v[0])) * max(1, I['occ'] ** 0.5) * 2 + pen * I['occ']
    choice = {k: min(range(len(I['own'])), key=lambda i: I['own'][i]) for k, I in info.items()}
    def move(u, v):
        u, v = sorted(u), sorted(v)
        if len(u) != len(v): return sum(min(abs(x - y) for y in v) for x in u)
        return sum(abs(x - y) for x, y in zip(u, v))
    nb = {}
    for (a, b), w in pairs.items():
        nb.setdefault(a, []).append((b, w, 0)); nb.setdefault(b, []).append((a, w, 1))
    for it in range(15):
        changed = 0
        for k, I in info.items():
            def tot(i):
                lh, v, _ = I['opts'][i]; c = I['own'][i]
                for o, w, _ in nb.get(k, []):
                    ol, ov, _ = info[o]['opts'][choice[o]]
                    c += w * (move(v, ov) + 0.3 * abs(lh[0] - ol[0]))
                return c
            i = min(range(len(I['opts'])), key=tot)
            if i != choice[k]: choice[k] = i; changed += 1
        if not changed: break
    out = {}
    for k, I in info.items():
        lh, v, _ = I['opts'][choice[k]]
        iv = [x - lh[0] for x in lh]
        left = 'Root' if len(lh) == 1 else 'Shell' if iv[1] in (9, 10, 11) else 'Root and 5th'
        form = left + ' + ' + I['form'].split(' + ', 1)[1] if ' + ' in I['form'] else I['form']
        out[k] = dict(name=I['name'], lh=lh, rh=v, form=form, occ=I['occ'])
    os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, 'shapes.json'), 'w'), ensure_ascii=False, indent=0)
    print(len(out), 'chords', 'iterations', it + 1)

if __name__ == '__main__':
    main()
