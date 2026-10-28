# Generates every dialogue clip with Kokoro (offline) and shapes each character with rubberband.
import json, subprocess, sys, os
import numpy as np, soundfile as sf
HF = sys.argv[1]; OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
# id: (voice, kokoro speed, pitch semitones, text)
V = {
 "l00": ("am_michael", 0.95, -0.5, "I'll start my startup... when the time is perfect."),
 "l01": ("am_michael", 1.0, -0.5, "Next Monday. Definitely."),
 "l02": ("am_michael", 1.1, 0.5, "Sir! Fund my idea!"),
 "l03": ("am_adam", 0.85, -5, "What's the idea?"),
 "l04": ("am_michael", 0.9, -0.5, "...I'm still thinking."),
 "l05": ("bm_george", 0.95, -2, "Have you talked to any customers?"),
 "l06": ("am_michael", 1.05, 0, "I told my mom. She loves it."),
 "l07": ("af_sky", 1.35, 6, "I'm here! I'll stay forever!"),
 "l08": ("am_michael", 0.9, -0.5, "...She lied."),
 "l09": ("am_michael", 0.85, -1, "Nobody's coming, huh?"),
 "l10": ("am_michael", 1.55, 10, "Bro, I'm two millimeters tall and I'm building."),
 "l11": ("am_michael", 0.85, -1, "...Respect."),
 "l12": ("am_michael", 1.15, 1, "Okay. Let's go."),
 "l14": ("am_adam", 1.25, 2, "Take my money!"),
 "l15a": ("af_heart", 1.3, 3, "Me too! Me too!"),
 "l15b": ("bm_george", 1.3, 1, "Me too! Me too!"),
 "l15c": ("af_nova", 1.4, 7, "Me too!"),
 "l16": ("am_adam", 1.1, -5, "Wait! Can I invest now?"),
 "l17": ("am_michael", 1.1, 1, "Sorry. We're busy building."),
 "l19": ("am_michael", 1.45, 10, "Told you."),
}
info = {}
for k, (voice, spd, st, text) in V.items():
    raw = f"{OUT}/raw_{k}.wav"
    subprocess.run(["npx", "hyperframes", "tts", text, "-v", voice, "-s", str(spd), "-o", raw, "--json"],
                   cwd=HF, check=True, capture_output=True)
    shaped = f"{OUT}/sh_{k}.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af",
                    f"rubberband=pitch={2 ** (st / 12):.5f},aresample=44100", "-ac", "1", shaped], check=True)
    x, sr = sf.read(shaped)
    a = np.abs(x); th = 0.02 * a.max(); idx = np.where(a > th)[0]
    i0 = max(0, idx[0] - int(0.02 * sr)); i1 = min(len(x), idx[-1] + int(0.06 * sr))
    y = x[i0:i1]; fade = int(0.01 * sr); y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
    sf.write(f"{OUT}/{k}.wav", y, sr)
    info[k] = {"dur": round(len(y) / sr, 3), "text": text}
    print(k, info[k]["dur"])
json.dump(info, open(f"{OUT}/voices.json", "w"), indent=1)
