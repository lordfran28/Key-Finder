"""Half-step rubs between the piano and the singer, from a built page: python3 rubs.py SLUG [page.html]"""
import sys, os, re, json, numpy as np
import beginner, voices
NM = ['C','C♯','D','E♭','E','F','F♯','G','A♭','A','B♭','B']
def check(slug, path=None, show=8):
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', slug, 'index.html')
    s = open(path, encoding='utf-8').read()
    D = json.loads(re.search(r'<script id="kf-data" type="application/json">(.*?)</script>', s, re.S).group(1))
    vp = voices.pitch(slug)
    if vp is None: return None
    S = beginner.Sung(vp)
    bad = {}; tot_s = 0.0
    seg_bar = {g['id']: b['n'] for b in D['bars'] for g in b['segs']}
    for b in D['bars']:
        for x in (b.get('fill') or {}).get('id', ''), : seg_bar[x] = b['n']
    for t, m, hand, off, seg in D['events']:
        off = min(off, t + 2.0)
        for v, sec in S.notes(t, off).items():
            if (m - v) in (1, -1, 11, 13, -13):
                k = (seg_bar.get(seg, '?'), NM[m % 12] + str(m // 12 - 1), NM[v % 12] + str(v // 12 - 1))
                bad[k] = bad.get(k, 0) + sec
    sung_total = len(S.m) * S.dt
    tot = sum(bad.values())
    worst = sorted(bad.items(), key=lambda x: -x[1])[:show]
    return tot, sung_total, worst
if __name__ == '__main__':
    r = check(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    if r: print('rub seconds %.1f of %.0f sung' % (r[0], r[1])); [print('  bar', k[0], 'piano', k[1], 'voice', k[2], '%.2f s' % v) for k, v in r[2]]
