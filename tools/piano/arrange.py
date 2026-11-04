"""Baritone voice and piano for a beginner: an arrangement from a chord chart.

The chords are the song's own, played plainly: triads, sixths and sevenths, with the 9ths, 11ths, 13ths
and altered colours left out (a sus, a raised or lowered 5th and the bass under a slash chord stay,
because they are the sound of the song). On a major 7th chord where the voice sings the root, the 7th
becomes a 6th, so nothing rubs against the voice.
Left hand: a shell, the root with the 7th (or the 6th or 5th) above it; under a slash chord, the bass alone.
Right hand: three notes close together, without the root on seventh and sixth chords (rootless), a plain
triad on triads. Of the three or four ways to stack them it takes the one nearest the last, so most fingers
stay put. Now and then a fourth note for a fuller sound: where a part starts or ends, on the
last chord, and on a long chord while the voice rests, at most once in four bars.
A short fill only where the voice rests at the end of a bar, at most one in eight bars.
"""
import re, json, math

NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
FLATN = ['C', 'D♭', 'D', 'E♭', 'E', 'F', 'G♭', 'G', 'A♭', 'A', 'B♭', 'B']
SHARPN = ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B']

def pc_of(s):
    return (NOTE[s[0]] + (1 if s[1:2] == '#' else -1 if s[1:2] == 'b' else 0)) % 12

