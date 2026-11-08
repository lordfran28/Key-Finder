"""The singer for each piano page: the guitar page's track with the singer (on the Fret Finder shelf),
opened with the singer key, with the guitar taken out; and the sung pitch, frame by frame, for the
rub check.  python3 voices.py [SLUG ...]   (writes WORK/SLUG/stem.npy, vp.npz; nothing goes in the repo)"""
import os, sys, json, subprocess, numpy as np
FF = '/home/claude/fret-finder/songs'
SP = '/tmp/claude-0/-home-claude/32eff81e-a259-5caa-a171-2530c104e7b0/scratchpad'
WORK = SP + '/kfwork'
UNLOCK = SP + '/unlock.mjs'
SR = 44100
# songs whose guitar page has more than one pair of tracks: (track with the singer, guitar alone)
PAIRS = {
 'what-a-difference-a-day-made': ('wad-long-voice.mp3.locked', 'wad-long-full.mp3'),      # the guitar with the trumpet
 'i-wonder-whos-kissing-her-now': ('iwonder-full-dean.mp3.locked', 'iwonder-full.mp3'),
 'you-dont-mess-around-with-jim': ('jim-voice.mp3.locked', 'jim-guitar.mp3'),
 'barquito-de-papel': ('bq-with-serrat.mp3.locked', 'bq-guitar-trumpet.mp3'),
 'ochi-chyornye': ('oci-voice.mp3', 'oci-guitar.mp3'),
}
# songs with no guitar page: the record itself (kept locked as it is), for the pitch only
RECORDS = {
 'are-you-lonesome-tonight': SP + '/imp/lonesome/are-you-lonesome-tonight-full.mp3',
 'love-me-tender': SP + '/imp/tender/love-me-tender-full.mp3',
}
NONE = {'it-had-to-be-you', 'dont-get-around-much-anymore'}

def pair(slug):
    if slug in NONE: return None
    if slug in RECORDS: return (RECORDS[slug], None)
    if slug in PAIRS:
        v, g = PAIRS[slug]
    else:
        files = json.load(open(os.path.join(FF, slug, 'song.json')))['files']
        L = [f for f in files if f.endswith('.locked')]
        G = [f for f in files if f.endswith('-guitar.mp3')]
        if len(L) != 1 or len(G) != 1: raise SystemExit(f'{slug}: tracks {files}')
        v, g = L[0], G[0]
    return (os.path.join(FF, slug, v), os.path.join(FF, slug, g))

def decode(path, sr=SR, ch=2):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', str(ch), '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(r, np.float32).reshape(-1, ch)

def mix_path(slug):
    p = pair(slug)
    if p is None: return None
    v = p[0]
    if not v.endswith('.locked'): return v
    out = os.path.join(WORK, slug, 'mix.mp3')
    if not os.path.exists(out):
        os.makedirs(os.path.dirname(out), exist_ok=True)
        subprocess.run(['node', UNLOCK, v, out], check=True, capture_output=True)
    return out

def stem(slug):
    """The singer alone (stereo, SR), on the guitar track's timeline; None for a song with no singer."""
    p = pair(slug)
    if p is None: return None, None
    f = os.path.join(WORK, slug, 'stem.npy')
    if os.path.exists(f): return np.load(f), ('record' if p[1] is None else 'stem')
    sep = os.path.join(WORK, slug, 'sep_voc.wav')
    m = decode(mix_path(slug))
    if os.path.exists(sep):                     # the guitar under this mix is not the page's: the voice was separated
        s = decode(sep)[:len(m)]; kind = 'stem'
    elif p[1] is None:
        s = m; kind = 'record'
    else:
        g = decode(p[1]); n = min(len(m), len(g)); m, g = m[:n], g[:n]
        k = float(np.sum(m * g) / max(1e-9, np.sum(g * g)))
        s = m - k * g; kind = 'stem'
        print(slug, 'guitar gain %.3f, left %.2f of the mix' % (k, np.sqrt(np.mean(s ** 2) / np.mean(m ** 2))))
    os.makedirs(os.path.dirname(f), exist_ok=True); np.save(f, s.astype(np.float32))
    return s, kind

def yin(x, sr=22050, N=2048, H=256, fmin=70.0, fmax=520.0):
    tmin, tmax = int(sr / fmax), int(sr / fmin)
    nfr = (len(x) - N) // H
    idx = np.arange(N)[None, :] + H * np.arange(nfr)[:, None]
    F = x[idx]                                     # frames
    W = N // 2
    rms = np.sqrt(np.mean(F ** 2, 1))
    A = np.fft.rfft(F, 2 * N); B = np.fft.rfft(F[:, :W], 2 * N)
    r = np.fft.irfft(A * np.conj(B), 2 * N)[:, :tmax + 1]
    cs = np.concatenate([np.zeros((nfr, 1)), np.cumsum(F ** 2, 1)], 1)
    tau = np.arange(tmax + 1)
    d = (cs[:, W] - cs[:, 0])[:, None] + cs[:, tau + W] - cs[:, tau] - 2 * r
    d[:, 0] = 0
    c = np.cumsum(d[:, 1:], 1)
    cm = np.ones_like(d); cm[:, 1:] = d[:, 1:] * tau[1:] / np.maximum(c, 1e-12)
    seg = cm[:, tmin:tmax]
    below = (seg[:, :-1] < 0.15) & (seg[:, :-1] <= seg[:, 1:])
    first = np.where(below.any(1), below.argmax(1), seg.argmin(1))
    t0 = first + tmin
    i = np.arange(nfr)
    a_, b_, c_ = cm[i, t0 - 1], cm[i, t0], cm[i, np.minimum(t0 + 1, tmax)]
    den = a_ - 2 * b_ + c_
    p = np.where(np.abs(den) > 1e-12, 0.5 * (a_ - c_) / np.where(np.abs(den) > 1e-12, den, 1), 0)
    f0 = sr / (t0 + p); conf = 1 - b_
    t = (np.arange(nfr) * H + N / 2) / sr
    return t, f0, conf, rms

def pitch(slug):
    f = os.path.join(WORK, slug, 'vp.npz')
    if os.path.exists(f): return dict(np.load(f))
    s, kind = stem(slug)
    if s is None: return None
    m = s.mean(1)
    # down to 22050
    from scipy.signal import resample_poly
    y = resample_poly(m, 1, 2).astype(np.float64)
    out = []
    step = 22050 * 60
    T, F0, CF, RM = [], [], [], []
    for a in range(0, len(y), step):
        seg = y[a:a + step + 2048]
        if len(seg) < 4096: break
        t, f0, cf, rm = yin(seg)
        keep = t < step / 22050 + 1e-9
        T.append(t[keep] + a / 22050); F0.append(f0[keep]); CF.append(cf[keep]); RM.append(rm[keep])
    D = dict(t=np.concatenate(T), f0=np.concatenate(F0), conf=np.concatenate(CF), rms=np.concatenate(RM))
    np.savez(f, **D)
    return D

if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import charts
    for slug in (sys.argv[1:] or list(charts.SONGS)):
        if pair(slug) is None: print(slug, 'no singer'); continue
        D = pitch(slug)
        ok = (D['conf'] > 0.5) & (D['rms'] > 0.003)
        print(slug, 'frames', len(D['t']), 'sung %.0f%%' % (100 * ok.mean()))
