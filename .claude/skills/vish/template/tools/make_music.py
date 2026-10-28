"""Turns the MusicGen seed clip into a music bed that covers the whole film.

Usage: python3 tools/make_music.py <seed.wav> <duration_s> assets/audio/music.wav

The seed comes from tools/gen_music.py (facebook/musicgen-small, run locally; original
audio). This script finds the tempo from the onset envelope, skips the seed's first bar,
loops whole bars with equal-power crossfades, then fades in briefly and out over the
last bars. Output: stereo 48 kHz, peak about -3 dBFS (the mix applies the bed volume).
"""
import sys
import numpy as np, soundfile as sf

seed, sr = sf.read(sys.argv[1]); dur = float(sys.argv[2]); out = sys.argv[3]
if seed.ndim > 1:
    seed = seed.mean(1)

# ---- tempo from spectral-flux autocorrelation
hop = 512; n = (len(seed) - 2048) // hop
frames = np.stack([np.abs(np.fft.rfft(seed[i * hop:i * hop + 2048] * np.hanning(2048))) for i in range(n)])
flux = np.maximum(0, np.diff(frames, axis=0)).sum(1); flux = (flux - flux.mean()) / (flux.std() + 1e-9)
ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
lag_s = np.arange(len(ac)) * hop / sr
band = (lag_s > 0.42) & (lag_s < 0.75)
beat = lag_s[band][np.argmax(ac[band])]
bar = 4 * beat
print(f"tempo ≈ {60 / beat:.1f} BPM, bar {bar:.3f}s")

# ---- loop whole bars from the second bar onward
start = int(bar * sr)
nbars = int((len(seed) / sr - bar - 0.6) // bar)
loop = seed[start:start + int(nbars * bar * sr)]
xf = int(0.35 * sr)
target = int(dur * sr)
out_buf = loop.copy()
while len(out_buf) < target + xf:
    a = out_buf[-xf:]; b = loop[:xf]
    t = np.linspace(0, np.pi / 2, xf)
    out_buf = np.concatenate([out_buf[:-xf], a * np.cos(t) + b * np.sin(t), loop[xf:]])
out_buf = out_buf[:target]

# ---- fades: short in, ~2 bars out ending on the film's last frame
fi = int(0.25 * sr); fo = int(min(2 * bar, 3.0) * sr)
out_buf[:fi] *= np.linspace(0, 1, fi)
out_buf[-fo:] *= np.cos(np.linspace(0, np.pi / 2, fo)) ** 2

# ---- gentle high-pass (remove sub rumble a phone cannot play) and resample to 48 kHz
a = np.exp(-2 * np.pi * 60 / sr); y = np.empty_like(out_buf); px = py = 0.0
for i, x in enumerate(out_buf):
    py = a * (py + x - px); px = x; y[i] = py
idx = np.arange(int(len(y) * 48000 / sr)) * sr / 48000
y = np.interp(idx, np.arange(len(y)), y)
y = y / (np.abs(y).max() + 1e-9) * 0.7
sf.write(out, np.stack([y, y], 1), 48000)
print("ok", round(len(y) / 48000, 2), "s")