class Chord:
    def __init__(self, name):
        self.name = name
        n = name.replace('6/9', '69').replace('(', '').replace(')', '').replace(' ', '')
        m = re.match(r'^([A-G][#b]?)(.*?)(?:/([A-G][#b]?))?$', n)
        if not m: raise ValueError(name)
        self.root = pc_of(m.group(1)); q = m.group(2); self.bass = pc_of(m.group(3)) if m.group(3) else self.root
        self.q = q
        third, fifth, sev, ext = 4, 7, None, set()
        qq = q
        dim = qq.startswith('dim') or qq.startswith('o')
        if dim:
            third, fifth = 3, 6; sev = 9 if '7' in qq else None
            self.family = 'dim'
        else:
            if qq.startswith('maj') or qq.startswith('M'):
                self.family = 'maj'; qq = re.sub(r'^(maj|M)', '', qq); sev = 11
            elif qq.startswith('m') and not qq.startswith('maj'):
                third = 3; qq = qq[1:]
                if qq.startswith('maj') or qq.startswith('M'):
                    sev = 11; qq = re.sub(r'^(maj|M)', '', qq); self.family = 'mmaj'
                else:
                    self.family = 'min'
            elif qq.startswith('aug') or qq.startswith('+'):
                fifth = 8; qq = re.sub(r'^(aug|\+)', '', qq); self.family = 'aug'
            else:
                self.family = 'maj'
            # numbers
            mm = re.match(r'^(69|13|11|9|7|6)?(.*)$', qq)
            num, rest = mm.group(1), mm.group(2)
            if num == '69': ext |= {9, 14}
            elif num == '6': ext.add(9)
            elif num in ('7', '9', '11', '13'):
                if sev is None: sev = 10
                if num in ('9', '11', '13'): ext.add(14)
                if num == '11': ext.add(17)
                if num == '13': ext.add(21)
            if self.family == 'maj' and sev == 10: self.family = 'dom'
            if self.family == 'aug' and sev == 10: self.family = 'dom'
            if 'sus4' in rest or rest.startswith('sus') and 'sus2' not in rest: third = 5; self.family = 'sus' if sev == 10 or self.family == 'dom' else 'sus3'
            if 'sus2' in rest: third = 2
            if 'no3' in rest: third = None
            for a in re.findall(r'(add\d+|[b#]\d+)', rest):
                if a == 'add9': ext.add(14)
                elif a == 'add11': ext.add(17)
                elif a == 'b5': fifth = 6
                elif a == '#5': fifth = 8
                elif a == 'b9': ext.discard(14); ext.add(13)
                elif a == '#9': ext.discard(14); ext.add(15)
                elif a == '#11': ext.add(18)
                elif a == 'b13': ext.add(20)
                elif a == '13': ext.add(21)
                elif a == '9': ext.add(14)
            if self.family == 'min' and fifth == 6 and sev == 10: self.family = 'hdim'
        self.third, self.fifth, self.sev, self.ext = third, fifth, sev, ext

    def pcs(self):
        s = {0, self.fifth}
        if self.third is not None: s.add(self.third)
        if self.sev is not None: s.add(self.sev)
        s |= {e % 12 for e in self.ext}
        return {(self.root + i) % 12 for i in s}

    def shapes(self, home=False, to_minor=False):
        """RH rootless shapes as intervals above the root, with a name."""
        f, t, fi = self.family, self.third, self.fifth
        e = self.ext
        if f == 'dim':
            return [('diminished', [3, 6, 9, 12]), ('diminished', [6, 9, 12, 15]), ('diminished', [9, 12, 15, 18])]
        if f in ('maj', 'aug', 'sus3'):
            if self.sev == 11:
                top5 = 18 if 18 in e else 19
                five = 6 if 18 in e else fi
                if fi == 8: five, top5 = 8, 20
                return [('A form', [t, five, 11, 14]), ('B form', [11, 14, t + 12, top5])]
            if 9 in e or home or self.sev is None:
                if f == 'aug' and self.sev is None: return [('augmented', [t, 8, 12]), ('augmented', [8, 12, 16])]
                if t == 5:  return [('sus', [5, 7, 14]), ('sus', [7, 14, 17])]
                return [('6/9, A form', [t, 9, 14, 19 if fi == 7 else 12 + fi]), ('6/9, B form', [9, 14, t + 12, 12 + fi])]
        if f in ('min', 'mmaj', 'hdim'):
            if f == 'hdim': return [('A form', [3, 6, 10, 17]), ('B form', [10, 15, 17, 18])]
            seven = 11 if f == 'mmaj' else (self.sev if self.sev is not None else (9 if (9 in e or home) else 10))
            nine = 14
            if 17 in e and self.sev is not None: return [('A form', [3, 10, 14, 17]), ('B form', [10, 14, 15, 17])]
            return [('A form', [3, 7, seven, nine]), ('B form', [seven, nine, 15, 19])]
        if f in ('dom', 'sus'):
            three = t if t is not None else 7
            nine = 13 if 13 in e else 15 if 15 in e else 14
            thir = 20 if (20 in e or fi == 8) else 21
            if to_minor and 14 in [nine] and 21 == thir and not (21 in e or 14 in e):
                nine, thir = 13, 20          # V7 into a minor chord: ♭9 and ♭13
            if 18 in e or fi == 6:
                return [('A form', [three, 6 if fi == 6 else 18 - 12, 10, nine]), ('B form', [10, nine, three + 12, 18])]
            if f == 'sus': return [('A form', [5, 7, 10, 14]), ('B form', [10, 14, 17, 19])]
            return [('A form', [three, thir - 12, 10, nine]), ('B form', [10, nine, three + 12, thir])]
        return [('A form', sorted({self.third or 4, self.fifth, 12}))]

LAB = {0: 'R', 1: '♭9', 2: '9', 3: '♭3', 4: '3', 5: '4', 6: '♭5', 7: '5', 8: '♯5', 9: '6', 10: '♭7', 11: '7'}
def tone_label(ch, midi):
    i = (midi - ch.root) % 12
    f = ch.family
    if i == 2: return '9'
    if i == 1: return '♭9'
    if i == 3: return '♯9' if f in ('dom',) and ch.third == 4 else '♭3'
    if i == 5: return '4' if ch.third == 5 else '11'
    if i == 6: return '♭5' if (ch.fifth == 6 or f in ('dim', 'hdim')) else '♯11'
    if i == 8: return '♯5' if ch.fifth == 8 and f != 'dom' else ('♭13' if f in ('dom', 'sus') else '♯5')
    if i == 9: return ('𝄫7' if f == 'dim' else '13' if ch.sev in (10, 11) else '6')
    return LAB[i]

