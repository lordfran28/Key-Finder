"""Piano audio from the Salamander Grand Piano samples (Alexander Holm, CC BY 3.0), one per minor third.
render(notes, length) -> stereo float array at SR. A note is dict(t, midi, vel 0..1, off, hand 'L'/'R')."""
import os, numpy as np, scipy.io.wavfile as w
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = {'C': 0, 'Ds': 3, 'Fs': 6, 'A': 9}
_S = {}
def _load():
    if _S: return _S
    for f in os.listdir(os.path.join(HERE, 'samples')):
        n, o = f[:-5], int(f[-5])
        m = 12 * (o + 1) + NAMES[n]
        sr, x = w.read(os.path.join(HERE, 'samples', f))
        x = x.astype(np.float32) / 32768.0
        _S[m] = x
    return _S

def _voice(m, vel, dur, rel=0.32):
    S = _load(); r = min(S, key=lambda k: abs(k - m)); x = S[r]
    ratio = 2 ** ((m - r) / 12)
    n_out = int((dur + rel * 5) * SR)
    pos = np.arange(n_out) * ratio
    pos = pos[pos < len(x) - 1]
    y = np.interp(pos, np.arange(len(x)), x).astype(np.float32)
    # softer touch: quieter and darker
    g = 0.18 + 0.82 * vel ** 1.6
    if vel < 0.75:
        a = np.exp(-2 * np.pi * (1800 + 7000 * vel) / SR)
        z = np.empty_like(y); acc = 0.0
        # one-pole low-pass (vectorised in blocks would be faster; notes are short enough)
        for i in range(0, len(y), 4096):
            seg = y[i:i + 4096]
            from scipy.signal import lfilter
            out, zi = lfilter([1 - a], [1, -a], seg, zi=[acc * a])
            z[i:i + 4096] = out; acc = out[-1] if len(out) else acc
        y = z
    k = int(dur * SR)
    if k < len(y):
        env = np.ones(len(y), np.float32)
        env[k:] = np.exp(-np.arange(len(y) - k) / (rel * SR))
        y = y * env
    return y * g

def _reverb(x, wet=0.16, seed=3):
    rng = np.random.default_rng(seed)
    n = int(1.6 * SR); t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)).astype(np.float32) * np.exp(-t / 0.42)[:, None]
    ir[:int(0.012 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum(0, keepdims=True))
    from scipy.signal import fftconvolve
    out = np.stack([fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], 1)
    return x + wet * out

def render(notes, length):
    N = int(length * SR) + SR
    out = np.zeros((N, 2), np.float32)
    for e in notes:
        i = int(e['t'] * SR)
        if i >= N: continue
        y = _voice(e['midi'], e.get('vel', 0.6), max(0.08, e['off'] - e['t']), rel=e.get('rel', 0.32))
        y = y[:N - i]
        pan = np.clip((e['midi'] - 60) / 48, -0.35, 0.35)
        out[i:i + len(y), 0] += y * (0.5 - pan / 2) * 2
        out[i:i + len(y), 1] += y * (0.5 + pan / 2) * 2
    out = _reverb(out)
    return out[:int(length * SR)]

def write_mp3(x, path, peak=0.89, fade=1.5):
    x = x.copy()
    n = int(fade * SR)
    if len(x) > n: x[-n:] *= np.linspace(1, 0, n)[:, None]
    x *= peak / max(1e-6, np.abs(x).max())
    tmp = path + '.wav'
    w.write(tmp, SR, (x * 32767).astype(np.int16))
    os.system(f'ffmpeg -v error -y -i "{tmp}" -b:a 160k "{path}"'); os.remove(tmp)
