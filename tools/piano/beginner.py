"""A beginner's chart: the song's own changes, fewer of them.

From the guitar page's chart (often a reharmonised one, with a new colour on every beat) to the chords a
beginner can learn the song with:
- every chord played plainly: major, minor, 6th, 7th, minor 7th, half-diminished, diminished, sus;
  a slash chord becomes the chord it is over its root (Dm/C is Dm7, C/D is D7sus4);
- one chord per half bar at most (one per bar in a waltz), the passing ones folded into their neighbour
  (a ii–V squeezed into two beats keeps the V);
- one kind of chord per root and family for the whole song (B♭maj7 or B♭6, not both);
- at most CAP different chords: the rarest go first, each time into the chord beside it or the one that
  shares the most notes with it, whichever sits best under what is sung.
The sung pitch (voices.py) decides between close choices; it never adds a chord."""
import re, math
import numpy as np
from arrange import Chord, pc_of, simplify

CAP = 12
NAMES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
NAMES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
KIND_PCS = {'': [0, 4, 7], 'maj7': [0, 4, 7, 11], '6': [0, 4, 7, 9], 'm': [0, 3, 7], 'm7': [0, 3, 7, 10], 'm6': [0, 3, 7, 9],
            '7': [0, 4, 7, 10], '7sus4': [0, 5, 7, 10], 'sus4': [0, 5, 7], 'm7b5': [0, 3, 6, 10], 'dim7': [0, 3, 6, 9]}
GROUP = {'': 'M', 'maj7': 'M', '6': 'M', 'm': 'm', 'm7': 'm', 'm6': 'm', '7': '7', '7sus4': 's', 'sus4': 'M',
         'm7b5': 'h', 'dim7': 'o'}

def root_name(name):
    return re.match(r'^([A-G][#b]?)', name).group(1)

def plain(name):
    """(root name, kind) for a chart chord."""
    name = name.replace('(', '').replace(')', '')
    try:
        ch = Chord(name)
    except Exception:
        return None
    rn = root_name(name); r = ch.root
    f, t, fi, sev, e = ch.family, ch.third, ch.fifth, ch.sev, ch.ext
    if f == 'dim': kind = 'dim7'
    elif f == 'hdim': kind = 'm7b5'
    elif f == 'mmaj': kind = 'm'
    elif f == 'min':
        kind = 'dim7' if fi == 6 and sev is None else 'm7' if sev == 10 else 'm6' if 9 in e else 'm'
    elif f == 'sus': kind = '7sus4'
    elif f == 'sus3' or t == 5: kind = 'sus4'
    elif f == 'dom': kind = '7'
    elif f == 'aug': kind = '7'
    else:
        kind = 'maj7' if sev == 11 else '6' if 9 in e else ''
    if ch.bass != ch.root:
        b = (ch.bass - r) % 12
        pcs = {x % 12 for x in KIND_PCS[kind]}
        if b in pcs: pass
        elif b == 10 and kind in ('', 'm', 'sus4'): kind = {'': '7', 'm': 'm7', 'sus4': '7sus4'}[kind]
        elif b == 11 and kind == '': kind = 'maj7'
        elif b == 10 and kind in ('6', 'm6'): kind = {'6': '7', 'm6': 'm7'}[kind]
        elif b == 2 and kind in ('', 'maj7', '6', 'sus4'):         # C/D: D9sus4
            bn = re.search(r'/([A-G][#b]?)', name).group(1); return (bn, '7sus4')
        elif b == 5 and kind in ('', 'maj7', '6'):                  # G/C: C major 7 (with the 9th)
            bn = re.search(r'/([A-G][#b]?)', name).group(1); return (bn, 'maj7')
        elif b == 9 and kind == 'm7': pass
    return (rn, kind)

def pcs_of(rn, kind):
    r = pc_of(rn)
    return {(r + i) % 12 for i in KIND_PCS[kind]}

def gkey(rn, kind):
    return (pc_of(rn), GROUP[kind])

def name_of(rn, kind):
    return rn + kind

# ---------------------------------------------------------------- the sung notes