LETTERS = 'CDEFGAB'; NATPC = [0, 2, 4, 5, 7, 9, 11]
DEG_OFF = {'R': 0, '♭9': 1, '9': 1, '♯9': 1, '♭3': 2, '3': 2, '4': 3, '11': 3, '♯11': 3, '♭5': 4, '5': 4, '♯5': 4,
           '6': 5, '13': 5, '♭13': 5, '𝄫7': 6, '♭7': 6, '7': 6}
def spell(ch, midi, fallback):
    """The note's name as a tone of this chord: B♭7 has A♭ (its ♭7), not G♯."""
    try:
        lab = tone_label(ch, midi); off = DEG_OFF[lab]
        li = (LETTERS.index(ch.name[0]) + off) % 7
        acc = {0: '', 1: '♯', 11: '♭'}.get((midi - NATPC[li]) % 12)
        if acc is None or LETTERS[li] + acc in ('C♭', 'F♭', 'E♯', 'B♯'): return fallback
        return LETTERS[li] + acc + str((midi - NATPC[li] - (1 if acc == '♯' else -1 if acc == '♭' else 0)) // 12 - 1)
    except Exception:
        return fallback

def disp(name):
    m = re.match(r'^([A-G])([#b]?)(.*)$', name)
    r = m.group(1) + {'#': '♯', 'b': '♭', '': ''}[m.group(2)]
    q = m.group(3)
    q = re.sub(r'/([A-G])([#b]?)', lambda x: '/' + x.group(1) + {'#': '♯', 'b': '♭', '': ''}[x.group(2)], q)
    q = q.replace('b5', '♭5').replace('b9', '♭9').replace('b13', '♭13').replace('#5', '♯5').replace('#9', '♯9').replace('#11', '♯11').replace('dim7', '°7').replace('dim', '°')
    return r + q


def simplify(name):
    """The song's chord, played plainly: (chart name for Chord(), display name)."""
    ch = Chord(name)
    m = re.match(r'^([A-G][#b]?)', name); root = m.group(1)
    sl = re.search(r'/([A-G][#b]?)$', name); slash = '/' + sl.group(1) if sl else ''
    f, t, fi, sev, e = ch.family, ch.third, ch.fifth, ch.sev, ch.ext
    if f == 'dim': q = 'dim7' if sev == 9 else 'dim'
    elif f == 'hdim': q = 'm7b5'
    elif f == 'mmaj': q = 'm(maj7)'
    elif f == 'min':
        if fi == 6: q = 'dim'
        elif sev == 10: q = 'm7'
        elif 9 in e: q = 'm6'
        else: q = 'm'
    elif f in ('sus', 'sus3') or t == 5:
        q = '7sus4' if sev == 10 else 'sus4'
    elif t == 2: q = 'sus2'
    elif f == 'dom':
        q = '7' + ('#5' if fi == 8 else 'b5' if fi == 6 else '')
    elif f == 'aug': q = 'aug' if sev is None else ('7#5' if sev == 10 else 'maj7#5')
    else:  # major
        if sev == 11: q = 'maj7' + ('#5' if fi == 8 else '')
        elif 9 in e: q = '6'
        else: q = ''
    plain = root + q + slash
    return plain

class Arranger:
    def __init__(self, chart):
        self.C = chart
        k = (chart.get('key') or 'C major').split('/')[0].strip().split()
        self.key_pc = pc_of(k[0].replace('♭', 'b').replace('♯', '#')) if k else 0
        self.minor = len(k) > 1 and k[1].startswith('min')
        self.flats = k[0][1:2] in ('b', '♭') or (self.key_pc in (5, 10, 3, 8, 1, 6) and k[0][1:2] != '#') or (self.minor and self.key_pc in (2, 7, 0, 5))
        self.N = FLATN if self.flats else SHARPN
        self.meter = chart.get('meter') or 4
        self.bpm = chart.get('bpm') or 80

    def nn(self, m): return self.N[m % 12] + str(m // 12 - 1)

    def hands(self, ch):
        """Left-hand intervals above the bass, right-hand intervals above the root (three of them), and the name."""
        t, fi, sev = ch.third, ch.fifth, ch.sev
        six = 9 in ch.ext and sev is None
        slash = ch.bass != ch.root
        if sev is not None:
            rh = [t if t is not None else 7, fi, sev]
            lh = [0, sev]
        elif six:
            rh = [t, fi, 9]; lh = [0, 7]
        else:
            rh = [0, t if t is not None else 7, fi]
            lh = [0, 7] if fi == 7 else [0]
        if slash:
            lh = [0]
            b = (ch.bass - ch.root) % 12
            if b in [x % 12 for x in rh] and 0 not in rh:
                rh = [0 if x % 12 == b else x for x in rh]
        rootless = 0 not in [x % 12 for x in rh]
        name = ('Bass' if len(lh) == 1 and slash else 'Root' if len(lh) == 1 else 'Shell') + (' + rootless' if rootless else ' + triad')
        return lh, rh, name

    def rh_options(self, ch, ivs, lo_floor):
        pcs = [(ch.root + i) % 12 for i in ivs]
        out = []
        for bottom in range(52, 70):
            if bottom % 12 not in pcs: continue
            rest = [p for p in pcs if p != bottom % 12] if len(set(pcs)) == len(pcs) else pcs[1:]
            v = [bottom]
            for p in rest:
                v.append(bottom + ((p - bottom) % 12 or 12))
            v = sorted(v)
            if v[-1] - v[0] > 12: continue
            if v[0] < lo_floor: continue
            out.append(v)
        return out

    def choose_rh(self, ch, ivs, prev, sung, lh_top):
        best = None
        for v in self.rh_options(ch, ivs, max(55, lh_top + 3)):
            c = 0.0
            if prev:
                a = sorted(prev); c += sum(abs(x - y) for x, y in zip(a, v)) * 0.5
            else:
                c += abs(sum(v) / len(v) - 64) * 0.3
            c += 1.0 * max(0, v[-1] - 72) + 0.6 * max(0, 57 - v[0]) + 0.25 * abs(sum(v) / len(v) - 63)
            for n in v:
                for p in sung:
                    d = (n - p) % 12
                    if d == 1: c += 3.0
                    elif d == 11: c += 0.8
            if best is None or c < best[0]: best = (c, v)
        return best[1] if best else sorted(60 + i for i in ivs)

    def four(self, ch, rh, lh_top):
        """A fourth right-hand note for a fuller chord: the 9th on a major 7th (the root would rub against
        the 7th), the root on other 7th and 6th chords, the bottom note an octave up on a triad.
        Fitted inside the hand if it can be, so the top note stays; the hand never spans more than an octave."""
        pcs = {m % 12 for m in rh}
        want = []
        if ch.family == 'maj' and ch.sev == 11: want = [2]
        elif ch.sev is not None or (9 in ch.ext and ch.sev is None): want = [0]
        for iv in want:
            pc = (ch.root + iv) % 12
            if pc in pcs: continue
            best = None
            for m in range(max(55, lh_top + 3), 76):
                if m % 12 != pc: continue
                v = sorted(rh + [m])
                if v[-1] - v[0] > 12: continue
                cost = (0 if rh[0] < m < rh[-1] else 2) + 0.1 * (v[-1] - v[0])
                if best is None or cost < best[0]: best = (cost, v)
            if best: return best[1]
        if rh[0] + 12 <= 75 and rh[0] + 12 > rh[-1]: return sorted(rh + [rh[0] + 12])
        return rh

    def bass(self, ch, prev, two):
        top = 47 if two else 50
        cands = [m for m in range(36, top + 1) if m % 12 == ch.bass]
        if prev is None: return min(cands, key=lambda m: abs(m - 42))
        return min(cands, key=lambda m: abs(m - prev) + 0.3 * abs(m - 42))

    def scale(self, ch):
        f = ch.family
        if f == 'maj' or f == 'aug' or f == 'sus3': s = [0, 2, 4, 5, 7, 9, 11] if 18 not in ch.ext else [0, 2, 4, 6, 7, 9, 11]
        elif f == 'dom' or f == 'sus':
            s = [0, 1, 4, 5, 7, 8, 10] if (13 in ch.ext or 20 in ch.ext or ch.fifth == 8) else [0, 2, 4, 5, 7, 9, 10]
        elif f == 'mmaj': s = [0, 2, 3, 5, 7, 9, 11]
        elif f == 'hdim': s = [0, 1, 3, 5, 6, 8, 10]
        elif f == 'dim': s = [0, 2, 3, 5, 6, 8, 9, 11]
        else: s = [0, 2, 3, 5, 7, 9, 10]
        nm = {(0, 2, 4, 5, 7, 9, 11): 'major scale', (0, 2, 4, 6, 7, 9, 11): 'Lydian scale', (0, 2, 4, 5, 7, 9, 10): 'Mixolydian scale',
              (0, 1, 4, 5, 7, 8, 10): 'Mixolydian with ♭9 and ♭13', (0, 2, 3, 5, 7, 9, 11): 'melodic minor scale', (0, 1, 3, 5, 6, 8, 10): 'Locrian scale',
              (0, 2, 3, 5, 6, 8, 9, 11): 'diminished scale', (0, 2, 3, 5, 7, 9, 10): 'Dorian scale'}[tuple(s)]
        return [(ch.root + i) % 12 for i in s], nm

    def fill(self, ch, start_note, target, n):
        """n notes stepping through the chord's scale from near start_note toward a neighbour of target."""
        pcs, nm = self.scale(ch)
        pool = sorted(m for m in range(55, 84) if m % 12 in pcs)
        if not pool: return [], nm
        tgt = target
        # end a step above or below the next chord's top note, coming from the direction of travel
        up = start_note < tgt
        end_c = [m for m in pool if (m < tgt if up else m > tgt)]
        end = (max(end_c) if up else min(end_c)) if end_c else tgt
        i_end = pool.index(end)
        i_start = i_end - (n - 1) if up else i_end + (n - 1)
        i_start = max(0, min(len(pool) - 1, i_start))
        seq = pool[i_start:i_end + 1] if up else list(reversed(pool[i_end:i_start + 1]))
        if len(seq) < n: seq = (seq + seq[::-1])[:n]
        return seq[:n], nm

    def run(self):
        C = self.C; bars = C['bars']
        prev_rh = None; prev_b = None; out_bars = []; events = []
        seen_part = {}; last_fill = -99; part = None
        rel_done = set(); moves_done = 0; six_done = 0; last_four = -99
        flat = []
        for bi, b in enumerate(bars):
            for c in b['chords']: flat.append((bi, c))
        uid = 0
        slow = self.bpm < 92
        gap = 12 if self.bpm >= 120 else 8
        for bi, b in enumerate(bars):
            if b['sec'] != part:
                part = b['sec']; seen_part = {}
            st, en = b['start'], b['end']
            beats = b['beats'] or self.meter
            spb = (en - st) / beats if beats else 60.0 / self.bpm
            sung = {pc_of(x.replace('♭', 'b').replace('♯', '#')) for x in b.get('mel', []) if x and x[0] in NOTE}
            segs = []
            for ci, c in enumerate(b['chords']):
                try:
                    plain = simplify(c['c']); ch = Chord(plain)
                except Exception:
                    continue
                tip = None
                # a major 7th under a sung root rubs: play the 6th instead
                if ch.family == 'maj' and ch.sev == 11 and ch.fifth == 7 and ch.root in sung:
                    plain = plain.replace('maj7', '6'); ch = Chord(plain)
                    if six_done < 2:
                        tip = f"{disp(plain).split('/')[0]} here, not major 7: you sing {self.N[ch.root]}, and the 7th would rub against it."
                        six_done += 1
                lhi, rhi, form = self.hands(ch)
                lh0 = self.bass(ch, prev_b, len(lhi) > 1)
                lh = [lh0 + i for i in lhi]
                rh3 = self.choose_rh(ch, rhi, prev_rh, sung, lh[-1]); rh = rh3
                # now and then a fourth finger: where a part starts or ends, the last chord, a long chord while the voice rests
                last_in_bar = ci == len(b['chords']) - 1
                part_end = last_in_bar and (bi + 1 == len(bars) or bars[bi + 1]['sec'] != b['sec'])
                vocb = b.get('voc') or ''
                resting = (vocb.count('·') * 2 >= len(vocb)) if vocb else bool(re.search(r'intro|ending|interlude|instrumental|solo', b['sec'] or '', re.I))
                song_end = part_end and bi + 1 == len(bars)
                part_start = ci == 0 and (bi == 0 or bars[bi - 1]['sec'] != b['sec'])
                if song_end or (bi - last_four >= 4 and (((part_end or part_start) and c['beats'] >= 2) or (c['beats'] >= 4 and resting))):
                    r4 = self.four(ch, rh3, lh[-1])
                    if len(r4) == 4:
                        rh = r4; last_four = bi
                        form = form.replace('rootless', 'four notes').replace('triad', 'four notes')
                t0 = st + c['at'] * spb; t1 = st + (c['at'] + c['beats']) * spb
                key = (plain, tuple(rh), tuple(lh))
                same = seen_part.get(key)
                uid += 1; sid = f's{uid}'
                if same is None: seen_part[key] = sid
                tones = {str(m): tone_label(ch, m) for m in lh + rh}
                if tip is None and prev_rh and len(rh) == 3:
                    diff = [(a, x) for a, x in zip(sorted(prev_rh), rh) if a != x]
                    if len(diff) == 1 and abs(diff[0][0] - diff[0][1]) <= 2 and moves_done < 3:
                        tip = f"Only one finger moves: {self.N[diff[0][0] % 12]} {'up' if diff[0][1] > diff[0][0] else 'down'} to {self.N[diff[0][1] % 12]}."
                        moves_done += 1
                if tip is None and same is None and 'rootless' in form:
                    rel = self.relation(ch, rh, plain)
                    if rel and rel not in rel_done and len(rel_done) < 4:
                        tip = rel; rel_done.add(rel)
                seg = dict(id=sid, c=disp(plain).replace('aug', '+'), beats=c['beats'], at=c['at'], lh=lh, rh=rh, form=form, tones=tones, same=same, tip=tip,
                           names=[spell(ch, m, self.nn(m)) for m in lh + rh])
                segs.append(seg)
                # ---- comping: held chords; a waltz plays the right hand on 2 and 3; quicker songs strike again
                for m in lh: events.append(dict(t=t0, midi=m, vel=0.52, off=t1, hand='L', seg=sid))
                if self.meter == 3 and c['beats'] >= 2:
                    for k_ in range(1, int(round(c['beats']))):
                        tk = t0 + k_ * spb
                        for j, m in enumerate(rh): events.append(dict(t=tk + 0.008 * j, midi=m, vel=0.42, off=tk + spb * 0.9, hand='R', seg=sid))
                else:
                    for j, m in enumerate(rh): events.append(dict(t=t0 + 0.014 * j, midi=m, vel=0.5 + 0.04 * (j == len(rh) - 1), off=t1, hand='R', seg=sid))
                    if not slow and c['beats'] >= 4:
                        tk = t0 + 2 * spb
                        for j, m in enumerate(rh): events.append(dict(t=tk + 0.01 * j, midi=m, vel=0.4, off=t1, hand='R', seg=sid))
                prev_rh, prev_b = rh3, lh0
            # ---- a fill where the voice rests at the end of the bar, leading into the next chord
            fill = None
            voc = b.get('voc') or ''
            rest_end = 0
            for ch_ in reversed(voc):
                if ch_ == '·': rest_end += 1
                else: break
            if not voc and (re.search(r'intro|ending|interlude|instrumental|solo', b['sec'] or '', re.I)) and bi + 1 < len(bars) and bars[bi + 1]['sec'] != b['sec']:
                rest_end = 4
            if segs and rest_end >= 3 and bi - last_fill >= gap and bi + 1 < len(bars) and bars[bi + 1]['chords']:
                try:
                    chn = Chord(simplify(bars[bi + 1]['chords'][0]['c']))
                    _, nri, _ = self.hands(chn)
                    nrh = self.choose_rh(chn, nri, prev_rh, set(), 50)
                    ch_last = Chord(simplify(b['chords'][-1]['c']))
                    eighths = min(rest_end, 5)
                    beats_per8 = (b['beats'] or self.meter) / max(1, len(voc) or 8)
                    notes, scale_name = self.fill(ch_last, prev_rh[-1], nrh[-1], eighths)
                    if len(notes) >= 3:
                        tstart = en - eighths * beats_per8 * spb
                        dur8 = beats_per8 * spb
                        for e in events:
                            if e['hand'] == 'R' and e['off'] > tstart and e['t'] < tstart and e['seg'] == segs[-1]['id']: e['off'] = tstart + 0.05
                        for j, m in enumerate(notes):
                            events.append(dict(t=tstart + j * dur8, midi=m, vel=0.5 + 0.03 * j / len(notes), off=tstart + (j + 1.2) * dur8, hand='F', seg=f'f{bi}'))
                        fill = dict(id=f'f{bi}', notes=notes, names=[spell(ch_last, m, self.nn(m)) for m in notes], scale=f"{self.N[ch_last.root]} {scale_name}",
                                    tones={str(m): tone_label(ch_last, m) for m in notes}, chord=disp(simplify(b['chords'][-1]['c'])), into=disp(simplify(bars[bi + 1]['chords'][0]['c'])),
                                    t=round(tstart, 3))
                        last_fill = bi
                except Exception:
                    pass
            out_bars.append(dict(n=b['label'], sec=b['sec'], start=round(st, 3), end=round(en, 3), voc=voc,
                                 words=b.get('words', '') if self.C.get('words_free') else '', segs=segs, fill=fill))
        if events:
            lastt = max(e['t'] for e in events)
            tail = [e for e in events if e['t'] >= lastt - 0.1]
            for j, e in enumerate(sorted(tail, key=lambda e: e['midi'])):
                e['t'] += 0.06 * j; e['off'] = e['t'] + 4.0; e['vel'] = min(0.6, e['vel'] + 0.05)
        return dict(bars=out_bars, events=events)

    def relation(self, ch, rh, plain):
        """When the right hand's three notes are a plain triad, say which: it is the easiest way to find them."""
        s = sorted({m % 12 for m in rh})
        if len(s) != 3: return None
        for r in range(12):
            for q, iv in (('major', [0, 4, 7]), ('minor', [0, 3, 7]), ('diminished', [0, 3, 6])):
                if sorted((r + i) % 12 for i in iv) == s and r != ch.root:
                    pn = lambda pc: re.sub(r'-?\d+$', '', spell(ch, 60 + pc, self.N[pc]))
                    return f"Your right hand is a plain {pn(r)} {q} chord. With {pn(ch.bass)} in the left hand it becomes {disp(plain).split('/')[0]}."
        return None

if __name__ == '__main__':
    import sys
    C = json.load(open(sys.argv[1]))
    A = Arranger(C).run()
    for b in A['bars'][:12]:
        print(b['n'], b['sec'][:14], [(s['c'], s['form'], s['names'], s['same'] is not None, s['tip']) for s in b['segs']], b['fill'] and (b['fill']['names'], b['fill']['scale']))
    print(len(A['events']), 'events')
