import sys, json, numpy as np, os
import charts, beginner, voices
NM=['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
def run(slug, cap=beginner.CAP, verbose=True):
    C = json.load(open(f'charts/{slug}.json'))
    vpf = os.path.join(voices.WORK, slug, 'vp.npz')
    vp = dict(np.load(vpf)) if os.path.exists(vpf) else None
    log = []
    S = beginner.reduce(C, vp, cap, log)
    R = beginner.to_chart(C, S)
    v = beginner.report(C, S)
    if verbose:
        print('==', slug, C['key'], 'chords', len(v), sorted(v.items(), key=lambda x: -x[1]))
        sung = beginner.Sung(vp)
        for b0, b1 in zip(C['bars'], R['bars']):
            ns = sung.notes(b1['start'], b1['end'])
            top = sorted(ns.items(), key=lambda x: -x[1])[:4]
            print(f"{b0['label']:>8} {b0['sec'][:8]:8} {' '.join(c['c'] for c in b0['chords']):34} → {' '.join(c['c']+'('+format(c['beats'],'g')+')' for c in b1['chords']):26} | {' '.join(NM[m%12]+str(m//12-1) for m,s in top)}")
    return C, S, R, v
if __name__ == '__main__':
    for s in sys.argv[1:]: run(s)