class Sung:
    """The sung notes: the median pitch of each quarter second where he sings (a wide vibrato is one note),
    corrected for a record that runs sharp or flat."""
    def __init__(self, vp):
        self.ok = vp is not None
        if not self.ok: return
        t, f0, cf, rm = vp['t'], vp['f0'], vp['conf'], vp['rms']
        thr = 0.12 * np.percentile(rm, 95)
        good = (cf > 0.6) & (rm > thr) & (f0 > 70) & (f0 < 520)
        c = 1200 * np.log2(np.where(good, f0, 440.0) / 440.0)
        W = 0.25; T = []; M = []
        i = 0; n = len(t)
        while i < n:
            j = np.searchsorted(t, t[i] + W)
            g = good[i:j]
            if g.sum() >= 0.6 * max(1, j - i):
                cc = c[i:j][g]
                if np.ptp(np.percentile(cc, [20, 80])) < 160:
                    T.append(t[i]); M.append(np.median(cc))
            i = max(j, i + 1)
        M = np.array(M); T = np.array(T)
        if len(M) > 20:
            ang = 2 * np.pi * (M % 100) / 100; z = np.mean(np.exp(1j * ang))
            self.tune = float(np.angle(z) / (2 * np.pi) * 100) if abs(z) > 0.15 else 0.0
        else: self.tune = 0.0
        self.t = T
        self.m = np.round(69 + (M - self.tune) / 100).astype(int) if len(M) else np.zeros(0, int)
        self.dt = W

    def notes(self, t0, t1):
        """{midi: seconds} sung between t0 and t1 (a note counts once it has lasted a quarter second)."""
        if not self.ok: return {}
        a, b = np.searchsorted(self.t, [t0, t1])
        out = {}
        for m in self.m[a:b]: out[int(m)] = out.get(int(m), 0) + self.dt
        return out

def pc_rub(pcs, sung):
    """Seconds of singing a half step from a chord note without being one (and a sung root under a major 7th)."""
    bad = 0.0; tot = 0.0
    for m, s in sung.items():
        p = m % 12; tot += s
        if p in pcs:
            if (p - 1) % 12 in pcs: bad += s          # a chord note a half step under what is sung (the root under a major 7th)
            continue
        if (p + 1) % 12 in pcs or (p - 1) % 12 in pcs: bad += s
    return bad, tot

def fit(pcs, sung):
    """How well a chord sits under what is sung: seconds on chord notes minus seconds rubbing."""
    good = sum(s for m, s in sung.items() if m % 12 in pcs)
    bad, tot = pc_rub(pcs, sung)
    return good - 2.0 * bad

# ---------------------------------------------------------------- slots

def slots(C):
    """Each bar cut into half bars (one per bar in 3/4), each with the chord that fills most of it."""
    meter = C.get('meter') or 4
    out = []          # [bar index, at, beats, (rn, kind) or None, t0, t1]
    last = None
    for bi, b in enumerate(C['bars']):
        beats = b.get('beats') or meter
        if beats <= 0: beats = meter
        st, en = b['start'], b['end']
        spb = (en - st) / beats
        if meter == 3 or beats < 4: cuts = [0, beats]
        elif beats >= 6 and meter in (6, 12): cuts = [0, beats / 2, beats]
        else: cuts = [0, 2, beats] if beats <= 5 else [0, beats / 2, beats]
        chs = []
        for c in b['chords']:
            p = plain(c['c'])
            if p: chs.append((c['at'], c['at'] + c['beats'], p))
        for a, z in zip(cuts, cuts[1:]):
            ov = {}
            order = []
            for (x0, x1, p) in chs:
                o = max(0.0, min(z, x1) - max(a, x0))
                if o > 0:
                    if p not in ov: order.append(p)
                    ov[p] = ov.get(p, 0) + o
            if not ov:
                pick = last
            else:
                best = max(ov.values())
                tied = [p for p in order if ov[p] >= best - 1e-6]
                span = {p: sum(x1 - x0 for (x0, x1, q) in chs if q == p) for p in tied}
                tied.sort(key=lambda p: -span[p])
                pick = tied[0]
                if len(tied) >= 2:
                    p0, p1 = tied[0], tied[1]
                    # a ii-V in the space of one chord: keep the V
                    if GROUP[p0[1]] in ('m', 'h') and p1[1] in ('7', '7sus4') and (pc_of(p0[0]) - pc_of(p1[0])) % 12 == 7:
                        pick = p1
            out.append(dict(bar=bi, at=a, beats=z - a, ch=pick, t0=st + a * spb, t1=st + z * spb))
            last = pick
    # a song that starts before its first chord: give it the first chord
    first = next((s['ch'] for s in out if s['ch']), None)
    for s in out:
        if s['ch'] is None: s['ch'] = first
        else: break
    return out

