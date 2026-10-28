"""Composes the stickman reel's soundtrack entirely in code.

Usage: python3 make_audio.py timeline.json voices_dir out.wav mouths.json

- Original music following the plan: lazy C major (115 BPM), sad A minor piano (80 BPM),
  record scratch into a 140 BPM hype section, then a C major resolve that leads back into bar 1.
- Every sound effect is synthesized here.
- Voice clips are placed at their bubble times; the music ducks ~60% under speech.
- Writes per-character mouth-openness envelopes (30 fps) for the lip-sync animation.
"""
import json, sys
import numpy as np
import soundfile as sf

TL = json.load(open(sys.argv[1])); VOICES = sys.argv[2]; OUT = sys.argv[3]; MOUTHS = sys.argv[4]
SR = 44100
DUR = TL["duration"]
TAIL = 2.5                      # rendered past the end, then wrapped onto the start for a seamless loop
N = int((DUR + TAIL) * SR)
rng = np.random.default_rng(42)

music = np.zeros((N, 2)); sfx = np.zeros((N, 2)); vox = np.zeros((N, 2))


def tt(d):
    return np.arange(int(d * SR)) / SR


def put(buf, sig, t, g=1.0, pan=0.0):
    i = int(round(t * SR)); j = min(len(buf), i + len(sig))
    if j <= i or i < 0:
        return
    s = sig[: j - i] * g
    buf[i:j, 0] += s * min(1, 1 - pan); buf[i:j, 1] += s * min(1, 1 + pan)


def onepole(x, a):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc); y[i] = acc
    return y


def sweep(x, a0, a1):
    a = np.linspace(a0, a1, len(x)); y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += a[i] * (v - acc); y[i] = acc
    return y


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ---------------------------------------------------------------- instruments
def pluck(m, d, bright=0.5):
    """Karplus-Strong ukulele-ish pluck."""
    f = hz(m); p = max(2, int(SR / f)); n = int(d * SR)
    buf = onepole(rng.uniform(-1, 1, p), bright)
    out = np.empty(n); k = 0
    for i in range(n):
        v = buf[k]; nk = (k + 1) % p
        buf[k] = 0.497 * (v + buf[nk]); out[i] = v; k = nk
    e = np.minimum(1, (n - np.arange(n)) / (0.02 * SR))
    return out * e


def piano(m, d):
    t = tt(d); f = hz(m)
    s = sum(g * np.sin(2 * np.pi * f * h * (1 + 0.0004 * h * h) * t) * np.exp(-t * (1.2 + h * 0.9))
            for h, g in ((1, 1), (2, 0.45), (3, 0.25), (4, 0.12), (5, 0.06)))
    hammer = onepole(rng.standard_normal(len(t)), 0.3) * np.exp(-t / 0.01) * 0.15
    e = np.minimum(1, (len(t) - np.arange(len(t))) / (0.08 * SR))
    return (s + hammer) * e * 0.5


def square_lead(m, d):
    t = tt(d); f = hz(m)
    s = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * 2 * f * t) * 0.3
    s = onepole(s, 0.25)
    return s * np.exp(-t / 0.18) * np.minimum(1, t / 0.004)


def bass_note(m, d, kind="tri"):
    t = tt(d); f = hz(m)
    if kind == "tri":
        s = 2 * np.abs(2 * ((t * f) % 1) - 1) - 1
    else:
        s = onepole(2 * ((t * f) % 1) - 1, 0.12) * 1.6
    e = np.minimum(1, t / 0.004) * np.minimum(1, (len(t) - np.arange(len(t))) / (0.015 * SR))
    return s * e


def snap():
    t = tt(0.08); n = rng.standard_normal(len(t))
    hp = n - onepole(n, 0.35)
    return hp * np.exp(-t / 0.012) * 0.7 + np.sin(2 * np.pi * 1900 * t) * np.exp(-t / 0.006) * 0.4


