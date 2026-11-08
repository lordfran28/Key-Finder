"""Après un rêve for a beginner: Fauré's harmony read from the score (faure.py), one chord a bar or so,
each chord one shape, played as Fauré's right hand plays: three soft repeated notes to the beat.
python3 faure_beginner.py [--no-audio]   (needs score.xml from the OpenScore Lieder corpus beside faure.py)"""
import sys, os, json, types
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import arrange, page, piano, beginner, build
SCORE_DIR = '/home/claude/keys/faure'

def score():
    src = open(os.path.join(HERE, 'faure.py'), encoding='utf-8').read()
    src = src[:src.index('A = dict(bars=bars, events=events)')]
    src = src.replace("sys.path.insert(0, '/home/claude/keys')\n", '')
    src = src.replace("os.path.join(os.path.dirname(__file__), 'score.xml')", repr(os.path.join(SCORE_DIR, 'score.xml')))
    ns = {'__name__': 'faure_score'}
    exec(compile(src, 'faure.py', 'exec'), ns)
    return ns

def run(audio=True):
    F = score()
    bars = F['bars']; spq = F['spq']
    C = dict(key='A minor', bpm=F['BPM'], meter=3, title='Fauré – Après un rêve', slug='apres-un-reve', words_free=True, bars=[])
    for b in bars:
        ch = [dict(c=s['c'].replace('♭', 'b').replace('♯', '#').replace('°', 'dim'), beats=float(s['beats']), at=float(s['at'])) for s in b['segs']]
        C['bars'].append(dict(label=b['n'], sec=b['sec'], start=b['start'], end=b['end'], chords=ch, beats=3, voc='', mel=[], words=b['words']))
    log = []
    S = beginner.reduce(C, None, log=log)
    R = beginner.to_chart(C, S)
    ar = arrange.Arranger(R); ar.N = arrange.SHARPN; ar.flats = False
    seq = []
    for b in R['bars']:
        st, en = b['start'], b['end']; spb = (en - st) / 3
        for c in b['chords']: seq.append((arrange.simplify(c['c']), st + c['at'] * spb, st + (c['at'] + c['beats']) * spb))
    ar.fixed = ar.fixed_shapes(seq, None)
    gp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shapes.json')
    if os.path.exists(gp):                      # the shelf's own shape for each chord, the same in every song
        import global_shapes
        G = json.load(open(gp))
        for n in list(ar.fixed):
            g = G.get(global_shapes.key_of(n))
            if g: ar.fixed[n] = (g['lh'], g['rh'], g['form'])
    A = ar.run()
    # Fauré's right hand: three repeated notes to every beat, the left hand held
    ev = []
    for e in A['events']:
        if e['hand'] != 'R': ev.append(e); continue
    for b in R['bars']:
        st, en = b['start'], b['end']; spb = (en - st) / 3
        for sgi, c in enumerate(b['chords']):
            seg = next(s for bb in A['bars'] if bb['n'] == b['label'] for s in bb['segs'] if s['at'] == c['at'])
            for k in range(int(round(c['beats'] * 3))):
                t = st + c['at'] * spb + k * spb / 3
                for j, m in enumerate(seg['rh']):
                    ev.append(dict(t=t + 0.006 * j, midi=m, vel=0.36 + (0.06 if k % 3 == 0 else 0), off=t + spb / 3 * 0.95, hand='R', seg=seg['id']))
    A['events'] = sorted(ev, key=lambda e: e['t'])
    build.limit_tips(A)
    for bb in A['bars']: bb['words'] = next(b['words'] for b in bars if b['n'] == bb['n'])
    out = os.path.join(HERE, 'out', 'apres-un-reve'); os.makedirs(out, exist_ok=True)
    tune = F['tune']
    length = max(max(e['off'] for e in A['events']), max(x['off'] for x in tune)) + 3
    if audio:
        x = piano.render(A['events'], length); piano.write_mp3(x, f'{out}/apres-un-reve-piano.mp3')
        y = piano.render(tune, length)
        n = min(len(x), len(y)); piano.write_mp3(x[:n] * 0.75 + y[:n] * 1.15, f'{out}/apres-un-reve-tune.mp3')
    nsh = len({(s['c'], tuple(s['lh']), tuple(s['rh'])) for b in A['bars'] for s in b['segs']})
    know = build.know_html(A, ar, dict(nshapes=nsh)).replace('The guitar arrangement’s passing chords and colours are left out.', 'Fauré’s passing chords are left out; his right hand’s three soft notes to the beat are kept.')
    meta = dict(title='Après un rêve', key_disp='A minor', nshapes=nsh,
                lede=f'Fauré’s harmony, a minor third down in A minor, the key of the low-voice editions; you sing the line an octave below what is written there. {nsh} chords, each with one shape that stays the same every time it comes back, played as Fauré’s right hand plays them: three soft notes to the beat. Romain Bussine’s words are above.',
                facts=[('Key', 'A minor'), ('Tempo', f"Andantino, about {F['BPM']} a minute"), ('Bars', str(len(A['bars']))), ('Shapes', str(nsh)), ('Words', 'Romain Bussine')],
                credits='Score: OpenScore Lieder (CC0), from the first edition. Piano sound: Salamander Grand Piano by Alexander Holm (CC BY 3.0).')
    page.build(meta, A, know, [('Piano', 'apres-un-reve-piano.mp3', False), ('Piano and the tune', 'apres-un-reve-tune.mp3', False)], f'{out}/index.html')
    json.dump(dict(slug='apres-un-reve', title='Fauré – Après un rêve', key='A minor', source='https://musescore.com/openscore-lieder-corpus/scores/6810863',
                   tracks=[('Piano', 'apres-un-reve-piano.mp3', False), ('Piano and the tune', 'apres-un-reve-tune.mp3', False)]), open(f'{out}/meta.json', 'w'), ensure_ascii=False)
    v = beginner.report(C, S)
    print('apres-un-reve bars', len(A['bars']), 'shapes', nsh, sorted(v, key=lambda k: -v[k]))
    print('\n'.join(log[:40]))
    for b in R['bars']: print(b['label'], ' '.join(c['c'] for c in b['chords']), end=' | ')

if __name__ == '__main__':
    run('--no-audio' not in sys.argv)