# ---------------------------------------------------------------- the reduction

def tonic(C):
    k = (C.get('key') or 'C major').split('/')[-1].strip().split()
    try:
        return pc_of(k[0].replace('♭', 'b').replace('♯', '#')), (len(k) > 1 and k[1].startswith('min'))
    except Exception:
        return 0, False

def reduce(C, vp=None, cap=CAP, log=None):
    S = slots(C)
    sung = Sung(vp)
    for s in S: s['sung'] = sung.notes(s['t0'], s['t1'])
    kpc, minor = tonic(C)
    # a part in another key ("Last A, in E♭") and everything after it: its chords stand apart
    KEYCH = re.compile(r'\bin [A-G][♭♯b#]?\b(?! minor)|\([^)]*\b[A-G][♭♯]? minor\)', re.I)
    reg = 0; region = []
    for s in S:
        if KEYCH.search(C['bars'][s['bar']].get('sec') or ''): reg = 1
        region.append(reg)
    for s, r in zip(S, region): s['region'] = r
    if any(region): cap = cap + 3
    # 1. one kind per root and family: the one that sits best under the voice, else the one most played
    groups = {}
    for s in S:
        rn, kind = s['ch']; groups.setdefault(gkey(rn, kind), []).append(s)
    for g, ss in groups.items():
        kinds = {}
        for s in ss: kinds[s['ch'][1]] = kinds.get(s['ch'][1], 0) + s['beats']
        rn = max(((s['ch'][0], s['beats']) for s in ss), key=lambda x: x[1])[0]
        rn = max({s['ch'][0] for s in ss}, key=lambda n: sum(s['beats'] for s in ss if s['ch'][0] == n))
        def score(k):
            pcs = pcs_of(rn, k)
            f = sum(fit(pcs, s['sung']) for s in ss)
            return f + 0.25 * kinds.get(k, 0)
        cands = [k for k in KIND_PCS if GROUP[k] == g[1]]
        # keep to what the chart uses, plus the 6th for a major 7th (a sung root rubs the 7th)
        use = set(kinds) | ({'6'} if 'maj7' in kinds else set()) | ({'m7'} if 'm6' in kinds else set())
        best = max([k for k in cands if k in use], key=score)
        for s in ss: s['ch'] = (rn, best)
    by_root = {}
    for s in S: by_root.setdefault(pc_of(s['ch'][0]), {}).setdefault(s['ch'], 0); by_root[pc_of(s['ch'][0])][s['ch']] += s['beats']
    for r, d in by_root.items():
        dom = [c for c in d if c[1] == '7']; sus = [c for c in d if c[1] == '7sus4']
        if dom and sus:
            keep = max(dom + sus, key=lambda c: d[c])
            for s in S:
                if s['ch'] in dom + sus: s['ch'] = keep
    # 2. the vocabulary
    def vocab():
        v = {}
        for s in S: v[s['ch']] = v.get(s['ch'], 0) + s['beats']
        return v
    protect = {S[-1]['ch']}
    for s in S:
        if pc_of(s['ch'][0]) == kpc and GROUP[s['ch'][1]] == ('m' if minor else 'M'): protect.add(s['ch'])
    EDGE = re.compile(r'intro|ending|outro|coda|interlude|instrumental|solo|tag|vamp', re.I)
    edge = [bool(EDGE.search(C['bars'][s['bar']].get('sec') or '')) for s in S]
    if all(edge): edge = [False] * len(S)
    while True:
        v = vocab()
        uses = {}
        for i, s in enumerate(S):
            if i == 0 or S[i - 1]['ch'] != s['ch']: uses[s['ch']] = uses.get(s['ch'], 0) + 1
        body = {s['ch'] for s, e in zip(S, edge) if not e}
        weak = [c for c in v if c not in protect]
        if not weak: break
        def prio(c):
            if c not in body: return (0, v[c])                                  # only in the intro or ending
            if (uses[c] == 1 and v[c] <= 2) or (c[1] == 'dim7' and uses[c] <= 3): return (1, v[c])   # passing
            return (2, v[c] + 2 * uses[c])
        w = min(weak, key=prio); pw = prio(w)
        if pw[0] == 2 and len(v) <= cap: break
        if pw[0] < 2 and len(v) <= 6: break
        others_all = [c for c in v if c != w]
        wp = pcs_of(*w); wr = pc_of(w[0])
        changed = False; plan = []
        for i, s in enumerate(S):
            if s['ch'] != w: continue
            prev = next((S[j]['ch'] for j in range(i - 1, -1, -1) if S[j]['ch'] != w), None)
            nxt = next((S[j]['ch'] for j in range(i + 1, len(S)) if S[j]['ch'] != w), None)
            def cost(c):
                cp = pcs_of(*c); cr = pc_of(c[0])
                share = len(cp & wp)
                x = -1.6 * share - 0.9 * fit(cp, s['sung']) / max(0.3, s['t1'] - s['t0'])
                if c == prev: x -= 1.2
                if c == nxt: x -= 0.6
                to_next = nxt is not None and c[1] in ('7', '7sus4') and (cr - pc_of(nxt[0])) % 12 == 7
                if w[1] == '7' and nxt is not None and (wr - pc_of(nxt[0])) % 12 == 1 and to_next: x -= 3.0   # a tritone sub: its V
                elif w[1] == '7' and to_next: x -= 1.0
                if w[1] == 'dim7' and c[1] == '7' and (cr - wr) % 3 == 2: x -= 1.5 + (1.5 if to_next else 0)  # a diminished: the 7♭9 it hides
                if nxt is not None and nxt in protect and pc_of(nxt[0]) == kpc:                              # into the home chord: V, or ii
                    if to_next: x -= 2.0
                    elif c[1] in ('m7', 'm7b5') and (cr - kpc) % 12 == 2: x -= 1.0
                return x
            here = {x['ch'] for x in S if x['region'] == s['region']}
            others = [c for c in others_all if c in here] or others_all
            best = min(others, key=cost)
            plan.append((s, best))
        # a passing chord stays when nothing else sits as well under what is sung there
        if pw[0] < 2:
            dur = lambda s: max(0.3, s['t1'] - s['t0'])
            lose = sum((fit(wp, s['sung']) - fit(pcs_of(*b), s['sung'])) / dur(s) for s, b in plan)
            if lose > 0.25 * len(plan):
                protect.add(w); continue
        for s, best in plan:
            if log is not None: log.append(f"{C['bars'][s['bar']]['label']}: {name_of(*w)} → {name_of(*best)}")
            s['ch'] = best; changed = True
        if not changed: break
    return S