def kick(g=1.0):
    t = tt(0.35); f = 48 + 140 * np.exp(-t / 0.03)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.14) * 2.0) * g


def clap():
    t = tt(0.22); n = rng.standard_normal(len(t)); e = np.exp(-t / 0.05)
    for o in (0.0, 0.01, 0.02):
        e = e + (t >= o) * np.exp(-np.clip(t - o, 0, None) / 0.005) * 0.6
    return (n - onepole(n, 0.15)) * e * 0.45


def hat(open_=False):
    t = tt(0.12 if open_ else 0.05); n = rng.standard_normal(len(t))
    return (n - onepole(n, 0.7)) * np.exp(-t / (0.04 if open_ else 0.01)) * 0.35


# ---------------------------------------------------------------- music
CHORDS = {"C": (48, [60, 64, 67]), "Am": (45, [57, 60, 64]), "F": (41, [57, 60, 65]), "G": (43, [55, 59, 62]),
          "Dm": (38, [57, 62, 65]), "E": (40, [56, 59, 64])}
PROG = ["C", "Am", "F", "G"]
# main melody: 4 bars of (beat, midi, beats)
MEL = [
    [(0, 76, .5), (.5, 79, .5), (1, 84, 1), (2, 79, .5), (2.5, 76, .5), (3, 79, 1)],
    [(0, 81, .5), (.5, 84, .5), (1, 88, 1), (2, 84, .5), (2.5, 81, .5), (3, 84, 1)],
    [(0, 77, .5), (.5, 81, .5), (1, 84, 1), (2, 81, .5), (2.5, 77, .5), (3, 81, 1)],
    [(0, 79, .5), (.5, 83, .5), (1, 86, .5), (1.5, 84, .5), (2, 83, .5), (2.5, 81, .5), (3, 79, 1)],
]
mus = TL["music"]
pause0, pause1 = mus["pause"]

# --- lazy section: 115 BPM
b = 60 / 115
s0, s1 = mus["lazy"]
nb = int(np.ceil((s1 - s0) / b))
for k in range(nb):
    t = s0 + k * b
    if t >= s1:
        break
    bar, beat = divmod(k, 4)
    root, triad = CHORDS[PROG[bar % 4]]
    in_pause = pause0 <= t < pause1
    # bouncy staccato bass: root on beats, fifth on the "and"
    if not in_pause:
        put(music, bass_note(root, b * 0.35), t, 0.32)
        put(music, bass_note(root + 7, b * 0.25), t + b / 2, 0.22)
    # finger snaps on 2 and 4
    if beat in (1, 3) and not in_pause:
        put(music, snap(), t, 0.5, 0.2)
    # soft strum on beat 1
    if beat == 0:
        for i, m in enumerate(triad):
            put(music, pluck(m, 1.2, 0.3), t + i * 0.018, 0.13, -0.3)
for bar in range(int(np.ceil((s1 - s0) / (4 * b)))):
    for (bt, m, d) in MEL[bar % 4]:
        t = s0 + (bar * 4 + bt) * b
        if t >= s1 - 0.05 or pause0 <= t < pause1:
            continue
        put(music, pluck(m, max(0.25, d * b * 1.2), 0.55), t, 0.33, 0.15)

# --- sad section: 80 BPM, A minor, soft piano (same contour, slowed and minor)
b = 60 / 80
s0, s1 = mus["sad"]
sad_prog = [("Am", 0, 2), ("F", 2, 2), ("Dm", 4, 2), ("E", 6, 1)]
for name, bt, ln in sad_prog:
    root, triad = CHORDS[name]; t = s0 + bt * b
    put(music, piano(root - 12, ln * b + 0.6), t, 0.55)
    for i, m in enumerate(triad):
        put(music, piano(m - 12 if m > 64 else m, ln * b + 0.6), t + 0.03 * i, 0.22)
