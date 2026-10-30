"""Original dhol sounds, modelled on a real Punjabi dhol (no third-party audio).

Usage: python3 make_dhol_sfx.py <sfx_dir>   (writes dhol-intro.mp3, dhol-loop.mp3, adds them to manifest.json)

A dhol has two heads. The thick dagga stick hits the bass head: a deep boom whose pitch drops right after the
hit, with the inharmonic overtones of a round drum skin, a wooden shell ring and a leathery slap. The thin tilli
cane hits the tight treble head: a short bright 'tak' with a cane click. v2 (Oct 2026, after "sounds fake"):
circular-membrane modes instead of a single sine, a shell resonance, two slightly different drummers, timing and
velocity humanised, the bhangra chaal played on a swung triplet grid, and a small room around it.
"""
import numpy as np, soundfile as sf, subprocess, json, sys
OUT = sys.argv[1]; sr = 44100
rng = np.random.default_rng(11)
MODES = [1.0, 1.59, 2.14, 2.30, 2.65, 2.92, 3.16, 3.50]       # ideal round-membrane overtone ratios


def bp(x, lo, hi):
    """Band-pass with a pair of one-pole filters (cheap, no scipy)."""
    def lp(v, fc):
        a = np.exp(-2 * np.pi * fc / sr); y = np.empty_like(v); s = 0.0
        for i, u in enumerate(v): s = (1 - a) * u + a * s; y[i] = s
        return y
    return lp(x, hi) - lp(x, lo)


def membrane(f0, d, decay, bend, bend_t, bright):
    t = np.arange(int(sr * d)) / sr
    out = np.zeros_like(t)
    for k, r in enumerate(MODES):
        f = f0 * r * (1 + bend * np.exp(-t / bend_t))
        amp = bright ** k / (1 + 0.4 * k)
        out += amp * np.sin(2 * np.pi * np.cumsum(f) / sr + rng.uniform(0, 6.28)) * np.exp(-t / (decay / (1 + 0.9 * k)))
    return out


def dagga(v=1.0):
    """Bass head: deep boom with a fast pitch drop, shell ring and a leathery slap."""
    d = 0.75; t = np.arange(int(sr * d)) / sr
    f0 = 62 * rng.uniform(0.97, 1.03)
    boom = membrane(f0, d, 0.26, 0.9, 0.03, 0.5)
    shell = np.sin(2 * np.pi * 182 * t) * np.exp(-t / 0.07) * 0.25
    slap = bp(rng.standard_normal(len(t)) * np.exp(-t / 0.012), 180, 1400) * 1.4
    x = boom + shell + slap
    return np.tanh(0.9 * x) * v


def tilli(v=1.0):
    """Treble head: tight bright 'tak' plus the click of the cane."""
    d = 0.25; t = np.arange(int(sr * d)) / sr
    f0 = 410 * rng.uniform(0.97, 1.04)
    skin = membrane(f0, d, 0.07, 0.25, 0.01, 0.7) * 0.7
    click = bp(rng.standard_normal(len(t)) * np.exp(-t / 0.004), 1800, 7000) * 1.6
    rattle = bp(rng.standard_normal(len(t)) * np.exp(-t / 0.03), 900, 3500) * 0.35
    return np.tanh(0.9 * (skin + click + rattle)) * 0.7 * v


def room(x, mix=0.18):
    n = int(sr * 0.55); t = np.arange(n) / sr
    ir = rng.standard_normal(n) * np.exp(-t / 0.12); ir[:int(sr * 0.012)] = 0
    ir = bp(ir, 120, 5000); ir /= np.abs(ir).sum() / 6
    wet = np.convolve(x, ir)[:len(x)]
    return x + mix * wet


def play(pattern, dur, drummers=((0.0, 1.0, 0.0), (0.012, 0.8, 0.35))):
    """pattern: (time, 'D' bass | 'T' treble | 'B' both, velocity). Each drummer: (lag s, gain, pan)."""
    L = np.zeros(int(sr * (dur + 0.8))); R = np.zeros_like(L)
    for lag, gain, pan in drummers:
        for t0, kind, v in pattern:
            t1 = t0 + lag + rng.normal(0, 0.006)
            vv = v * gain * rng.uniform(0.88, 1.0)
            hits = []
            if kind in 'DB': hits.append(dagga(vv))
            if kind in 'TB': hits.append(tilli(vv * 0.9))
            for h in hits:
                i = max(0, int(t1 * sr)); n = min(len(h), len(L) - i)
                L[i:i + n] += h[:n] * (1 - max(0, pan)); R[i:i + n] += h[:n] * (1 + min(0, pan))
    L, R = room(L), room(R)
    x = np.stack([L, R], 1)[:int(sr * dur)]
    return x / np.abs(x).max() * 0.9


def write(x, name):
    sf.write(OUT + '/_' + name + '.wav', x.astype(np.float32), sr)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', OUT + '/_' + name + '.wav', '-af',
                    'equalizer=f=70:t=q:w=1:g=3,equalizer=f=3000:t=q:w=1:g=2,acompressor=threshold=-12dB:ratio=2:attack=8:release=120,alimiter=limit=0.84',
                    '-b:a', '192k', OUT + '/' + name + '.mp3'], check=True)
    subprocess.run(['rm', OUT + '/_' + name + '.wav'])


BEAT = 60 / 104; TR = BEAT / 3                     # 104 bpm, swung triplets
SW = [0, TR * 1.08, TR * 2.05]                      # a little push on the middle triplet


def chaal(bars, accent_last=True):
    """Bhangra chaal: DHA . ta | DHA . ta | DHA . ta | DHA ta ta, with the tilli filling the gaps."""
    p = []
    for b in range(bars):
        o = b * 4 * BEAT
        for beat in range(4):
            ob = o + beat * BEAT
            p.append((ob, 'B' if beat in (0, 2) else 'D', 1.0 if beat == 0 else 0.85))
            if beat < 3: p.append((ob + SW[2], 'T', 0.7))
            else: p += [(ob + SW[1], 'T', 0.6), (ob + SW[2], 'T', 0.75)]
    return p


# intro: a tilli roll that speeds up, then three big hits (the third lands at INTRO_HIT)
roll = []; t = 0.0; gap = 0.11
while t < 0.62:
    roll.append((t, 'T', 0.5 + 0.5 * t / 0.62)); t += gap; gap = max(0.045, gap * 0.86)
INTRO_HIT = 0.9
intro = roll + [(0.66, 'B', 0.9), (0.78, 'D', 0.9), (INTRO_HIT, 'B', 1.15)]
write(play(intro, 1.7), 'dhol-intro')
loop = chaal(4)
write(play(loop, 4 * 4 * BEAT + 0.3), 'dhol-loop')

m = json.load(open(OUT + '/manifest.json'))
m['dhol-intro'] = {'file': 'dhol-intro.mp3', 'description': 'Original dhol intro (modelled): tilli roll speeding up, then DHA-dha-DHA; the big hit lands at 0.9 s.', 'duration': 1.7}
m['dhol-loop'] = {'file': 'dhol-loop.mp3', 'description': 'Original bhangra chaal on dhol (modelled, two drummers), 4 bars at 104 bpm, beat every %.3f s.' % BEAT, 'duration': round(4 * 4 * BEAT + 0.3, 2)}
json.dump(m, open(OUT + '/manifest.json', 'w'), indent=1); print('ok beat', round(BEAT, 4))
