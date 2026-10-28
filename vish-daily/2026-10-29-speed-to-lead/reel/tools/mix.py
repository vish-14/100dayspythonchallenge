"""Writes the ducked music bed (assets/audio/music_bed.wav) from the music and the voiceover.

Usage: python3 tools/mix.py
The bed dips by config.audio.duck_db while the voice is speaking (60 ms attack, 350 ms
release) so the music plays throughout but never competes with the dialogue.
"""
import json, os
import numpy as np, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *p: os.path.join(ROOT, *p)
cfg = json.load(open(P("project.config.json")))
A = cfg["audio"]
music, sr = sf.read(P(cfg["assets"]["music_raw"]))
voice, vsr = sf.read(P(cfg["assets"]["voiceover"]))
if voice.ndim > 1:
    voice = voice.mean(1)
# speech mask at the music's sample rate, from 20 ms voice energy frames
hop = int(0.02 * vsr)
env = np.array([np.sqrt(np.mean(voice[i:i + hop] ** 2)) for i in range(0, len(voice), hop)])
speech = env > 0.02 * env.max() * 3
# bridge tiny gaps between words so the bed does not pump
k = int(0.25 / 0.02)
for i in range(len(speech)):
    if speech[i]:
        j = i + 1
        while j < min(len(speech), i + k) and not speech[j]:
            j += 1
        if j < len(speech) and speech[j] and j - i < k:
            speech[i:j] = True
t_music = np.arange(len(music)) / sr
mask = np.interp(t_music, np.arange(len(speech)) * 0.02, speech.astype(float), right=0)
target = 10 ** (A["music_base_db"] / 20) / np.abs(music).max() * np.where(mask > 0.5, 10 ** (A["duck_db"] / 20), 1.0)
att = 1 - np.exp(-1 / (0.06 * sr)); rel = 1 - np.exp(-1 / (0.35 * sr))
g = np.empty_like(target); acc = target[0]
for i, tg in enumerate(target):
    acc += (att if tg < acc else rel) * (tg - acc); g[i] = acc
bed = music * g[:, None]
sf.write(P(cfg["assets"]["music_bed"]), bed, sr)
print("music bed:", round(len(bed) / sr, 2), "s; ducked share", round(float((mask > 0.5).mean()), 2))