SAD_MEL = [(0, 76, 1), (1, 72, 1), (2, 77, 1), (3, 76, 1), (4, 74, 1), (5, 77, 1), (6, 68, 1.4)]
for bt, m, d in SAD_MEL:
    put(music, piano(m, d * b + 0.5), s0 + bt * b, 0.5, 0.1)

# --- hype section: 140 BPM
b = 60 / 140
s0, s1 = mus["hype"]
nb = int(round((s1 - s0) / b))
for k in range(nb):
    t = s0 + k * b
    bar, beat = divmod(k, 4)
    root, triad = CHORDS[PROG[bar % 4]]
    put(music, kick(), t, 0.75)
    if beat in (1, 3):
        put(music, clap(), t, 0.6)
    put(music, hat(), t + b / 2, 0.5, 0.3)
    put(music, hat(), t + b / 4, 0.18, -0.3); put(music, hat(), t + 3 * b / 4, 0.18, -0.3)
    for e in (0, 0.5):
        put(music, bass_note(root - 12 if root > 44 else root, b * 0.42, "saw"), t + e * b, 0.3)
    if beat == 0:
        for i, m in enumerate(triad):
            put(music, square_lead(m, b * 1.6), t, 0.08, -0.4 + 0.4 * i)
for bar in range(int(np.ceil(nb / 4))):
    for (bt, m, d) in MEL[bar % 4]:
        t = s0 + (bar * 4 + bt) * b
        if t >= s1 - 0.02:
            continue
        put(music, square_lead(m + 12, d * b + 0.1), t, 0.17, 0.2)
        put(music, pluck(m, d * b + 0.2, 0.7), t, 0.18, -0.2)

# --- ending: back to 115 BPM so the last bar leads straight into the opening bar
b = 60 / 115
s0, s1 = mus["end"]
# G chord pickup run, resolve on C major, then a two-note pickup into bar 1 (which starts on E5)
put(music, kick(), s0, 0.7)
for i, m in enumerate(CHORDS["G"][1]):
    put(music, pluck(m, 1.0, 0.4), s0 + i * 0.018, 0.14)
put(music, bass_note(43, b * 0.8), s0, 0.35)
for i, (m, d) in enumerate([(86, .5), (84, .5), (83, .5), (81, .5)]):
    put(music, pluck(m, d * b * 1.4, 0.6), s0 + i * b * 0.5, 0.35)
tres = s0 + 2 * b
put(music, kick(), tres, 0.8); put(music, clap(), tres, 0.5)
for i, m in enumerate([48, 60, 64, 67, 72]):
    put(music, pluck(m, 2.4, 0.35), tres + i * 0.025, 0.2)
    put(music, piano(m, 2.4), tres, 0.12)
put(music, pluck(84, 2.0, 0.6), tres, 0.4)
put(music, bass_note(36, b * 2), tres, 0.35)
for k in range(1, 4):
    put(music, snap(), tres + k * b, 0.45 if k % 2 else 0.2, 0.2)
put(music, pluck(72, b * 0.6, 0.55), DUR - b, 0.3)
put(music, pluck(74, b * 0.6, 0.55), DUR - b / 2, 0.3)
put(music, bass_note(43, b * 0.3), DUR - b, 0.3)
# the opening bar again past the end, so its downbeat lands in the wrap-around tail
put(music, bass_note(48, (60 / 115) * 0.35), DUR, 0.32)
for i, m in enumerate(CHORDS["C"][1]):
    put(music, pluck(m, 1.2, 0.3), DUR + i * 0.018, 0.13, -0.3)

# --- soft sustained pad under the lazy and ending sections so the music never drops out
def pad(m, d):
    t = tt(d); f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t) + 0.1 * np.sin(2 * np.pi * 3.01 * f * t)
    e = np.minimum(1, t / 0.15) * np.minimum(1, (len(t) - np.arange(len(t))) / (0.25 * SR))
    return s * e