# by hand, where the guitar page's chart is a transcription that wanders: the plain chord in the key
OVERRIDE = {
 'the-christmas-song': {'Cm6': 'Cm7', 'C6': 'C7', 'Fmaj7': 'F7', 'F': 'F7'},
}

# whole bars by hand: {bar label: [chord for each half bar]}
OVERRIDE_BARS = {
 'the-christmas-song': {'1': ['Bb6', 'Bb6'], '2': ['Cm7', 'F7']},      # the intro on the home chord, then ii–V into it
 'i-wonder-whos-kissing-her-now': {'1.24': ['Fm6', 'Fm6'], '2.24': ['Fm6', 'Fm6']},   # Dean holds D on "won-der if": Fm6 has it, Fm7's E♭ rubs
}

def override(slug, S, C=None):
    m = OVERRIDE.get(slug, {})
    for s in S:
        n = name_of(*s['ch'])
        if n in m:
            k = plain(m[n]); s['ch'] = k
    if C is not None:
        for lab, chs in OVERRIDE_BARS.get(slug, {}).items():
            ss = [s for s in S if C['bars'][s['bar']]['label'] == lab]
            for s, c in zip(ss, chs): s['ch'] = plain(c)
    return S

def to_chart(C, S):
    """The chart again, bar by bar, with the beginner's chords."""
    bars = []
    byb = {}
    for s in S: byb.setdefault(s['bar'], []).append(s)
    out = dict(C); out['bars'] = []
    for bi, b in enumerate(C['bars']):
        ch = []
        for s in byb.get(bi, []):
            n = name_of(*s['ch'])
            if ch and ch[-1]['c'] == n: ch[-1]['beats'] += s['beats']
            else: ch.append(dict(c=n, beats=s['beats'], at=s['at']))
        nb = dict(b); nb['chords'] = ch
        out['bars'].append(nb)
    return out

def report(C, S):
    v = {}
    for s in S: v[name_of(*s['ch'])] = v.get(name_of(*s['ch']), 0) + s['beats']
    return v