bar = 4 * 60 / 115
s0, s1 = mus["lazy"]
k = 0
while s0 + k * bar < s1:
    t = s0 + k * bar; d = min(bar, s1 - t) + 0.3
    for m in CHORDS[PROG[k % 4]][1]:
        put(music, pad(m - 12, d), t, 0.05)
    k += 1
e0, e1 = mus["end"]
for name, t, d in (("G", e0, 2 * 60 / 115 + 0.2), ("C", e0 + 2 * 60 / 115, e1 - e0 - 2 * 60 / 115 + 0.6)):
    for m in CHORDS[name][1]:
        put(music, pad(m - 12, d), t, 0.05)

# ---------------------------------------------------------------- sound effects
S = TL["sfx"]


def page_flip():
    t = tt(0.22); n = rng.standard_normal(len(t))
    bp = onepole(n, 0.5) - onepole(n, 0.05)
    e = np.exp(-((t - 0.07) / 0.05) ** 2) + 0.4 * np.exp(-t / 0.02)
    return bp * e * 1.6


def trombone():
    out = []
    for m, d, vib in ((58, .17, 0), (57, .17, 0), (56, .17, 0), (55, .45, 1)):
        t = tt(d); f = hz(m) * (1 + vib * 0.03 * np.sin(2 * np.pi * 6 * t)) * (1 - vib * 0.04 * t / d)
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = sum(np.sin(h * ph) / h ** 0.8 for h in range(1, 9))
        wah = 0.35 + 0.65 * np.clip(t / (d * 0.5), 0, 1)
        e = np.minimum(1, t / 0.02) * np.minimum(1, (len(t) - np.arange(len(t))) / (0.03 * SR))
        out.append(onepole(s * wah, 0.18) * e)
    return np.concatenate(out) * 0.5


def slap():
    t = tt(0.25); n = rng.standard_normal(len(t))
    return (onepole(n, 0.6) * np.exp(-t / 0.025) * 1.2 + np.sin(2 * np.pi * 180 * t) * np.exp(-t / 0.03))


def sparkle():
    out = np.zeros(int(1.0 * SR))
    for i, m in enumerate([84, 88, 91, 96, 100, 103]):
        t = tt(0.6); s = (np.sin(2 * np.pi * hz(m) * t) + 0.3 * np.sin(2 * np.pi * hz(m) * 2.76 * t)) * np.exp(-t / 0.18)
        j = int(i * 0.06 * SR); out[j:j + len(s)] += s[: len(out) - j]
    return out * 0.35


def poof():
    t = tt(0.6); n = rng.standard_normal(len(t))
    return sweep(n, 0.35, 0.02) * np.exp(-t / 0.15) * np.minimum(1, t / 0.01) * 1.4


def ding():
    t = tt(1.4); f = hz(93)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) + 0.15 * np.sin(2 * np.pi * f * 5.4 * t)) * np.exp(-t / 0.45) * 0.5


def scratch():
    t = tt(0.38); n = rng.standard_normal(len(t))
    rate = np.abs(np.sin(2 * np.pi * 2.6 * t))            # forward/back hand motion
    s = sweep(n, 0.05, 0.4) * rate
    tone_ = np.sin(2 * np.pi * np.cumsum(300 + 900 * rate) / SR) * 0.4
    return (s + tone_) * np.minimum(1, t / 0.005) * 0.9


def key_click():
    t = tt(0.03); n = rng.standard_normal(len(t))
    return (n - onepole(n, 0.4)) * np.exp(-t / 0.005) + np.sin(2 * np.pi * 2600 * t) * np.exp(-t / 0.004) * 0.3


def chaching():
    out = np.zeros(int(1.1 * SR))
    t = tt(0.12); out[: len(t)] += onepole(rng.standard_normal(len(t)), 0.7) * np.exp(-t / 0.03) * 0.8  # drawer
    for i, m in enumerate([96, 100]):
        t = tt(0.9); s = sum(np.sin(2 * np.pi * hz(m) * h * t) / h for h in (1, 2.4, 3.9)) * np.exp(-t / 0.3)
        j = int((0.12 + i * 0.09) * SR); out[j:j + len(s)] += s[: len(out) - j] * 0.45
    return out


def horn():
    t = tt(0.4); out = 0
    for m in (60, 64, 67, 70):
        f = hz(m); out = out + onepole(2 * ((t * f) % 1) - 1, 0.3)
    return out * np.minimum(1, t / 0.01) * np.exp(-np.clip(t - 0.25, 0, None) / 0.05) * 0.35


def bass_drop():
    t = tt(1.4); f = 30 + 180 * np.exp(-t / 0.12)
    return np.tanh(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.6) * 2.5) * 0.9


for t in S["flip"]:
    put(sfx, page_flip(), t, 0.8, 0.3)
put(sfx, trombone(), S["trombone"], 0.75)
put(sfx, slap(), S["slap"], 0.9)
put(sfx, sparkle(), S["sparkle"], 0.8, -0.2)
put(sfx, poof(), S["poof"], 0.85)
put(sfx, ding(), S["ding"], 0.7)
put(sfx, scratch(), S["scratch"], 0.85)
ty0, ty1 = S["typing"]
k = 0
while ty0 + k * 0.045 < ty1:
    put(sfx, key_click(), ty0 + k * 0.045 + (0.012 if k % 3 == 0 else 0), 0.35 + 0.15 * (k % 2), 0.2 * (1 if k % 2 else -1)); k += 1
put(sfx, chaching(), S["chaching"], 0.75)
put(sfx, horn(), S["horn"], 0.8)
put(sfx, bass_drop(), S["drop"], 0.9)

# ---------------------------------------------------------------- voices + lip-sync envelopes
FPS = 30
nframes = int(DUR * FPS) + 1
mouths = {}
speech = np.zeros(N)
for ln in TL["lines"]:
    x, sr = sf.read(f"{VOICES}/{ln['id']}.wav")
    assert sr == SR, sr
    x = x / (np.abs(x).max() + 1e-9)
    pan = {"cust2": -0.35, "cust3": 0.35, "cust4": 0.15}.get(ln["char"], 0.0)
    g = 0.8 if ln["char"].startswith("cust") and ln["id"] != "l14" else 1.0
    put(vox, x, ln["t"], 0.9 * g, pan)
    i = int(ln["t"] * SR); speech[i:i + len(x)] = 1
    env = mouths.setdefault(ln["char"], [0.0] * nframes)
    hop = SR // FPS
    for f in range(len(x) // hop):
        rms = float(np.sqrt(np.mean(x[f * hop:(f + 1) * hop] ** 2)))
        fi = int(round(ln["t"] * FPS)) + f
        if fi < nframes:
            env[fi] = max(env[fi], min(1.0, rms * 4.0))

# duck the music ~60% under speech: fast attack, smooth release
duck = np.empty(N); acc = 1.0
att = 1 - np.exp(-1 / (0.04 * SR)); rel = 1 - np.exp(-1 / (0.3 * SR))
target = 1 - 0.6 * speech
for i in range(N):
    tg = target[i]; acc += (att if tg < acc else rel) * (tg - acc); duck[i] = acc
music *= duck[:, None]

mix = music * 0.9 + sfx * 0.9 + vox * 1.0
# wrap the tail past the end onto the start so the loop is seamless
L = int(DUR * SR)
mix[: N - L] += mix[L:N]
mix = mix[:L]
mix = np.tanh(mix / (np.abs(mix).max() + 1e-9) * 1.3) / np.tanh(1.3) * 0.92
sf.write(OUT, mix, SR)

# quantise envelopes to digits 0–9 for compact embedding
json.dump({c: "".join(str(min(9, int(v * 9.99))) for v in e) for c, e in mouths.items()}, open(MOUTHS, "w"))
print("ok", round(L / SR, 2), "s")
